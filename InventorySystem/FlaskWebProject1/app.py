import inventorydb
from inventorydb import db, app
from flask import Flask, request, flash, url_for, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
import datetime
from datetime import timedelta, date
import createtestdata
from flask_login import LoginManager, login_user, logout_user, login_required, current_user #https://flask-login.readthedocs.io/en/latest/
from functools import wraps #https://blog.teclado.com/learn-python-defining-user-access-roles-in-flask/
import requests

app.secret_key = 'key5'

if __name__ == '__main__':
    db.create_all
    db.init_app(app)
    #https://flask-login.readthedocs.io/en/latest/
    #https://flask-login.readthedocs.io/en/latest/#flask_login.LoginManager.login_view
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app


@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=2)

@app.route('/') 
def index():
    return redirect(url_for('login')) #want to make this nav instead???



#decorator for access levels code from https://blog.teclado.com/learn-python-defining-user-access-roles-in-flask/
#and https://circleci.com/blog/authentication-decorators-flask/#:~:text=A%20decorator%20is%20a%20function,being%20assigned%20to%20a%20variable
#additional research & information from https://circleci.com/blog/authentication-decorators-flask/#:~:text=A%20decorator%20is%20a%20function,being%20assigned%20to%20a%20variable.
def requires_access_level(access_level):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            currentjobtitle = inventorydb.EmployeeTitle.query.filter_by(emp_title_id=(current_user.emp_id), end_date='').one()
            currenttitleid = currentjobtitle.emp_job_title
            currentaccesslevel = (inventorydb.Title.query.filter_by(job_title=currenttitleid).one()).access_level

            if not current_user.emp_id:
                return render_template('login.html')

            elif not currentaccesslevel >= access_level:
                return render_template('noauth.html')
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@login_manager.user_loader
def load_user(emp_id):
    return inventorydb.Employee.query.get(emp_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        id = request.form['username']   

        if inventorydb.Employee.query.get(id):
            login_user(inventorydb.Employee.query.get(id))

            currentjobtitle = inventorydb.EmployeeTitle.query.filter_by(emp_title_id=(current_user.emp_id), end_date="").one()
            currenttitleid = currentjobtitle.emp_job_title
            currentaccesslevel = (inventorydb.Title.query.filter_by(job_title=currenttitleid).one()).access_level

            return redirect(url_for('nav' , accesslevel=currentaccesslevel))


        else:
            flash('Invalid Login')

    return render_template('login.html')



@app.route('/logout', methods=['GET'])
@login_required
def logout():

    logout_user()
    return render_template("logout.html")



@app.route('/nav')
@login_required
def nav():

    currentemp=inventorydb.Employee.query.filter_by(emp_id=(current_user.emp_id)).one()
    currenttitle=inventorydb.EmployeeTitle.query.filter_by(emp_title_id=(current_user.emp_id), end_date='').one()
    currenttitleid = currenttitle.emp_job_title
    currentaccesslevel = (inventorydb.Title.query.filter_by(job_title=currenttitleid).one()).access_level

    message = 'Logged in as ' + currenttitle.emp_job_title + ' ' + currentemp.first_name
    flash(message)

    return render_template('nav.html', accesslevel=currentaccesslevel)


#https://api-ninjas.com/api/cocktail
@app.route('/recommendation', methods=['GET', 'POST'])
@login_required
@requires_access_level(2)
def recommendation():

    if request.method == 'POST':
        
        if 'by_name' in request.form:
            name = request.form['name']

        elif 'by_date' in request.form:
            name=inventorydb.Item.query.filter(inventorydb.Item.category_id != 12).order_by(inventorydb.Item.expiration_date).first().name

        api_url = 'https://api.api-ninjas.com/v1/cocktail?ingredients={}'.format(name)

        response = requests.get(api_url, headers={'X-Api-Key': 'e6iZfcExID2SRfreoiuRjw==Al2MlWkq2AbiqHIC'})
        
        if response.status_code == requests.codes.ok and len(response.content) > 2:
            return render_template('recommendation.html', cocktails=response.json(), name=inventorydb.Item.query.filter(inventorydb.Item.category_id != 12).order_by(inventorydb.Item.expiration_date).first().name, date=inventorydb.Item.query.filter(inventorydb.Item.category_id != 12).order_by(inventorydb.Item.expiration_date).first().expiration_date)
        elif response.status_code == requests.codes.ok:
            flash("No results, please try again")
            return render_template('recommendation.html', name=inventorydb.Item.query.filter(inventorydb.Item.category_id != 12).order_by(inventorydb.Item.expiration_date).first().name, date=inventorydb.Item.query.filter(inventorydb.Item.category_id != 12).order_by(inventorydb.Item.expiration_date).first().expiration_date)
        else:
            flash("Error: please try again")
            return render_template('recommendation.html', name=inventorydb.Item.query.filter(inventorydb.Item.category_id != 12).order_by(inventorydb.Item.expiration_date).first().name, date=inventorydb.Item.query.filter(inventorydb.Item.category_id != 12).order_by(inventorydb.Item.expiration_date).first().expiration_date)

    return render_template('recommendation.html', name=inventorydb.Item.query.filter(inventorydb.Item.category_id != 12).order_by(inventorydb.Item.expiration_date).first().name, date=inventorydb.Item.query.filter(inventorydb.Item.category_id != 12).order_by(inventorydb.Item.expiration_date).first().expiration_date)

@app.route('/additem', methods=['GET', 'POST'])
@login_required
@requires_access_level(3)
def additem():

    if request.method == 'POST':

        if not request.form['name'] or not request.form['description'] or not request.form['unit_cost'] or not request.form['sale_price'] or not request.form['units_in_stock'] or not request.form['supplier_id'] or not request.form['category_id']:
            flash('Error: all fields are required')
        else:

            item = inventorydb.Item(request.form['name'], request.form['description'], float(request.form['unit_cost']), float(request.form['sale_price']), int(request.form['units_in_stock']), request.form['expiration_date'], int(request.form['supplier_id']), int(request.form['category_id']))


            inventorydb.db.session.add(item)
            inventorydb.db.session.commit()
            flash('Item was successfully added')

    return render_template('additem.html', suppliers=inventorydb.Supplier.query.all(), categories=inventorydb.Category.query.all())




@app.route('/viewitem', methods=['GET', 'POST'])
@login_required
@requires_access_level(1)
def viewitem():

    return render_template('viewitem.html', query=inventorydb.Item.query.all())


@app.route('/deleteitem', methods=['GET', 'POST'])
@login_required
@requires_access_level(2)
def deleteitem():
    
    id = request.form["item_id"]
    
    if request.method == 'POST':

        if 'delete' in request.form:

            try:
                inventorydb.db.session.delete(inventorydb.Item.query.filter_by(item_id=id).one())

                inventorydb.db.session.commit()
            except:
                message = 'Error: unable to delete the item'
                flash(message)
                return render_template('deleteitem.html', query=inventorydb.Item.query.all())

        else:
            return render_template('viewitem.html', query=inventorydb.Item.query.all()) 

    return redirect(url_for('viewitem', message='Item successfully deleted'))



@app.route('/selectitem', methods=['GET', 'POST'])
@login_required
@requires_access_level(1)
def selectitem():

    currenttitle=inventorydb.EmployeeTitle.query.filter_by(emp_title_id=(current_user.emp_id), end_date='').one()
    currenttitleid = currenttitle.emp_job_title
    currentaccesslevel = (inventorydb.Title.query.filter_by(job_title=currenttitleid).one()).access_level

    if request.method == 'POST':

        id = request.form["item_id"]

        if request.method == 'POST':

            if 'update' in request.form:
                if request.form["item_id"] == "no_id":
                    flash('Please select an item')
                    return render_template('selectitem.html', items=inventorydb.Item.query.all(), accesslevel=currentaccesslevel)
                else:
                    return render_template('updateitem.html', query=inventorydb.Item.query.get(id), suppliers=inventorydb.Supplier.query.all(), categories=inventorydb.Category.query.all())

            elif 'delete' in request.form:
                if request.form["item_id"] == "no_id":
                    flash('Please select an item')
                    return render_template('selectitem.html', items=inventorydb.Item.query.all(), accesslevel=currentaccesslevel)

                else:
                    return render_template('deleteitem.html', query=inventorydb.Item.query.filter(inventorydb.Item.item_id==id).all())

            else: #search item
                if request.form["item_id"] != "no_id": #search by id provided
                    return render_template('viewitem.html', query=inventorydb.Item.query.filter(inventorydb.Item.item_id==id).all())
                else: #search by something other than item ID


                    if request.form["name"] != "":
                        #https://stackoverflow.com/questions/3325467/sqlalchemy-equivalent-to-sql-like-statement
                        #used for case insensitve & fuzze match matching assistance
                        query=inventorydb.Item.query.filter(inventorydb.Item.name.ilike(f'%{request.form["name"]}%')).first()
                        if not query:
                            flash('No items matched your search. View all items below:')
                            return render_template('viewitem.html', query=inventorydb.Item.query.order_by(inventorydb.Item.name).all())
                        else:
                            return render_template('viewitem.html', query=inventorydb.Item.query.filter(inventorydb.Item.name.ilike(f'%{request.form["name"]}%')).order_by(inventorydb.Item.name).all())
                    elif request.form["max_inventory_level"] != "":
                        query=inventorydb.Item.query.filter(inventorydb.Item.units_in_stock <= request.form["max_inventory_level"]).first()
                        if not query:
                            flash('No items matched your search. View all items below:')
                            return render_template('viewitem.html', query=inventorydb.Item.query.order_by(inventorydb.Item.units_in_stock).all())
                        else:
                            return render_template('viewitem.html', query=inventorydb.Item.query.filter(inventorydb.Item.units_in_stock <= request.form["max_inventory_level"]).order_by(inventorydb.Item.units_in_stock).all())
                    
                    elif request.form['min_inventory_level'] != "":
                        query=inventorydb.Item.query.filter(inventorydb.Item.units_in_stock >= request.form["min_inventory_level"]).first()
                        if not query:
                            flash('No items matched your search. View all items below:')
                            return render_template('viewitem.html', query=inventorydb.Item.query.order_by(inventorydb.Item.units_in_stock.desc()).all())
                        else:    
                            return render_template('viewitem.html', query=inventorydb.Item.query.filter(inventorydb.Item.units_in_stock >= request.form["min_inventory_level"]).order_by(inventorydb.Item.units_in_stock.desc()).all())
                    
                    elif request.form['expiration_date'] != "":
                        query=inventorydb.Item.query.filter(inventorydb.Item.expiration_date <= request.form["expiration_date"]).first()
                        if not query:
                            flash('No items matched your search. View all items below:')
                            return render_template('viewitem.html', query=inventorydb.Item.query.order_by(inventorydb.Item.expiration_date).all())

                        else:
                            return render_template('viewitem.html', query=inventorydb.Item.query.filter(inventorydb.Item.expiration_date <= request.form["expiration_date"]).order_by(inventorydb.Item.expiration_date).all())
                   
                    elif request.form['category_id'] != "category_id":
                        return render_template('viewitem.html', query=inventorydb.Item.query.filter(inventorydb.Item.category_id == int(request.form["category_id"])).all())

                    else:
                        flash('Please enter a field')
                        return render_template('selectitem.html', items=inventorydb.Item.query.all(), accesslevel=currentaccesslevel)

    return render_template('selectitem.html', items=inventorydb.Item.query.all(), accesslevel=currentaccesslevel, categories=inventorydb.Category.query.all())



@app.route('/updateitem', methods=['GET', 'POST'])
@login_required
@requires_access_level(2)
def updateitem():
    if request.method == 'POST':

        id = request.form["item_id"]

        if not request.form['name'] or not request.form['description'] or not request.form['unit_cost'] or not request.form['sale_price'] or not request.form['units_in_stock'] or not request.form['supplier_id'] or not request.form['category_id']:
            flash('Error: all fields are required')

        else:

            item=inventorydb.Item.query.get(id)
        
            item.name = request.form['name']
            item.description = request.form['description']
            item.unit_cost = float(request.form['unit_cost'])
            item.sale_price = float(request.form['sale_price'])
            item.units_in_stock = int(request.form['units_in_stock'])
            item.expiration_date = request.form['expiration_date']
            item.supplier_id = int(request.form['supplier_id'])
            item.category_id = int(request.form['category_id'])

            inventorydb.db.session.commit()

            return redirect(url_for('viewitem'))

    return render_template('updateitem.html', query=inventorydb.Item.query.get(id), suppliers=inventorydb.Supplier.query.all(), categories=inventorydb.Category.query.all())





@app.route('/addemployee', methods=['GET', 'POST'])
@login_required
@requires_access_level(3)
def addemployee():

    if request.method == 'POST':

        if not request.form['first_name'] or not request.form['last_name'] or not request.form['pps_number'] or not request.form['dob'] or not request.form['hire_date']:
            flash('Error: all fields are required')

        else:        
            employee = inventorydb.Employee(request.form['first_name'], request.form['last_name'], request.form['pps_number'], request.form['dob'], request.form['hire_date'], request.form['job_title'])
            inventorydb.db.session.add(employee)
            inventorydb.db.session.flush() #flush() use info taken from https://stackoverflow.com/questions/27736122/how-to-insert-into-multiple-tables-to-mysql-with-sqlalchemy
         
            employeetitle = inventorydb.EmployeeTitle(employee.emp_id, request.form['job_title'], request.form['hire_date'], '')
            inventorydb.db.session.add(employeetitle)

            inventorydb.db.session.commit()
            flash('Employee was successfully added')

    return render_template('addemployee.html', jobtitles=inventorydb.Title.query.all())


@app.route('/viewemployee', methods=['GET', 'POST'])
@login_required
@requires_access_level(2)
def viewemployee():


    #query help from https://stackoverflow.com/questions/28518510/select-attributes-from-different-joined-tables-with-flask-and-sqlalchemy
    #and https://stackoverflow.com/questions/46657757/basequery-object-not-callable-inside-a-flask-app-using-sqlalchemy
    #and https://stackoverflow.com/questions/60444153/flask-sql-alchemy-join-multiple-tables

    return render_template('viewemployee.html',
                                               employees=inventorydb.db.session.query(inventorydb.Employee.emp_id, inventorydb.Employee.first_name, inventorydb.Employee.last_name, inventorydb.Employee.pps_number, inventorydb.Employee.dob, inventorydb.Employee.hire_date                                                                                  
                                                    ,inventorydb.Title.job_title, inventorydb.Title.access_level)
                                                    .outerjoin(inventorydb.EmployeeTitle, inventorydb.Employee.emp_id==inventorydb.EmployeeTitle.emp_title_id)
                                                    .outerjoin(inventorydb.Title, inventorydb.Title.job_title==inventorydb.EmployeeTitle.emp_job_title).filter(inventorydb.EmployeeTitle.end_date=="").all())

    








@app.route('/selectemployee', methods=['GET', 'POST'])
@login_required
@requires_access_level(3)
def selectemployee():



    if request.method == 'POST':
        id = request.form["emp_id"]

        if 'update' in request.form:
            return render_template('updateemployee.html', titles = inventorydb.Title.query.all(),
                                                                                          employee=inventorydb.db.session.query(inventorydb.Employee.emp_id, inventorydb.Employee.first_name, inventorydb.Employee.last_name, inventorydb.Employee.pps_number, inventorydb.Employee.dob, inventorydb.Employee.hire_date                                                                                  
                                                                                         ,inventorydb.Title.job_title)
                                                                                         .outerjoin(inventorydb.EmployeeTitle, inventorydb.Employee.emp_id==inventorydb.EmployeeTitle.emp_title_id)
                                                                                         .outerjoin(inventorydb.Title, inventorydb.Title.job_title==inventorydb.EmployeeTitle.emp_job_title).filter(inventorydb.Employee.emp_id==id, inventorydb.EmployeeTitle.end_date=="").all())
            
        elif 'delete' in request.form:

            if current_user.emp_id == int(id):
                message = "Error: Cannot delete current user"  
                flash(message)
                return render_template('selectemployee.html', employees=inventorydb.Employee.query.all())

            elif id == 1:
                message = "Error: Cannot delete the admin user"  
                flash(message)
                return render_template('selectemployee.html', employees=inventorydb.Employee.query.all())

            else:
                return render_template('deleteemployee.html', titles = inventorydb.Title.query.all(),
                                                                                          employee=inventorydb.db.session.query(inventorydb.Employee.emp_id, inventorydb.Employee.first_name, inventorydb.Employee.last_name, inventorydb.Employee.pps_number, inventorydb.Employee.dob, inventorydb.Employee.hire_date                                                                                  
                                                                                         ,inventorydb.Title.job_title)
                                                                                         .outerjoin(inventorydb.EmployeeTitle, inventorydb.Employee.emp_id==inventorydb.EmployeeTitle.emp_title_id)
                                                                                         .outerjoin(inventorydb.Title, inventorydb.Title.job_title==inventorydb.EmployeeTitle.emp_job_title).filter(inventorydb.Employee.emp_id==id, inventorydb.EmployeeTitle.end_date=="").all())
          
            


        #WORKS return render_template('updateemployee.html', query=inventorydb.Employee.query.get(id) 





                               #, query=inventorydb.db.session.query(inventorydb.Employee.emp_id, inventorydb.Employee.first_name, inventorydb.Employee.last_name, inventorydb.Employee.pps_number, inventorydb.Employee.dob, inventorydb.Employee.hire_date                                                                                  
                               #                     ,inventorydb.Title.job_title, inventorydb.Title.access_level)
                               #                     .outerjoin(inventorydb.EmployeeTitle, inventorydb.Employee.emp_id==inventorydb.EmployeeTitle.emp_title_id)
                               #                     .outerjoin(inventorydb.Title, inventorydb.Title.job_title==inventorydb.EmployeeTitle.emp_job_title).filter_by(inventorydb.Employee.emp_id==id).fisrt())
       
    return render_template('selectemployee.html', employees=inventorydb.Employee.query.all())


@app.route('/updateemployee', methods=['GET', 'POST'])
@login_required
@requires_access_level(3)
def updateemployee():
    if request.method == 'POST':

        id = request.form["emp_id"]
        
        if 'update' in request.form:

            if not request.form['first_name'] or not request.form['last_name'] or not request.form['pps_number'] or not request.form['dob'] or not request.form['hire_date']:
                flash('Error: all fields are required')

                return render_template('updateemployee.html', titles = inventorydb.Title.query.all(),
                                                                                          employee=inventorydb.db.session.query(inventorydb.Employee.emp_id, inventorydb.Employee.first_name, inventorydb.Employee.last_name, inventorydb.Employee.pps_number, inventorydb.Employee.dob, inventorydb.Employee.hire_date                                                                                  
                                                                                         ,inventorydb.Title.job_title)
                                                                                         .outerjoin(inventorydb.EmployeeTitle, inventorydb.Employee.emp_id==inventorydb.EmployeeTitle.emp_title_id)
                                                                                         .outerjoin(inventorydb.Title, inventorydb.Title.job_title==inventorydb.EmployeeTitle.emp_job_title).filter(inventorydb.Employee.emp_id==id).all())
       

            else:

                employee=inventorydb.Employee.query.get(id)

                #get current job title entry
                current_emp_title = inventorydb.EmployeeTitle.query.filter(inventorydb.EmployeeTitle.emp_title_id == employee.emp_id, inventorydb.EmployeeTitle.end_date == "").first()
                current_emp_title.end_date = date.today()
                
                #add new job title
                new_emp_title = inventorydb.EmployeeTitle(employee.emp_id, request.form['job_title'], date.today(), '')
                inventorydb.db.session.add(new_emp_title)



                #title = employee.title

                #jobtitle=inventorydb.Employee.query.get(title)

                employee.first_name = request.form['first_name']
                employee.last_name = request.form['last_name']
                employee.pps_number = (request.form['pps_number'])
                employee.dob = (request.form['dob'])
                employee.hire_date = (request.form['hire_date'])
                #employee.title = request.form['job_title']

                inventorydb.db.session.commit()

                return redirect(url_for('viewemployee'))

        else:
            return render_template('selectemployee.html', employees=inventorydb.Employee.query.all())

    return render_template('updateemployee.html')


@app.route('/deleteemployee', methods=['GET', 'POST'])
@login_required
@requires_access_level(3)
def deleteemployee():

    id = request.form["emp_id"]
    
    if request.method == 'POST':

        if 'delete' in request.form:


            try:

                inventorydb.db.session.delete(inventorydb.Employee.query.filter_by(emp_id=id).one())

                inventorydb.EmployeeTitle.query.filter(inventorydb.EmployeeTitle.emp_title_id == id).delete()
                #inventorydb.db.session.delete(inventorydb.EmployeeTitle).where(emp_title_id == id)
                #inventorydb.db.session.query.filter(inventorydb.EmployeeTitle.emp_title_id == id).delete()
                #inventorydb.db.session.delete(inventorydb.EmployeeTitle.query.filter_by(inventorydb.EmployeeTitle.emp_title_id == id).all())

                inventorydb.db.session.commit()
            except:
                message = 'Error: unable to delete the employee'
                flash(message)
                return render_template('deleteemployee.html')

        else:
            return render_template('selectemployee.html', employees=inventorydb.Employee.query.all())

    return redirect(url_for('viewemployee', message='Employee successfully deleted'))
    #return render_template('viewemployee.html')






@app.route('/viewtitles', methods=['GET', 'POST'])
@login_required
@requires_access_level(2)
def viewtitles():
    return render_template('viewtitles.html', query=inventorydb.Title.query.all())



@app.route('/addtitle', methods=['GET', 'POST'])
@login_required
@requires_access_level(3)
def addtitle():
    if request.method =='POST':
        if not request.form['job_title'] or not request.form['department'] or not request.form['access_level']:
            flash('Error: all fields are required')

        else:     
            title=inventorydb.Title(request.form['job_title'], request.form['department'], request.form['access_level'])
            inventorydb.db.session.add(title)
            inventorydb.db.session.commit()
            flash('Title successfully added')

    return render_template('addtitle.html')


@app.route('/selecttitle', methods=['GET', 'POST'])
@login_required
@requires_access_level(3)
def selecttitle():

    if request.method == 'POST':

        id = request.form["job_title"]
        return render_template('updatetitle.html', query=inventorydb.Title.query.get(id))

    return render_template('selecttitle.html', titles=inventorydb.Title.query.all())


@app.route('/updatetitle', methods=['GET', 'POST'])
@login_required
@requires_access_level(3)
def updatetitle():
    if request.method == 'POST':

        id = request.form["job_title"]

        if not request.form['job_title'] or not request.form['department'] or not request.form['access_level']:
            flash('Error: all fields are required')

        else:     

            title=inventorydb.Title.query.get(id)
        
            title.department = request.form['department']
            title.access_level = int(request.form['access_level'])

            inventorydb.db.session.commit()

            return redirect(url_for('viewtitles'))

    return render_template('updatetitle.html', query=inventorydb.Title.query.get(id))


    job_title = db.Column(db.String(50), primary_key=True)
    department = db.Column(db.String(50), nullable=False)
    access_level = db.Column(db.Integer, nullable=False)
    emp_title = db.relationship("EmployeeTitle", backref="emp_title", lazy="joined")

    def __init__ (self, job_title, department, access_level):
        self.job_title = job_title
        self.department = department
        self.access_level = access_level


@app.route('/deletetitle', methods=['GET', 'POST'])
@login_required
@requires_access_level(3)
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
@login_required
@requires_access_level(2)
def viewemployeetitles():
    return render_template('viewemployeetitles.html', query=inventorydb.EmployeeTitle.query.all())



@app.route('/viewsuppliers', methods=['GET', 'POST'])
@login_required
@requires_access_level(1)
def viewsuppliers():
    return render_template('viewsuppliers.html', query=inventorydb.Supplier.query.all())





@app.route('/addsupplier', methods=['GET', 'POST'])
@login_required
@requires_access_level(2)
def addsupplier():
    if request.method == 'POST':

        if not request.form['name'] or not request.form['phone'] or not request.form['email']:
            flash('Error: name, phone and email fields are required')

        else:     
            supplier = inventorydb.Supplier(request.form['name'], request.form['phone'], request.form['email'], request.form['comments'])
            inventorydb.db.session.add(supplier)
            inventorydb.db.session.commit()
            flash('Supplier successfully added')

    return render_template('addsupplier.html')


@app.route('/selectsupplier', methods=['GET', 'POST'])
@login_required
@requires_access_level(2)
def selectsupplier():

    if request.method == 'POST':

        id = request.form["supplier_id"]
        return render_template('updatesupplier.html', query=inventorydb.Supplier.query.get(id))

    return render_template('selectsupplier.html', suppliers=inventorydb.Supplier.query.all())


@app.route('/updatesupplier', methods=['GET', 'POST'])
@login_required
@requires_access_level(2)
def updatesupplier():
    if request.method == 'POST':

        id = request.form["supplier_id"]

        if not request.form['name'] or not request.form['phone'] or not request.form['email']:
            flash('Error: name, phone and email fields are required')

        else:     
 
            supplier=inventorydb.Supplier.query.get(id)
        
            supplier.name = request.form['name']
            supplier.phone = request.form['phone']
            supplier.email = (request.form['email'])
            supplier.comments = (request.form['comments'])

            inventorydb.db.session.commit()

            return redirect(url_for('viewsuppliers'))

    return render_template('updatesupplier.html', query=inventorydb.Supplier.query.get(id))


@app.route('/deletesupplier', methods=['GET', 'POST'])
@login_required
@requires_access_level(2)
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
@login_required
@requires_access_level(1)
def viewcategories():
    return render_template('viewcategories.html', query=inventorydb.Category.query.all())



@app.route('/addcategory', methods=['GET', 'POST'])
@login_required
@requires_access_level(2)
def addcategory():
    if request.method == 'POST':
        if not request.form['name'] or not request.form['description']:
            flash('Error: all fields are required')

        else:    

            category = inventorydb.Category(request.form['name'], request.form['description'])
            inventorydb.db.session.add(category)
            inventorydb.db.session.commit()
            flash('Supplier successfully added')

    return render_template('addcategory.html')

@app.route('/deletecategory', methods=['GET', 'POST'])
@login_required
@requires_access_level(2)
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
@login_required
@requires_access_level(2)
def selectcategory():

    if request.method == 'POST':

        id = request.form["category_id"]
        return render_template('updatecategory.html', query=inventorydb.Category.query.get(id))

    return render_template('selectcategory.html', categories=inventorydb.Category.query.all())


@app.route('/updatecategory', methods=['GET', 'POST'])
@login_required
@requires_access_level(2)
def updatecategory():
    if request.method == 'POST':
        id = request.form["category_id"]
        if not request.form['name'] or not request.form['description']:
            flash('Error: all fields are required')

        else:    


            category=inventorydb.Category.query.get(id)
        
            category.name = request.form['name']
            category.description = request.form['description']

            inventorydb.db.session.commit()

            return redirect(url_for('viewcategories'))

    return render_template('updatecategory.html', query=inventorydb.Category.query.get(id))



if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT) #debug=True)
 




