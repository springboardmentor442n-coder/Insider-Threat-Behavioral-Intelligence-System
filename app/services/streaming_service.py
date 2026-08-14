"""
Real-Time Stateful Stream Prediction Engine
===========================================
Tracks rolling sliding-window features in Redis and feeds them to the Classifier.
This avoids high-latency SQL database queries during streaming replays.
"""
import redis
import json
import numpy as np
from datetime import datetime, timezone
from typing import Dict, Optional
from sqlalchemy.orm import Session
from loguru import logger

from app.core.config import settings
from app.models import Employee, ActivityLog, RiskScore, RiskCategory, Anomaly, AnomalyType, Alert, AlertSeverity, AlertStatus
from app.ml.feature_engineering import encode_location, encode_department, encode_role, FEATURE_NAMES, N_FEATURES
from app.ml import inference as inf_service
from app.services import ml_service

# Initialize Redis client with fallback to in-memory dictionary
class SafeRedisWrapper:
    def __init__(self):
        self.mem_hash = {}
        self.mem_set = {}
        try:
            self.redis = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
            self.redis.ping()
            self.use_redis = True
        except Exception as e:
            logger.warning(f"Redis unavailable ({e}); using stateful in-memory cache for live streaming.")
            self.use_redis = False

    def exists(self, name: str) -> bool:
        if self.use_redis:
            try: return bool(self.redis.exists(name))
            except Exception: pass
        return name in self.mem_hash

    def hgetall(self, name: str) -> Dict[str, str]:
        if self.use_redis:
            try: return self.redis.hgetall(name)
            except Exception: pass
        return self.mem_hash.get(name, {})

    def hmset(self, name: str, mapping: dict) -> bool:
        if self.use_redis:
            try: return self.redis.hmset(name, mapping)
            except Exception: pass
        if name not in self.mem_hash: self.mem_hash[name] = {}
        self.mem_hash[name].update({k: str(v) for k, v in mapping.items()})
        return True

    def hincrby(self, name: str, key: str, amount: int = 1) -> int:
        if self.use_redis:
            try: return self.redis.hincrby(name, key, amount)
            except Exception: pass
        if name not in self.mem_hash: self.mem_hash[name] = {}
        curr = int(self.mem_hash[name].get(key, 0)) + amount
        self.mem_hash[name][key] = str(curr)
        return curr

    def hincrbyfloat(self, name: str, key: str, amount: float = 1.0) -> float:
        if self.use_redis:
            try: return self.redis.hincrbyfloat(name, key, amount)
            except Exception: pass
        if name not in self.mem_hash: self.mem_hash[name] = {}
        curr = float(self.mem_hash[name].get(key, 0.0)) + amount
        self.mem_hash[name][key] = str(curr)
        return curr

    def sadd(self, name: str, value: str) -> int:
        if self.use_redis:
            try: return self.redis.sadd(name, value)
            except Exception: pass
        if name not in self.mem_set: self.mem_set[name] = set()
        self.mem_set[name].add(value)
        return len(self.mem_set[name])

    def scard(self, name: str) -> int:
        if self.use_redis:
            try: return self.redis.scard(name)
            except Exception: pass
        return len(self.mem_set.get(name, set()))

    def delete(self, name: str) -> int:
        if self.use_redis:
            try: return self.redis.delete(name)
            except Exception: pass
        self.mem_hash.pop(name, None)
        self.mem_set.pop(name, None)
        return 1

    def expire(self, name: str, time: int) -> bool:
        if self.use_redis:
            try: return self.redis.expire(name, time)
            except Exception: pass
        return True

r_client = SafeRedisWrapper()

