from config import engine, Base
from models import User, Employee, Prediction

Base.metadata.create_all(bind=engine)