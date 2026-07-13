from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class PredictionHistory(db.Model):

    __tablename__ = "prediction_history"

    id = db.Column(db.Integer, primary_key=True)

    employee = db.Column(db.String(50))

    risk_score = db.Column(db.Float)

    prediction = db.Column(db.String(20))

    anomaly = db.Column(db.String(20))

    date = db.Column(db.String(50))