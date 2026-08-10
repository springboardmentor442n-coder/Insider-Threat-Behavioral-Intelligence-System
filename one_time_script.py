from run import app
from app.extensions import db

with app.app_context():
    print(db.engine)
    print(db.inspect(db.engine).get_table_names())