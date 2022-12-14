
from flask import Flask
from flask_sqlalchemy import SQLAlchemy 


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///inventory.sqlite3'

db = SQLAlchemy(app)


#Backref info from https://docs.sqlalchemy.org/en/14/orm/backref.html
#https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/


#create employee table as per requirements document
class Employee(db.Model):
    __tablename__ = "employee"
    emp_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    pps_number = db.Column(db.String(9), nullable=False)    
    dob = db.Column(db.String, nullable=False)
    hire_date = db.Column(db.String, nullable=False)
    title = db.relationship("EmployeeTitle", uselist=False, cascade="all,delete", backref="employee_job_title", lazy="joined")


    def __init__(self, first_name, last_name, pps_number, dob, hire_date, title):
        self.first_name = first_name
        self.last_name = last_name
        self.pps_number = pps_number
        self.dob = dob
        self.hire_date = hire_date

    #ensure employee can be used with flask login, "user" table requires the following
    #https://flask-login.readthedocs.io/en/latest/

    def is_authenticated(self):
        return True #all users are authenticated

    def is_active(self):
        return True #all users are active

    def is_anonymous(self):
        return False #anonymous users are not able to access system

    def get_id(self):
        return str(self.emp_id)


#create title table
class Title(db.Model):

    job_title = db.Column(db.String(50), primary_key=True)
    department = db.Column(db.String(50), nullable=False)
    access_level = db.Column(db.Integer, nullable=False)
    emp_title = db.relationship("EmployeeTitle", backref="emp_title", lazy="joined")

    def __init__ (self, job_title, department, access_level):
        self.job_title = job_title
        self.department = department
        self.access_level = access_level


#create EmployeeTitle table to enable many to many relationship in a normalized db schema, allows a record to be kept of employees previous job titles
class EmployeeTitle(db.Model):

    __tablename__ = "employee_title"

    emp_title_id  = db.Column(db.Integer, db.ForeignKey(Employee.emp_id), primary_key=True)
    emp_job_title = db.Column(db.String(50), db.ForeignKey(Title.job_title), primary_key=True)
    start_date = db.Column(db.String, nullable=False)
    end_date = db.Column(db.String, nullable=True)
    employee = db.relationship("Employee", back_populates = "title")
    titlejoin = db.relationship("Title", back_populates = "emp_title")


    def __init__(self, emp_title_id, emp_job_title, start_date, end_date):
        self.emp_title_id = emp_title_id
        self.emp_job_title = emp_job_title
        self.start_date = start_date
        self.end_date = end_date


#Create Category table
class Category(db.Model):
    category_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def __init__(self, name, description):
        self.name = name
        self.description = description


#Create Supplier Table
class Supplier(db.Model):
    supplier_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    comments = db.Column(db.String(200), nullable=True)

    def __init__(self, name, phone, email, comments):
        self.name = name
        self.phone = phone
        self.email = email
        self.comments = comments

#Create item table
class Item(db.Model):
    item_id  = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name  = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    unit_cost  = db.Column(db.Numeric, nullable=False)
    sale_price  = db.Column(db.Numeric, nullable=False)
    units_in_stock  = db.Column(db.Integer, nullable=False)
    expiration_date  = db.Column(db.String, nullable=True)
    supplier_id = db.Column(db.Integer, nullable=False)
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
       

db.create_all()