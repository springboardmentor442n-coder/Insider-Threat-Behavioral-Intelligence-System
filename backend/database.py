from backend.config import engine, Base
from backend.models import (
    User,
    Employee,
    Prediction,
    BehaviorFeature,
    PipelineRun,
    Alert,
)

Base.metadata.create_all(bind=engine)