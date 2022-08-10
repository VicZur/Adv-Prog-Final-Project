from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite://students.sqlite3'

db = SQLAlchemy(app)

class User(db.Model):
    emp_id = db.Column('emp_id', db.Integer, primary_key=True)
    emp_first_name = db.Column(db.String(50), nullable=False)
    emp_last_name = db.Column(db.String(50), nullable=False)
    emp_pps_number = db.Column(db.String(9), nullable=False)
    emp_dob = db.Column(db.Date, nullable=False)
    emp_hire_date = db.Column(db.Date, nullable=False)

