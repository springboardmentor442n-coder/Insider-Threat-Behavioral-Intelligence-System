from datetime import datetime

from flask_login import UserMixin

from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(50),
        default="analyst",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class Employee(db.Model):
    __tablename__ = "employees"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    employee_id = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    department = db.Column(
        db.String(100)
    )

    role = db.Column(
        db.String(100)
    )

    business_unit = db.Column(
        db.String(100)
    )

    login_count = db.Column(db.Float, default=0)
    logoff_count = db.Column(db.Float, default=0)

    night_login_count = db.Column(db.Float, default=0)
    weekend_login_count = db.Column(db.Float, default=0)

    unique_pc_count = db.Column(db.Float, default=0)

    night_login_ratio = db.Column(db.Float, default=0)
    weekend_login_ratio = db.Column(db.Float, default=0)

    pc_switching_frequency = db.Column(
        db.Float,
        default=0
    )

    usb_connect_count = db.Column(db.Float, default=0)
    usb_disconnect_count = db.Column(db.Float, default=0)
    usb_total_activity = db.Column(db.Float, default=0)
    usb_connect_ratio = db.Column(db.Float, default=0)

    file_copy_count = db.Column(db.Float, default=0)
    avg_daily_file_copy = db.Column(db.Float, default=0)
    max_daily_file_copy = db.Column(db.Float, default=0)

    email_sent_count = db.Column(db.Float, default=0)
    external_email_count = db.Column(db.Float, default=0)

    avg_attachment_count = db.Column(
        db.Float,
        default=0
    )

    avg_email_size = db.Column(
        db.Float,
        default=0
    )

    external_email_ratio = db.Column(
        db.Float,
        default=0
    )

    website_visit_count = db.Column(
        db.Float,
        default=0
    )

    unique_domain_count = db.Column(
        db.Float,
        default=0
    )

    avg_daily_web_activity = db.Column(
        db.Float,
        default=0
    )

    # Personality features
    O = db.Column(db.Float, default=0)
    C = db.Column(db.Float, default=0)
    E = db.Column(db.Float, default=0)
    A = db.Column(db.Float, default=0)
    N = db.Column(db.Float, default=0)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    predictions = db.relationship(
        "Prediction",
        backref="employee",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Prediction(db.Model):
    __tablename__ = "predictions"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    employee_id = db.Column(
        db.Integer,
        db.ForeignKey("employees.id"),
        nullable=False
    )

    prediction = db.Column(
        db.String(50),
        nullable=False
    )

    status = db.Column(
        db.String(50)
    )

    threat_probability = db.Column(
        db.Float
    )

    normal_probability = db.Column(
        db.Float
    )

    ml_risk_level = db.Column(
        db.String(50)
    )

    behavioral_risk_score = db.Column(
        db.Float
    )

    overall_risk_level = db.Column(
        db.String(50)
    )

    recommendation = db.Column(
        db.Text
    )

    model_name = db.Column(
        db.String(100),
        default="Random Forest"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    risk_indicators = db.relationship(
        "RiskIndicator",
        backref="prediction",
        lazy=True,
        cascade="all, delete-orphan"
    )


class RiskIndicator(db.Model):
    __tablename__ = "risk_indicators"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    prediction_id = db.Column(
        db.Integer,
        db.ForeignKey("predictions.id"),
        nullable=False
    )

    feature = db.Column(
        db.String(100),
        nullable=False
    )

    value = db.Column(
        db.Float
    )

    points = db.Column(
        db.Float
    )

    severity = db.Column(
        db.String(50)
    )

    reason = db.Column(
        db.Text
    )