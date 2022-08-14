
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///inventory.sqlite3'

db = SQLAlchemy(app)


#Backref info from https://docs.sqlalchemy.org/en/14/orm/backref.html
#https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/

class Employee(db.Model):
    __tablename__ = "employee"
    emp_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    pps_number = db.Column(db.String(9), nullable=False)
    dob = db.Column(db.String, nullable=False)
    hire_date = db.Column(db.String, nullable=False)
    title = db.relationship("EmployeeTitle", backref="employee_job_title", lazy="joined")

    def __init__(self, first_name, last_name, pps_number, dob, hire_date):
        self.first_name = first_name
        self.last_name = last_name
        self.pps_number = pps_number
        self.dob = dob
        self.hire_date = hire_date

    #need username & password?

class Department(db.Model):
    department_num = db.Column(db.Integer, autoincrement=True, primary_key=True)
    department_name = db.Column(db.String(50), nullable=False)
    department_phone = db.Column(db.String(20), nullable=False)
    title = db.relationship("Title", backref="jobtitle", lazy="joined")

    def __init__(self, department_name, department_phone):
        self.department_name = department_name
        self.department_phone = department_phone

class Title(db.Model):
    job_title = db.Column(db.String(50), primary_key=True)
    department_num = db.Column(db.Integer, db.ForeignKey(Department.department_num), nullable=False)
    access_level = db.Column(db.Integer, nullable=False)
    department = db.relationship("Department", back_populates ="title")

    def __init__ (self, job_title, department_num, access_level):
        self.job_title = job_title
        self.department_num = department_num
        self.access_level = access_level

   

class EmployeeTitle(db.Model):

    __tablename__ = "employee_title"

    emp_title_id  = db.Column(db.Integer, db.ForeignKey(Employee.emp_id), primary_key=True)
    emp_job_title = db.Column(db.String(50), db.ForeignKey(Title.job_title), primary_key=True)
    start_date = db.Column(db.String, nullable=False)
    end_date = db.Column(db.String, nullable=True)
    employee = db.relationship("Employee", back_populates = "title")


    def __init__(self, emp_title_id, emp_job_title, start_date, end_date):
        self.emp_title_id = emp_title_id
        self.emp_job_title = emp_job_title
        self.start_date = start_date
        self.end_date = end_date

    #should this be Model or Table

class Category(db.Model):
    category_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def __init__(self, name, description):
        self.name = name
        self.description = description

class Supplier(db.Model):
    supplier_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    #ADDRESS?!?!!? - sep table for this? connect to emp as well?
    email = db.Column(db.String(50), nullable=False)
    comments = db.Column(db.String(200), nullable=True)

    def __init__(self, supplier_id, name, phone, email, comments):
        self.name = name
        self.phone = phone
        self.email = email
        self.comments = comments

class Item(db.Model):
    item_id  = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name  = db.Column(db.String(50), nullable=False) #, unique=True)
    description = db.Column(db.Text, nullable=True)
    unit_cost  = db.Column(db.Numeric, nullable=False)
    sale_price  = db.Column(db.Numeric, nullable=False)
    units_in_stock  = db.Column(db.Integer, nullable=False)
    expiration_date  = db.Column(db.String, nullable=True) #put some kind of batch table to handle this?
    supplier_id = db.Column(db.Integer, nullable=False)
   # supplier_id = db.Column(db.Integer, db.ForeignKey(Supplier.supplier_id), nullable=False)
   # category_id = db.Column(db.Integer, db.ForeignKey(Category.category_id), nullable=False)
    category_id = db.Column(db.Integer, nullable=False)

    def __init__(self, name, description, unit_cost, sale_price, units_in_stock, expiration_date, supplier_id, category_id):
        self.name = name
        self.description = description
        self.unit_cost = unit_cost
        self.sale_price = sale_price
        self.units_in_stock = units_in_stock
        self.expiration_date = expiration_date
        self.supplier_id = supplier_id
        self.category_id = category_id