class StreamingRiskEngine:
    @staticmethod
    def get_redis_key(employee_id: int) -> str:
        return f"streaming:features:{employee_id}"

    @staticmethod
    def get_devices_key(employee_id: int) -> str:
        return f"streaming:devices:{employee_id}"

    @classmethod
    def initialize_profile(cls, db: Session, employee_id: int, force_rebuild: bool = False) -> Dict:
        """
        Loads employee metadata (location, dept, role) and bootstraps
        historical counters from DB logs over the last 30 days.
        """
        redis_key = cls.get_redis_key(employee_id)
        
        # Check if already initialized
        if not force_rebuild and r_client.exists(redis_key):
            try:
                data = r_client.hgetall(redis_key)
                if "location" in data and "department" in data:
                    return data
            except Exception as e:
                logger.warning(f"Error reading Redis profile, rebuilding: {e}")

        emp = db.query(Employee).filter(Employee.id == employee_id).first()
        if not emp:
            raise ValueError(f"Employee {employee_id} not found in database")

        dept_code = emp.department.code if emp.department else ""
        val_location = encode_location(emp.location)
        val_department = encode_department(dept_code)
        val_role = encode_role(emp.designation)

        # Build initial structure
        profile = {
            "location": str(val_location),
            "department": str(val_department),
            "employee_role": str(val_role),
            "total_login_hour": "0.0",
            "login_count": "0",
            "failed_logins": "0",
            "vpn_usage": "0",
            "usb_usage": "0",
            "file_downloads": "0",
            "file_uploads": "0",
            "email_count": "0",
            "cloud_uploads": "0",
            "outside_hours_count": "0",
            "total_activities_count": "0",
            "privilege_escalation": "0",
            "database_access": "0",
            "website_visits": "0",
            "external_storage_usage": "0",
            "total_session_duration": "0.0",
            "session_count": "0",
            "total_bytes_transferred": "0"
        }

        # Clear device sets
        r_client.delete(cls.get_devices_key(employee_id))

        # Bootstrap from last 30 days of DB logs
        from datetime import timedelta
        since = datetime.now(timezone.utc) - timedelta(days=30)
        logs = db.query(ActivityLog).filter(
            ActivityLog.employee_id == employee_id,
            ActivityLog.timestamp >= since
        ).all()

        cloud_resources = ["drive.google.com", "dropbox.com", "s3.amazonaws.com", "onedrive.live.com", "box.com", "cloud"]
        db_keywords = ["select", "insert", "update", "delete", "query", "database", "prod_db", "table"]
        usb_resource = ["usb", "external", "drive"]

        total_login_hour = 0.0
        login_count = 0
        failed_logins = 0
        vpn_usage = 0
        usb_usage = 0
        file_downloads = 0
        file_uploads = 0
        email_count = 0
        cloud_uploads = 0
        outside_hours_count = 0
        total_activities_count = len(logs)
        privilege_escalation = 0
        database_access = 0
        website_visits = 0
        external_storage_usage = 0
        total_session_duration = 0.0
        session_count = 0
        total_bytes_transferred = 0

        for log in logs:
            res_lower = (log.resource or "").lower()
            act_val = log.activity_type.value

            if log.is_outside_hours:
                outside_hours_count += 1
            
            if log.device_id:
                r_client.sadd(cls.get_devices_key(employee_id), log.device_id)

            if act_val == "login":
                login_count += 1
                total_login_hour += log.timestamp.hour
            elif act_val == "failed_login" or (act_val == "login" and log.is_suspicious):
                failed_logins += 1
            elif act_val == "remote_access":
                vpn_usage += 1
            elif act_val == "usb_connect":
                usb_usage += 1
                if any(x in res_lower for x in usb_resource):
                    external_storage_usage += 1
            elif act_val == "file_download":
                file_downloads += 1
            elif act_val == "file_upload":
                file_uploads += 1
                if any(x in res_lower for x in cloud_resources):
                    cloud_uploads += 1
                if any(x in res_lower for x in usb_resource):
                    external_storage_usage += 1
            elif act_val in ["email_send", "email_receive"]:
                email_count += 1
            elif act_val == "privilege_change":
                privilege_escalation += 1
            elif act_val == "database_query":
                database_access += 1
            elif act_val == "application_access":
                if any(x in res_lower for x in db_keywords):
                    database_access += 1
            elif act_val == "network_access":
                website_visits += 1

            if log.duration_seconds:
                session_count += 1
                total_session_duration += log.duration_seconds
                
            if log.bytes_transferred:
                total_bytes_transferred += log.bytes_transferred

        # Save bootstrap states
        profile.update({
            "total_login_hour": str(total_login_hour),
            "login_count": str(login_count),
            "failed_logins": str(failed_logins),
            "vpn_usage": str(vpn_usage),
            "usb_usage": str(usb_usage),
            "file_downloads": str(file_downloads),
            "file_uploads": str(file_uploads),
            "email_count": str(email_count),
            "cloud_uploads": str(cloud_uploads),
            "outside_hours_count": str(outside_hours_count),
            "total_activities_count": str(total_activities_count),
            "privilege_escalation": str(privilege_escalation),
            "database_access": str(database_access),
            "website_visits": str(website_visits),
            "external_storage_usage": str(external_storage_usage),
            "total_session_duration": str(total_session_duration),
            "session_count": str(session_count),
            "total_bytes_transferred": str(total_bytes_transferred),
        })

        r_client.hmset(redis_key, profile)
        # Expire profile after 7 days if inactive
        r_client.expire(redis_key, 604800)
        
        logger.info(f"✅ Initialized and bootstrapped Redis streaming profile for employee {emp.full_name} ({emp.employee_id})")
        return profile

    @classmethod
    def process_stream_event(cls, db: Session, employee_id: int, activity_type: str, details: dict) -> np.ndarray:
        """
        Increments/updates metrics inside the Redis hash based on the incoming event details,
        then returns the fully constructed 20-dimensional feature vector.
        """
        redis_key = cls.get_redis_key(employee_id)
        
        # Ensure profile is initialized
        if not r_client.exists(redis_key):
            cls.initialize_profile(db, employee_id)

        # Standard filters
        cloud_resources = ["drive.google.com", "dropbox.com", "s3.amazonaws.com", "onedrive.live.com", "box.com", "cloud"]
        db_keywords = ["select", "insert", "update", "delete", "query", "database", "prod_db", "table"]
        usb_resource = ["usb", "external", "drive"]

        # Parse event characteristics
        resource = str(details.get("resource", "")).lower()
        bytes_transferred = int(details.get("bytes_transferred", 0) or 0)
        is_outside_hours = bool(details.get("is_outside_hours", False))
        is_suspicious = bool(details.get("is_suspicious", False))
        duration = float(details.get("duration_seconds", 0.0) or 0.0)
        device_id = details.get("device_id")
        timestamp_str = details.get("timestamp")
        
        if timestamp_str:
            try:
                # Expecting isoformat
                dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                event_hour = dt.hour
            except Exception:
                event_hour = datetime.now(timezone.utc).hour
        else:
            event_hour = datetime.now(timezone.utc).hour

        # Hashed increments
        updates = {}
        
        # Track outside hours
        r_client.hincrby(redis_key, "total_activities_count", 1)
        if is_outside_hours:
            r_client.hincrby(redis_key, "outside_hours_count", 1)

        # Register device changes
        if device_id:
            r_client.sadd(cls.get_devices_key(employee_id), device_id)

        # Core logic mapping
        if activity_type == "login":
            r_client.hincrby(redis_key, "login_count", 1)
            r_client.hincrbyfloat(redis_key, "total_login_hour", event_hour)
        elif activity_type == "failed_login" or (activity_type == "login" and is_suspicious):
            r_client.hincrby(redis_key, "failed_logins", 1)
        elif activity_type == "remote_access":
            r_client.hincrby(redis_key, "vpn_usage", 1)
        elif activity_type == "usb_connect":
            r_client.hincrby(redis_key, "usb_usage", 1)
            if any(x in resource for x in usb_resource):
                r_client.hincrby(redis_key, "external_storage_usage", 1)
        elif activity_type == "file_download":
            r_client.hincrby(redis_key, "file_downloads", 1)
        elif activity_type == "file_upload":
            r_client.hincrby(redis_key, "file_uploads", 1)
            if any(x in resource for x in cloud_resources):
                r_client.hincrby(redis_key, "cloud_uploads", 1)
            if any(x in resource for x in usb_resource):
                r_client.hincrby(redis_key, "external_storage_usage", 1)
        elif activity_type in ["email_send", "email_receive"]:
            r_client.hincrby(redis_key, "email_count", 1)
        elif activity_type == "privilege_change":
            r_client.hincrby(redis_key, "privilege_escalation", 1)
        elif activity_type == "database_query":
            r_client.hincrby(redis_key, "database_access", 1)
        elif activity_type == "application_access":
            if any(x in resource for x in db_keywords):
                r_client.hincrby(redis_key, "database_access", 1)
        elif activity_type == "network_access":
            r_client.hincrby(redis_key, "website_visits", 1)

        if duration > 0:
            r_client.hincrby(redis_key, "session_count", 1)
            r_client.hincrbyfloat(redis_key, "total_session_duration", duration)

        if bytes_transferred > 0:
            r_client.hincrby(redis_key, "total_bytes_transferred", bytes_transferred)

        # Retrieve full hash to calculate averages/fractions
        data = r_client.hgetall(redis_key)

        login_count = int(data.get("login_count", 0))
        total_login_hour = float(data.get("total_login_hour", 0.0))
        login_time = total_login_hour / login_count if login_count > 0 else 9.0

        outside_hours = int(data.get("outside_hours_count", 0))
        total_activities = int(data.get("total_activities_count", 0))
        working_hours = outside_hours / total_activities if total_activities > 0 else 0.0

        device_changes = float(r_client.scard(cls.get_devices_key(employee_id)) or 1.0)

        session_count = int(data.get("session_count", 0))
        total_duration = float(data.get("total_session_duration", 0.0))
        session_duration = total_duration / session_count if session_count > 0 else 0.0

        # Dynamic frequency over 30 days
        login_frequency = login_count / 30.0

        # Data transfer size in MB
        total_bytes = int(data.get("total_bytes_transferred", 0))
        data_transfer_size = total_bytes / 1048576.0

        # Construct vector order matching FEATURE_NAMES
        vector = np.array([
            login_time,
            float(data.get("failed_logins", 0)),
            float(data.get("vpn_usage", 0)),
            float(data.get("usb_usage", 0)),
            float(data.get("file_downloads", 0)),
            float(data.get("file_uploads", 0)),
            float(data.get("email_count", 0)),
            float(data.get("cloud_uploads", 0)),
            device_changes,
            working_hours,
            float(data.get("privilege_escalation", 0)),
            float(data.get("database_access", 0)),
            float(data.get("website_visits", 0)),
            float(data.get("external_storage_usage", 0)),
            float(data.get("location", 0.0)),
            float(data.get("department", 0.0)),
            float(data.get("employee_role", 0.0)),
            session_duration,
            login_frequency,
            data_transfer_size
        ], dtype=np.float32)

        return vector

    @classmethod
    def predict_stream_event(cls, db: Session, employee_id: int, activity_type: str, details: dict) -> Dict:
        """
        Updates the feature cache state in Redis, runs standard classifier prediction,
        saves the RiskScore to MySQL, and triggers real-time WebSocket alerts if critical.
        """
        # 1. Update state and retrieve feature vector
        vector = cls.process_stream_event(db, employee_id, activity_type, details)
        
        # 2. Run model predictions using our updated RandomForest inference system
        pred = inf_service.predict_threat(vector)
        pred["employee_id"] = employee_id
        
        # Format feature values in prediction output
        pred["feature_values"] = {
            name: round(float(val), 4)
            for name, val in zip(FEATURE_NAMES, vector)
        }

        # 3. Compute database representation
        total = pred["threat_score"]
        cat_map = {
            "Normal": RiskCategory.low,
            "Low Risk": RiskCategory.low,
            "Medium Risk": RiskCategory.medium,
            "High Risk": RiskCategory.high,
            "Critical Risk": RiskCategory.critical
        }
        category = cat_map.get(pred["threat_level"], RiskCategory.low)

        # 4. Read previous score for trend
        prev = (db.query(RiskScore)
                .filter(RiskScore.employee_id == employee_id)
                .order_by(RiskScore.score_date.desc())
                .first())
        if prev:
            delta = total - prev.total_score
            trend = "increasing" if delta > 0.1 else ("decreasing" if delta < -0.1 else "stable")
        else:
            trend = "increasing" if total >= 50.0 else "stable"

        explanation = {
            "top_factors": [
                {"factor": tf["feature"].replace("_", " ").title(), "score": round(tf["value"], 2), "weight": f"{tf['contribution']*100:.1f}%"}
                for tf in pred["top_features"]
            ],
            "shap_explanation": pred["shap_explanation"],
            "recommended_action": pred["recommended_action"],
            "confidence": pred["confidence"]
        }

        # 5. Insert new RiskScore to database
        rs = RiskScore(
            employee_id=employee_id,
            behavioral_anomaly_score=pred["isolation_forest_score"],
            privilege_misuse_score=float(pred["feature_values"].get("privilege_escalation", 0.0) * 20),
            data_access_violation_score=float(pred["feature_values"].get("data_transfer_size", 0.0) / 10),
            access_pattern_score=float(pred["feature_values"].get("usb_usage", 0.0) * 15),
            historical_security_score=pred["confidence"],
            total_score=total,
            risk_category=category,
            trend=trend,
            explanation=explanation,
            isolation_forest_score=pred["isolation_forest_score"],
            xgboost_probability=pred["confidence"],
            score_date=datetime.now(timezone.utc)
        )
        db.add(rs)
        db.commit()
        db.refresh(rs)

        # 6. Auto-generate alerts if risk level is critical/high
        if rs.risk_category in (RiskCategory.high, RiskCategory.critical):
            ml_service._auto_create_alert(db, employee_id, rs)

        return {
            "prediction": pred,
            "risk_score_id": rs.id,
            "total_score": total,
            "risk_category": category.value,
            "trend": trend
        }
