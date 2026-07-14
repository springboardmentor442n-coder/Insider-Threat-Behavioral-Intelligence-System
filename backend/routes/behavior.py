from fastapi import APIRouter

router = APIRouter()


@router.get("/behavior-profile")
def get_behavior_profiles():
    return [
        {
            "employee_id": "EMP001",
            "name": "Alice Johnson",
            "department": "HR",
            "avg_login": 165,
            "avg_devices": 3,
            "avg_hour": 9,
            "weekend_activity": "Low",
            "behavior_score": 92,
            "status": "Normal"
        },
        {
            "employee_id": "EMP002",
            "name": "Bob Smith",
            "department": "Finance",
            "avg_login": 280,
            "avg_devices": 6,
            "avg_hour": 23,
            "weekend_activity": "High",
            "behavior_score": 45,
            "status": "Suspicious"
        },
        {
            "employee_id": "EMP003",
            "name": "Charlie Brown",
            "department": "IT",
            "avg_login": 190,
            "avg_devices": 4,
            "avg_hour": 10,
            "weekend_activity": "Medium",
            "behavior_score": 78,
            "status": "Monitor"
        }
    ]

