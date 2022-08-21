import inventorydb
from inventorydb import db, app
from flask import Flask, request, flash, url_for, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
import datetime
import createtestdata
from flask_login import LoginManager, login_user, logout_user, login_required #https://flask-login.readthedocs.io/en/latest/

app.secret_key = 'key5'

if __name__ == '__main__':
    db.create_all
    db.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app


@app.route('/')
def index():
    return redirect(url_for('login'))

#@app.route('/')
#def login():
#    return render_template('login.html')

#@app.route('/')
#def index():
#    return redirect(url_for('login'))



@login_manager.user_loader
def load_user(emp_id):
    return inventorydb.Employee.query.get(emp_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        id = request.form['username']   

        if inventorydb.Employee.query.get(id):
            login_user(inventorydb.Employee.query.get(id))
            return render_template('menu.html')

    return render_template('login.html')



@app.route('/logout', methods=['GET'])
@login_required
def logout():

    logout_user()
    return render_template("logout.html")




@app.route('/menu')
def menu():
    render_template('menu.html')










@app.route('/additem', methods=['GET', 'POST'])
def additem():

    if request.method == 'POST':
    #  if not request.form['name'] or not request.form['salary'] or not request.form['age']:
    #     flash('Please enter all the fields', 'error')
    # else:

        item = inventorydb.Item(request.form['name'], request.form['description'], int(request.form['unit_cost']), int(request.form['sale_price']), int(request.form['units_in_stock']), request.form['expiration_date'], int(request.form['supplier_id']), int(request.form['category_id']))


        inventorydb.db.session.add(item)
        inventorydb.db.session.commit()
  #      flash('Record was successfully added')

    return render_template('additem.html', suppliers=inventorydb.Supplier.query.all(), categories=inventorydb.Category.query.all())




@app.route('/viewitem', methods=['GET', 'POST'])
def viewitem():

    return render_template('viewitem.html', query=inventorydb.Item.query.all())


@app.route('/deleteitem', methods=['GET', 'POST'])
def deleteitem():

    if request.method == 'POST':
        id = request.form["item_id"]
 
        inventorydb.db.session.delete(inventorydb.Item.query.filter_by(item_id=id).one())
        inventorydb.db.session.commit()
        return render_template('viewitem.html', query=inventorydb.Item.query.all())

    return render_template('deleteitem.html')


@app.route('/selectitem', methods=['GET', 'POST'])
def selectitem():

    if request.method == 'POST':

        id = request.form["item_id"]
        return render_template('updateitem.html', query=inventorydb.Item.query.get(id), suppliers=inventorydb.Supplier.query.all(), categories=inventorydb.Category.query.all())

    return render_template('selectitem.html', items=inventorydb.Item.query.all())



@app.route('/updateitem', methods=['GET', 'POST'])
def updateitem():
    if request.method == 'POST':

        #item=inventorydb.Item.query.get(5)

        id = request.form["item_id"]
        item=inventorydb.Item.query.get(id)
        
        item.name = request.form['name']
        item.description = request.form['description']
        item.unit_cost = (request.form['unit_cost'])
        item.sale_price = (request.form['sale_price'])
        item.units_in_stock = int(request.form['units_in_stock'])
        item.expiration_date = request.form['expiration_date']
        item.supplier_id = int(request.form['supplier_id'])
        item.category_id = int(request.form['category_id'])

        inventorydb.db.session.commit()

        return redirect(url_for('viewitem'))

    return render_template('updateitem.html')


















@app.route('/addemployee', methods=['GET', 'POST'])
def addemployee():



    if request.method == 'POST':
    #  if not request.form['name'] or not request.form['salary'] or not request.form['age']:
    #     flash('Please enter all the fields', 'error')
    # else:
        
        employee = inventorydb.Employee(request.form['first_name'], request.form['last_name'], request.form['pps_number'], request.form['dob'], request.form['hire_date'], request.form['job_title'])
        inventorydb.db.session.add(employee)
        inventorydb.db.session.flush() #flush() use info taken from https://stackoverflow.com/questions/27736122/how-to-insert-into-multiple-tables-to-mysql-with-sqlalchemy
         
        employeetitle = inventorydb.EmployeeTitle(employee.emp_id, request.form['job_title'], request.form['hire_date'], '')
        inventorydb.db.session.add(employeetitle)

        inventorydb.db.session.commit()
  #      flash('Record was successfully added')

    return render_template('addemployee.html', jobtitles=inventorydb.Title.query.all())


@app.route('/viewemployee', methods=['GET', 'POST'])
def viewemployee():

    return render_template('viewemployee.html', employees=inventorydb.Employee.query.all())
    #return render_template('viewemployee.html', employees=inventorydb.Employee.query.join(inventorydb.EmployeeTitle, inventorydb.Employee.emp_id == inventorydb.EmployeeTitle.emp_title_id).filter(inventorydb.Employee.emp_id == inventorydb.EmployeeTitle.emp_title_id).all())
    #return render_template('viewemployee.html', employees=inventorydb.db.session.query(inventorydb.Employee, inventorydb.EmployeeTitle.emp_job_title, inventorydb.Title.access_level).join(inventorydb.Employee).join(inventorydb.EmployeeTitle).join(inventorydb.Title).filter(inventorydb.Employee.emp_id == inventorydb.EmployeeTitle.emp_title_id).all())
    

@app.route('/selectemployee', methods=['GET', 'POST'])
def selectemployee():

    if request.method == 'POST':
        id = request.form["emp_id"]

            
        return render_template('updateemployee.html', query=inventorydb.Employee.query.get(id), titles=inventorydb.Title.query.all())
       

    return render_template('selectemployee.html', employees=inventorydb.Employee.query.all())


@app.route('/updateemployee', methods=['GET', 'POST'])
def updateemployee():
    if request.method == 'POST':

        id = request.form["emp_id"]
        employee=inventorydb.Employee.query.get(id)
        
        employee.first_name = request.form['first_name']
        employee.last_name = request.form['last_name']
        employee.pps_number = (request.form['pps_number'])
        employee.dob = (request.form['dob'])
        employee.hire_date = (request.form['hire_date'])
        employee.title = request.form['title']

        inventorydb.db.session.commit()

        return redirect(url_for('viewemployee'))

    return render_template('updateemployee.html')


@app.route('/deleteemployee', methods=['GET', 'POST'])
def deleteemployee():

    if request.method == 'POST':
        id = request.form["emp_id"]

        try:
            inventorydb.db.session.delete(inventorydb.Employee.query.filter_by(emp_id=id).one())
            inventorydb.db.session.commit()
        except:
            #NEED TO ADD AN ERROR MESSAGE HERE
            return render_template('deleteemployee.html')

    return render_template('deleteemployee.html')






@app.route('/viewtitles', methods=['GET', 'POST'])
def viewtitles():
    return render_template('viewtitles.html', query=inventorydb.Title.query.all())



@app.route('/addtitle', methods=['GET', 'POST'])
def addtitle():
    if request.method =='POST':

        title=inventorydb.Title(request.form['job_title'], request.form['department'], request.form['access_level'])
        inventorydb.db.session.add(title)
        inventorydb.db.session.commit()
    return render_template('addtitle.html')


@app.route('/selecttitle', methods=['GET', 'POST'])
def selecttitle():

    if request.method == 'POST':

        id = request.form["job_title"]
        return render_template('updatetitle.html', query=inventorydb.Title.query.get(id))

    return render_template('selecttitle.html', titles=inventorydb.Title.query.all())


@app.route('/updatetitle', methods=['GET', 'POST'])
def updatetitle():
    if request.method == 'POST':

        id = request.form["job_title"]
        title=inventorydb.Title.query.get(id)
        
        #title.job_title = request.form['job_title']
        title.department = request.form['department']
        title.access_level = int(request.form['access_level'])

        inventorydb.db.session.commit()

        return redirect(url_for('viewtitles'))

    return render_template('updatetitle.html')


    job_title = db.Column(db.String(50), primary_key=True)
    department = db.Column(db.String(50), nullable=False)
    access_level = db.Column(db.Integer, nullable=False)
    emp_title = db.relationship("EmployeeTitle", backref="emp_title", lazy="joined")

    def __init__ (self, job_title, department, access_level):
        self.job_title = job_title
        self.department = department
        self.access_level = access_level


@app.route('/deletetitle', methods=['GET', 'POST'])
def deletetitle():
    if request.method == 'POST':
        id = request.form['job_title']

        try:
            inventorydb.db.session.delete(inventorydb.Title.query.filter_by(job_title=id).one())
            inventorydb.db.session.commit()
        except:
            #NEED TO ADD AN ERROR MESSAGE HERE
            return render_template('deletetitle.html')

    return render_template('deletetitle.html')




@app.route('/viewemployeetitles', methods=['GET', 'POST'])
def viewemployeetitles():
    return render_template('viewemployeetitles.html', query=inventorydb.EmployeeTitle.query.all())



@app.route('/viewsuppliers', methods=['GET', 'POST'])
def viewsuppliers():
    return render_template('viewsuppliers.html', query=inventorydb.Supplier.query.all())





@app.route('/addsupplier', methods=['GET', 'POST'])
def addsupplier():
    if request.method == 'POST':

        supplier = inventorydb.Supplier(request.form['name'], request.form['phone'], request.form['email'], request.form['comments'])
        inventorydb.db.session.add(supplier)
        inventorydb.db.session.commit()

    return render_template('addsupplier.html')


@app.route('/selectsupplier', methods=['GET', 'POST'])
def selectsupplier():

    if request.method == 'POST':

        id = request.form["supplier_id"]
        return render_template('updatesupplier.html', query=inventorydb.Supplier.query.get(id))

    return render_template('selectsupplier.html', suppliers=inventorydb.Supplier.query.all())


@app.route('/updatesupplier', methods=['GET', 'POST'])
def updatesupplier():
    if request.method == 'POST':

        id = request.form["supplier_id"]
        supplier=inventorydb.Supplier.query.get(id)
        
        supplier.name = request.form['name']
        supplier.phone = request.form['phone']
        supplier.email = (request.form['email'])
        supplier.comments = (request.form['comments'])

        inventorydb.db.session.commit()

        return redirect(url_for('viewsuppliers'))

    return render_template('updatesupplier.html')


@app.route('/deletesupplier', methods=['GET', 'POST'])
def deletesupplier():
    if request.method == 'POST':
        id = request.form['supplier_id']

        try:
            inventorydb.db.session.delete(inventorydb.Supplier.query.filter_by(supplier_id=id).one())
            inventorydb.db.session.commit()
        except:
            #NEED TO ADD AN ERROR MESSAGE HERE
            return render_template('deletesupplier.html')

    return render_template('deletesupplier.html')









@app.route('/viewcategories', methods=['GET', 'POST'])
def viewcategories():
    return render_template('viewcategories.html', query=inventorydb.Category.query.all())



@app.route('/addcategory', methods=['GET', 'POST'])
def addcategory():
    if request.method == 'POST':

        category = inventorydb.Category(request.form['name'], request.form['description'])
        inventorydb.db.session.add(category)
        inventorydb.db.session.commit()

    return render_template('addcategory.html')

@app.route('/deletecategory', methods=['GET', 'POST'])
def deletecategory():
    if request.method == 'POST':
        id = request.form['category_id']

        try:
            inventorydb.db.session.delete(inventorydb.Category.query.filter_by(category_id=id).one())
            inventorydb.db.session.commit()
        except:
            #NEED TO ADD AN ERROR MESSAGE HERE
            return render_template('deletecategory.html')

    return render_template('deletecategory.html')


@app.route('/selectcategory', methods=['GET', 'POST'])
def selectcategory():

    if request.method == 'POST':

        id = request.form["category_id"]
        return render_template('updatecategory.html', query=inventorydb.Category.query.get(id))

    return render_template('selectcategory.html', categories=inventorydb.Category.query.all())


@app.route('/updatecategory', methods=['GET', 'POST'])
def updatecategory():
    if request.method == 'POST':

        id = request.form["category_id"]
        category=inventorydb.Category.query.get(id)
        
        category.name = request.form['name']
        category.description = request.form['description']

        inventorydb.db.session.commit()

        return redirect(url_for('viewcategories'))

    return render_template('updatecategory.html')



if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT) #debug=True)
 




