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


#function to facilitate automatically logging out the user after a period of time of inactivity (2 minutes)
#checks to confirm if login has expired each time a user trie to perfom a new function using app.before request
#code assistance from https://stackoverflow.com/questions/11783025/is-there-an-easy-way-to-make-sessions-timeout-in-flask
@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=2)


@app.route('/') 
def index():
    return redirect(url_for('login'))


#decorator created to restrict access to pages based on the user's access level as defined by the employee title & corresponding access level
#decorator for access levels code from https://blog.teclado.com/learn-python-defining-user-access-roles-in-flask/
#and https://circleci.com/blog/authentication-decorators-flask/#:~:text=A%20decorator%20is%20a%20function,being%20assigned%20to%20a%20variable
#additional research & information from https://circleci.com/blog/authentication-decorators-flask/#:~:text=A%20decorator%20is%20a%20function,being%20assigned%20to%20a%20variable.
def requires_access_level(access_level):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            #link the employee to the access level via employeetitle table & title table
            currentjobtitle = inventorydb.EmployeeTitle.query.filter_by(emp_title_id=(current_user.emp_id), end_date='').one()
            currenttitleid = currentjobtitle.emp_job_title
            currentaccesslevel = (inventorydb.Title.query.filter_by(job_title=currenttitleid).one()).access_level

            #if the current user's acccess level is equal or greater than the required access level grant permission to view the requested pade
            if not current_user.emp_id:
                return render_template('login.html')
            
            #if the current user's access level is lower than required do not grant access
            elif not currentaccesslevel >= access_level:
                return render_template('noauth.html')
            return f(*args, **kwargs)
        return decorated_function
    return decorator


#enable ability to use current user later
#https://flask-login.readthedocs.io/en/latest/
@login_manager.user_loader
def load_user(emp_id):
    return inventorydb.Employee.query.get(emp_id)




#Function for loging in a user - required for all access
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        #the employees first name in the system is their username
        name = request.form['username']

        #the password is the employee id number - based on current restaurant system best practices
        id = request.form['password']   

        #check if the username & password are assosiated with an employee in the system
        if inventorydb.Employee.query.get(id) and inventorydb.Employee.query.get(id).first_name == name:
            #if the login info is correct, log in the user
            login_user(inventorydb.Employee.query.get(id))

            #link tables to get current access level in order to determine what to display on the home page
            currentjobtitle = inventorydb.EmployeeTitle.query.filter_by(emp_title_id=(current_user.emp_id), end_date="").one()
            currenttitleid = currentjobtitle.emp_job_title
            currentaccesslevel = (inventorydb.Title.query.filter_by(job_title=currenttitleid).one()).access_level

            return redirect(url_for('nav' , accesslevel=currentaccesslevel))

        #if the username & password do not match with an employee in the system do not log anyone in, instead print error message
        else:
            flash('Invalid Login')

    return render_template('login.html')


#funtion for logging out a user when a user chooses to
@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return render_template("logout.html")


#Function for displaying the home navigation page
@app.route('/nav')
@login_required
def nav():

    #Get the current user's access level (via 3 linked tables) in order to display the correct functionality options
    currentemp=inventorydb.Employee.query.filter_by(emp_id=(current_user.emp_id)).one()
    currenttitle=inventorydb.EmployeeTitle.query.filter_by(emp_title_id=(current_user.emp_id), end_date='').one()
    currenttitleid = currenttitle.emp_job_title
    currentaccesslevel = (inventorydb.Title.query.filter_by(job_title=currenttitleid).one()).access_level

    #display message on home page indicating the current user
    message = 'Logged in as ' + currenttitle.emp_job_title + ' ' + currentemp.first_name
    flash(message)

    return render_template('nav.html', accesslevel=currentaccesslevel)


#Function to make recommendations based on call to API
#api from
#https://api-ninjas.com/api/cocktail
@app.route('/recommendation', methods=['GET', 'POST'])
@login_required
@requires_access_level(2)
def recommendation():

    if request.method == 'POST':
        
        #if the user searches using the input any ingedients field
        if 'by_name' in request.form:
            name = request.form['name']
        
        #or if the user wants to see recommendations by the next expiring item
        elif 'by_date' in request.form:
            #name is the name of the ingredient going to be passed to the API, set here to the name of the item with the closest expiry date, excluding category 12 (misc) items
            name=inventorydb.Item.query.filter(inventorydb.Item.category_id != 12).order_by(inventorydb.Item.expiration_date).first().name

        #call to API to find coctails containing the ingredient stored in name variable above
        api_url = 'https://api.api-ninjas.com/v1/cocktail?ingredients={}'.format(name)

        #from API documentation linked above
        response = requests.get(api_url, headers={'X-Api-Key': 'e6iZfcExID2SRfreoiuRjw==Al2MlWkq2AbiqHIC'})
        
        #check to see if the call was successful AND results were returned
        if response.status_code == requests.codes.ok and len(response.content) > 2:
            return render_template('recommendation.html', cocktails=response.json(), name=inventorydb.Item.query.filter(inventorydb.Item.category_id != 12).order_by(inventorydb.Item.expiration_date).first().name, date=inventorydb.Item.query.filter(inventorydb.Item.category_id != 12).order_by(inventorydb.Item.expiration_date).first().expiration_date)
        
        #check to esse if the call was considered successful, but didnt actually return any results
        elif response.status_code == requests.codes.ok:
            flash("No results, please try again")
            return render_template('recommendation.html', name=inventorydb.Item.query.filter(inventorydb.Item.category_id != 12).order_by(inventorydb.Item.expiration_date).first().name, date=inventorydb.Item.query.filter(inventorydb.Item.category_id != 12).order_by(inventorydb.Item.expiration_date).first().expiration_date)
        
        #Call was unsuccessful
        else:
            flash("Error: please try again")
            return render_template('recommendation.html', name=inventorydb.Item.query.filter(inventorydb.Item.category_id != 12).order_by(inventorydb.Item.expiration_date).first().name, date=inventorydb.Item.query.filter(inventorydb.Item.category_id != 12).order_by(inventorydb.Item.expiration_date).first().expiration_date)

    return render_template('recommendation.html', name=inventorydb.Item.query.filter(inventorydb.Item.category_id != 12).order_by(inventorydb.Item.expiration_date).first().name, date=inventorydb.Item.query.filter(inventorydb.Item.category_id != 12).order_by(inventorydb.Item.expiration_date).first().expiration_date)

#allow user to add a new item
@app.route('/additem', methods=['GET', 'POST'])
@login_required
@requires_access_level(2)
def additem():

    if request.method == 'POST':

        #check to ensure all fields are not empty
        if not request.form['name'] or not request.form['description'] or not request.form['unit_cost'] or not request.form['sale_price'] or not request.form['units_in_stock'] or not request.form['supplier_id'] or not request.form['category_id']:
            flash('Error: all fields are required')
        
        #if all required info present, add item
        else:
            item = inventorydb.Item(request.form['name'], request.form['description'], float(request.form['unit_cost']), float(request.form['sale_price']), int(request.form['units_in_stock']), request.form['expiration_date'], int(request.form['supplier_id']), int(request.form['category_id']))

            inventorydb.db.session.add(item)
            inventorydb.db.session.commit()
            flash('Item was successfully added')

    return render_template('additem.html', suppliers=inventorydb.Supplier.query.all(), categories=inventorydb.Category.query.all())


#allow user to view all items
@app.route('/viewitem', methods=['GET', 'POST'])
@login_required
@requires_access_level(1)
def viewitem():
    return render_template('viewitem.html', query=inventorydb.Item.query.all())


#allow user to delete item 
@app.route('/deleteitem', methods=['GET', 'POST'])
@login_required
@requires_access_level(2)
def deleteitem():
    
    #get current access level in order to pass to selectitem
    currenttitle=inventorydb.EmployeeTitle.query.filter_by(emp_title_id=(current_user.emp_id), end_date='').one()
    currenttitleid = currenttitle.emp_job_title
    currentaccesslevel = (inventorydb.Title.query.filter_by(job_title=currenttitleid).one()).access_level

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
            return render_template('selectitem.html', items=inventorydb.Item.query.all(), accesslevel=currentaccesslevel, categories=inventorydb.Category.query.all())

    return redirect(url_for('viewitem', message='Item successfully deleted'))


#Allow user to select an item (for the purpose of updating/deleting/sesarching)
@app.route('/selectitem', methods=['GET', 'POST'])
@login_required
@requires_access_level(1)
def selectitem():

    #get current access level of user
    currenttitle=inventorydb.EmployeeTitle.query.filter_by(emp_title_id=(current_user.emp_id), end_date='').one()
    currenttitleid = currenttitle.emp_job_title
    currentaccesslevel = (inventorydb.Title.query.filter_by(job_title=currenttitleid).one()).access_level

    if request.method == 'POST':

        id = request.form["item_id"]

        if request.method == 'POST':

            #if the user selects to update the selected item
            if 'update' in request.form:
                #error check if no item was selected
                if request.form["item_id"] == "no_id":
                    flash('Please select an item')
                    return render_template('selectitem.html', items=inventorydb.Item.query.all(), accesslevel=currentaccesslevel)
               #if an item was correctly selected, send the user to the update item page, passing through the relevent item information
                else:
                    return render_template('updateitem.html', query=inventorydb.Item.query.get(id), suppliers=inventorydb.Supplier.query.all(), categories=inventorydb.Category.query.all())

            #if the user selects to delete the selected item
            elif 'delete' in request.form:
                #error check if no item was selected
                if request.form["item_id"] == "no_id":
                    flash('Please select an item')
                    return render_template('selectitem.html', items=inventorydb.Item.query.all(), accesslevel=currentaccesslevel)
                
                #if an item was correctly selected, send the user to the delete item page, passing through the relevent item information
                else:
                    return render_template('deleteitem.html', query=inventorydb.Item.query.filter(inventorydb.Item.item_id==id).all())

            #the user selects to search for an item
            else: #search item

                #"no_id" is the default value on the html form, if NOT no_id (ie. if the user has selected an item by id), then search the item by the id provided
                if request.form["item_id"] != "no_id":
                    return render_template('viewitem.html', query=inventorydb.Item.query.filter(inventorydb.Item.item_id==id).all())
                
                #search by something other than item ID
                else:

                    #if a name was provided to search by
                    if request.form["name"] != "":
                        #https://stackoverflow.com/questions/3325467/sqlalchemy-equivalent-to-sql-like-statement
                        #used for case insensitve & fuzze match matching assistance
                        query=inventorydb.Item.query.filter(inventorydb.Item.name.ilike(f'%{request.form["name"]}%')).first()
                        #error check if no item was found
                        if not query:
                            flash('No items matched your search. View all items below:')
                            return render_template('viewitem.html', query=inventorydb.Item.query.order_by(inventorydb.Item.name).all())

                        #display the item(s) in question -> send to view page but only pass through selected items in query
                        else:
                            return render_template('viewitem.html', query=inventorydb.Item.query.filter(inventorydb.Item.name.ilike(f'%{request.form["name"]}%')).order_by(inventorydb.Item.name).all())
                    
                   #if a max inventory level was provided to search by     
                    elif request.form["max_inventory_level"] != "":
                        query=inventorydb.Item.query.filter(inventorydb.Item.units_in_stock <= request.form["max_inventory_level"]).first()
                        #error check if no item was found
                        if not query:
                            flash('No items matched your search. View all items below:')
                            return render_template('viewitem.html', query=inventorydb.Item.query.order_by(inventorydb.Item.units_in_stock).all())
                        
                        #display the item(s) in question -> send to view page but only pass through selected items in query                    
                        else:
                            return render_template('viewitem.html', query=inventorydb.Item.query.filter(inventorydb.Item.units_in_stock <= request.form["max_inventory_level"]).order_by(inventorydb.Item.units_in_stock).all())
                    
                    #if a min inventory level was provided to search by
                    elif request.form['min_inventory_level'] != "":
                        query=inventorydb.Item.query.filter(inventorydb.Item.units_in_stock >= request.form["min_inventory_level"]).first()
                        #error check if no item was found
                        if not query:
                            flash('No items matched your search. View all items below:')
                            return render_template('viewitem.html', query=inventorydb.Item.query.order_by(inventorydb.Item.units_in_stock.desc()).all())

                        #display the item(s) in question -> send to view page but only pass through selected items in query                    
                        else:    
                            return render_template('viewitem.html', query=inventorydb.Item.query.filter(inventorydb.Item.units_in_stock >= request.form["min_inventory_level"]).order_by(inventorydb.Item.units_in_stock.desc()).all())
                    
                    #if an expiration date was provided to search by
                    elif request.form['expiration_date'] != "":
                        query=inventorydb.Item.query.filter(inventorydb.Item.expiration_date <= request.form["expiration_date"]).first()
                        
                        #error check if no item was found                        
                        if not query:
                            flash('No items matched your search. View all items below:')
                            return render_template('viewitem.html', query=inventorydb.Item.query.order_by(inventorydb.Item.expiration_date).all())

                        #display the item(s) in question -> send to view page but only pass through selected items in query 
                        else:
                            return render_template('viewitem.html', query=inventorydb.Item.query.filter(inventorydb.Item.expiration_date <= request.form["expiration_date"]).order_by(inventorydb.Item.expiration_date).all())
                   
                    #If a category was selected (not category_id, which is the default value) to search by category
                    elif request.form['category_id'] != "category_id":
                        query=inventorydb.Item.query.filter(inventorydb.Item.category_id == int(request.form["category_id"])).first()
                        #error check if no item was found   
                        if not query:
                            flash('No items matched your search. View all items below:')
                            return render_template('viewitem.html', query=inventorydb.Item.query.order_by(inventorydb.Item.expiration_date).all())
                        #display the item(s) in question -> send to view page but only pass through selected items in query         
                        else:
                            return render_template('viewitem.html', query=inventorydb.Item.query.filter(inventorydb.Item.category_id == int(request.form["category_id"])).all())

                    #no search critera was given
                    else:
                        flash('Please enter a field')
                        return render_template('selectitem.html', items=inventorydb.Item.query.all(), accesslevel=currentaccesslevel)

    return render_template('selectitem.html', items=inventorydb.Item.query.all(), accesslevel=currentaccesslevel, categories=inventorydb.Category.query.all())


#allow user to update item
@app.route('/updateitem', methods=['GET', 'POST'])
@login_required
@requires_access_level(2)
def updateitem():

    #get current user access level
    currenttitle=inventorydb.EmployeeTitle.query.filter_by(emp_title_id=(current_user.emp_id), end_date='').one()
    currenttitleid = currenttitle.emp_job_title
    currentaccesslevel = (inventorydb.Title.query.filter_by(job_title=currenttitleid).one()).access_level
    

    if request.method == 'POST':

        #set the id to the item_id on the request form, selected by user on select item page
        id = request.form["item_id"]
        
        if 'update' in request.form:

            #error check to make sure all information is provided
            if not request.form['name'] or not request.form['description'] or not request.form['unit_cost'] or not request.form['sale_price'] or not request.form['units_in_stock'] or not request.form['supplier_id'] or not request.form['category_id']:
                flash('Error: all fields are required')

            #if all information given update item
            else:

                #instance of relevent item by item_id
                item=inventorydb.Item.query.get(id)
        
                #update item with provided info
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

        #cancel button selected
        else: 
            return render_template('selectitem.html', items=inventorydb.Item.query.all(), accesslevel=currentaccesslevel, categories=inventorydb.Category.query.all())


    return render_template('updateitem.html', query=inventorydb.Item.query.get(id), suppliers=inventorydb.Supplier.query.all(), categories=inventorydb.Category.query.all())




#allow user to add employee
@app.route('/addemployee', methods=['GET', 'POST'])
@login_required
@requires_access_level(3)
def addemployee():

    if request.method == 'POST':

        #ensure all fields are entered
        if not request.form['first_name'] or not request.form['last_name'] or not request.form['pps_number'] or not request.form['dob'] or not request.form['hire_date']:
            flash('Error: all fields are required')

        #add employee
        else:        
            #add employee using user inputted data
            employee = inventorydb.Employee(request.form['first_name'], request.form['last_name'], request.form['pps_number'], request.form['dob'], request.form['hire_date'], request.form['job_title'])
            inventorydb.db.session.add(employee)
            inventorydb.db.session.flush() #flush() use info taken from https://stackoverflow.com/questions/27736122/how-to-insert-into-multiple-tables-to-mysql-with-sqlalchemy
         
            #add new employee title entry to ensure PK / FK is enforced correctly
            employeetitle = inventorydb.EmployeeTitle(employee.emp_id, request.form['job_title'], request.form['hire_date'], '')
            inventorydb.db.session.add(employeetitle)

            inventorydb.db.session.commit()
            flash('Employee was successfully added')

    return render_template('addemployee.html', jobtitles=inventorydb.Title.query.all())

#allow user to view employees
@app.route('/viewemployee', methods=['GET', 'POST'])
@login_required
@requires_access_level(2)
def viewemployee():


    #query help from https://stackoverflow.com/questions/28518510/select-attributes-from-different-joined-tables-with-flask-and-sqlalchemy
    #and https://stackoverflow.com/questions/46657757/basequery-object-not-callable-inside-a-flask-app-using-sqlalchemy
    #and https://stackoverflow.com/questions/60444153/flask-sql-alchemy-join-multiple-tables
    #above used for information on joining tables, as need to link 3 tables to show data correctly
    return render_template('viewemployee.html', 
                                               employees=inventorydb.db.session.query(inventorydb.Employee.emp_id, inventorydb.Employee.first_name, inventorydb.Employee.last_name, inventorydb.Employee.pps_number, inventorydb.Employee.dob, inventorydb.Employee.hire_date                                                                                  
                                                    ,inventorydb.Title.job_title, inventorydb.Title.access_level)
                                                    .outerjoin(inventorydb.EmployeeTitle, inventorydb.Employee.emp_id==inventorydb.EmployeeTitle.emp_title_id)
                                                    .outerjoin(inventorydb.Title, inventorydb.Title.job_title==inventorydb.EmployeeTitle.emp_job_title).filter(inventorydb.EmployeeTitle.end_date=="").all())

    
#allow users to select an employee
@app.route('/selectemployee', methods=['GET', 'POST'])
@login_required
@requires_access_level(3)
def selectemployee():

    if request.method == 'POST':
        id = request.form["emp_id"]

        #user selected to update the employee
        if 'update' in request.form:

            #hidden is the default field, so check to ensure user has actually selected an employee
            if id == "hidden":
                message = "Error: Please select an employee"  
                flash(message)
                return render_template('selectemployee.html', employees=inventorydb.Employee.query.all())

            #Do not allow user to update themselves
            elif current_user.emp_id == int(id):
                message = "Error: Cannot update current user"  
                flash(message)
                return render_template('selectemployee.html', employees=inventorydb.Employee.query.all())

            #do not allow the user to update the primary admin user (hard coded by ID as other admin users may be created)
            elif int(id) == 9000123:
                message = "Error: Cannot update the admin user"  
                flash(message)
                return render_template('selectemployee.html', employees=inventorydb.Employee.query.all())
            #send to update emp page, passing through info about employee selected to be displayed
            else:
                return render_template('updateemployee.html', titles = inventorydb.Title.query.all(),
                                                                                          employee=inventorydb.db.session.query(inventorydb.Employee.emp_id, inventorydb.Employee.first_name, inventorydb.Employee.last_name, inventorydb.Employee.pps_number, inventorydb.Employee.dob, inventorydb.Employee.hire_date                                                                                  
                                                                                         ,inventorydb.Title.job_title)
                                                                                         .outerjoin(inventorydb.EmployeeTitle, inventorydb.Employee.emp_id==inventorydb.EmployeeTitle.emp_title_id)
                                                                                         .outerjoin(inventorydb.Title, inventorydb.Title.job_title==inventorydb.EmployeeTitle.emp_job_title).filter(inventorydb.Employee.emp_id==id, inventorydb.EmployeeTitle.end_date=="").all())
         
        #user selected to delete the employee
        elif 'delete' in request.form:

            #hidden is the default field, so check to ensure user has actually selected an employee
            if id == "hidden":
                message = "Error: Please select an employee"  
                flash(message)
                return render_template('selectemployee.html', employees=inventorydb.Employee.query.all())

            #Do not allow user to delete themselves
            elif current_user.emp_id == int(id):
                message = "Error: Cannot delete current user"  
                flash(message)
                return render_template('selectemployee.html', employees=inventorydb.Employee.query.all())

            #Do not allow the user to delete the primary admin user (hard coded by ID as other admin users may be created)
            elif id == 9000123:
                message = "Error: Cannot delete the admin user"  
                flash(message)
                return render_template('selectemployee.html', employees=inventorydb.Employee.query.all())
           
           #send to delete emp page, passing through info about employee selected to be displayed
            else:
                return render_template('deleteemployee.html', titles = inventorydb.Title.query.all(),
                                                                                          employee=inventorydb.db.session.query(inventorydb.Employee.emp_id, inventorydb.Employee.first_name, inventorydb.Employee.last_name, inventorydb.Employee.pps_number, inventorydb.Employee.dob, inventorydb.Employee.hire_date                                                                                  
                                                                                         ,inventorydb.Title.job_title)
                                                                                         .outerjoin(inventorydb.EmployeeTitle, inventorydb.Employee.emp_id==inventorydb.EmployeeTitle.emp_title_id)
                                                                                         .outerjoin(inventorydb.Title, inventorydb.Title.job_title==inventorydb.EmployeeTitle.emp_job_title).filter(inventorydb.Employee.emp_id==id, inventorydb.EmployeeTitle.end_date=="").all())
       
    return render_template('selectemployee.html', employees=inventorydb.Employee.query.all())

#Allow user to update employee
@app.route('/updateemployee', methods=['GET', 'POST'])
@login_required
@requires_access_level(3)
def updateemployee():
    if request.method == 'POST':

        id = request.form["emp_id"]
        
        if 'update' in request.form:

            #error check to make sure all fields have data
            if not request.form['first_name'] or not request.form['last_name'] or not request.form['pps_number'] or not request.form['dob'] or not request.form['hire_date']:
                flash('Error: all fields are required')

                return render_template('updateemployee.html', titles = inventorydb.Title.query.all(),
                                                                                          employee=inventorydb.db.session.query(inventorydb.Employee.emp_id, inventorydb.Employee.first_name, inventorydb.Employee.last_name, inventorydb.Employee.pps_number, inventorydb.Employee.dob, inventorydb.Employee.hire_date                                                                                  
                                                                                         ,inventorydb.Title.job_title)
                                                                                         .outerjoin(inventorydb.EmployeeTitle, inventorydb.Employee.emp_id==inventorydb.EmployeeTitle.emp_title_id)
                                                                                         .outerjoin(inventorydb.Title, inventorydb.Title.job_title==inventorydb.EmployeeTitle.emp_job_title).filter(inventorydb.Employee.emp_id==id).all())
            
            #update employee useing user provided data
            else:

                employee=inventorydb.Employee.query.get(id)

                #get current job title entry (current because no end date)
                current_emp_title = inventorydb.EmployeeTitle.query.filter(inventorydb.EmployeeTitle.emp_title_id == employee.emp_id, inventorydb.EmployeeTitle.end_date == "").first()


                #check to see if the employees title has been updated (if the title on the form is not the same as the current title)
                if request.form['job_title'] != current_emp_title.emp_job_title:

                    #set the end date of the current title entry for the employee being updated to "today"
                    current_emp_title.end_date = date.today()

                    #get ALL titles that the employee being updated has had
                    all_emp_titles = inventorydb.EmployeeTitle.query.filter(inventorydb.EmployeeTitle.emp_title_id == employee.emp_id).all()

                    #set bool variable used to check if emp has already had job title previously
                    emp_title_already_exists = False;

                    #Check to see if the employe being updated has ever had the job title being updated to preivously
                    for title in all_emp_titles:
                        #if the employee has previous record of having the job title set 
                        if request.form['job_title'] == title.emp_job_title:
                            emp_title_already_exists = True
                            #store the actual title name of the title the employee previously held
                            existing_title = title.emp_job_title
                            break


                    if emp_title_already_exists == True:
                        inventorydb.EmployeeTitle.query.filter(inventorydb.EmployeeTitle.emp_title_id == employee.emp_id, inventorydb.EmployeeTitle.emp_job_title == existing_title).first().end_date = ""
                    else:
                    #add new job title
                        new_emp_title = inventorydb.EmployeeTitle(employee.emp_id, request.form['job_title'], date.today(), "")
                        inventorydb.db.session.add(new_emp_title)
                    
                #update employee info
                employee.first_name = request.form['first_name']
                employee.last_name = request.form['last_name']
                employee.pps_number = (request.form['pps_number'])
                employee.dob = (request.form['dob'])
                employee.hire_date = (request.form['hire_date'])

                inventorydb.db.session.commit()

                return redirect(url_for('viewemployee'))

        #user cancelled update
        else:
            return render_template('selectemployee.html', employees=inventorydb.Employee.query.all())

    return render_template('updateemployee.html')

#allow user to delete employee
@app.route('/deleteemployee', methods=['GET', 'POST'])
@login_required
@requires_access_level(3)
def deleteemployee():

    id = request.form["emp_id"]
    
    if request.method == 'POST':

        #user confirms wants to delete
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
        #user cancels delete
        else:
            return render_template('selectemployee.html', employees=inventorydb.Employee.query.all())

    return redirect(url_for('viewemployee', message='Employee successfully deleted'))
 
#allow user to view titles
@app.route('/viewtitles', methods=['GET', 'POST'])
@login_required
@requires_access_level(2)
def viewtitles():
    return render_template('viewtitles.html', query=inventorydb.Title.query.all())


#allow user to add titles
@app.route('/addtitle', methods=['GET', 'POST'])
@login_required
@requires_access_level(3)
def addtitle():
    if request.method =='POST':
        #ensure all information required is provided 
        if not request.form['job_title'] or not request.form['department'] or not request.form['access_level']:
            flash('Error: all fields are required')

        #add title if all info required given
        else:     
            title=inventorydb.Title(request.form['job_title'], request.form['department'], request.form['access_level'])
            inventorydb.db.session.add(title)
            inventorydb.db.session.commit()
            flash('Title successfully added')

    return render_template('addtitle.html')

#allows user to select titless 
@app.route('/selecttitle', methods=['GET', 'POST'])
@login_required
@requires_access_level(3)
def selecttitle():

    if request.method == 'POST':

        id = request.form["job_title"]

        #user selects to update the item
        if 'update' in request.form:
            return render_template('updatetitle.html', query=inventorydb.Title.query.get(id))

        #user selects to delete the item
        elif 'delete' in request.form:
            return render_template('deletetitle.html', query=inventorydb.Title.query.get(id))
    return render_template('selecttitle.html', titles=inventorydb.Title.query.all())

#allows user to update title
@app.route('/updatetitle', methods=['GET', 'POST'])
@login_required
@requires_access_level(3)
def updatetitle():
    if request.method == 'POST':

        id = request.form["job_title"]
        
        #user has selected to update
        if 'update' in request.form:

            #check to ensure all required info is given
            if not request.form['job_title'] or not request.form['department'] or not request.form['access_level']:
                flash('Error: all fields are required')

            #update title
            else:   
                title=inventorydb.Title.query.get(id)
        
                title.department = request.form['department']
                title.access_level = int(request.form['access_level'])

                inventorydb.db.session.commit()

                return redirect(url_for('viewtitles'))

        #cancel button selected
        else: 
            return render_template('selecttitle.html', titles=inventorydb.Title.query.all())

    return render_template('updatetitle.html', query=inventorydb.Title.query.get(id))


#allow user to delete title
@app.route('/deletetitle', methods=['GET', 'POST'])
@login_required
@requires_access_level(3)
def deletetitle():

    if request.method == 'POST':

        id = request.form['job_title']

        #user has selected to delete
        if 'delete' in request.form:

            try:
                inventorydb.db.session.delete(inventorydb.Title.query.filter_by(job_title=id).one())
                inventorydb.db.session.commit()
            except:
                flash('Error: Unable to delete the title')
                return render_template('deletetitle.html')
        
        #cancel was selected
        else: 
            return render_template('selecttitle.html', titles=inventorydb.Title.query.all())

    return redirect(url_for('viewtitles', message='Title successfully deleted'))



#allow user to view employee titles (table between titles & employees)
@app.route('/viewemployeetitles', methods=['GET', 'POST'])
@login_required
@requires_access_level(2)
def viewemployeetitles():
    return render_template('viewemployeetitles.html', query=inventorydb.EmployeeTitle.query.order_by(inventorydb.EmployeeTitle.emp_title_id).all())


#allow user to view suppliers
@app.route('/viewsuppliers', methods=['GET', 'POST'])
@login_required
@requires_access_level(1)
def viewsuppliers():
    return render_template('viewsuppliers.html', query=inventorydb.Supplier.query.all())


#allow user to add supplier
@app.route('/addsupplier', methods=['GET', 'POST'])
@login_required
@requires_access_level(2)
def addsupplier():
    if request.method == 'POST':

        #check all info is provided
        if not request.form['name'] or not request.form['phone'] or not request.form['email']:
            flash('Error: name, phone and email fields are required')

        #add supplier if all info present
        else:     
            supplier = inventorydb.Supplier(request.form['name'], request.form['phone'], request.form['email'], request.form['comments'])
            inventorydb.db.session.add(supplier)
            inventorydb.db.session.commit()
            flash('Supplier successfully added')

    return render_template('addsupplier.html')

#allow user to select a supplier
@app.route('/selectsupplier', methods=['GET', 'POST'])
@login_required
@requires_access_level(2)
def selectsupplier():

    if request.method == 'POST':

        id = request.form["supplier_id"]

        #update was selected by user
        if 'update' in request.form:
            return render_template('updatesupplier.html', query=inventorydb.Supplier.query.get(id))

        #delete was selected by user
        elif 'delete' in request.form:
            return render_template('deletesupplier.html', query=inventorydb.Supplier.query.get(id))

    return render_template('selectsupplier.html', suppliers=inventorydb.Supplier.query.all())

#allow user to update supplier
@app.route('/updatesupplier', methods=['GET', 'POST'])
@login_required
@requires_access_level(2)
def updatesupplier():
    if request.method == 'POST':

        id = request.form["supplier_id"]

        #user selected to update
        if 'update' in request.form:

            #error check all info required was given
            if not request.form['name'] or not request.form['phone'] or not request.form['email']:
                flash('Error: name, phone and email fields are required')

            #add supplier
            else:     
 
                supplier=inventorydb.Supplier.query.get(id)
        
                supplier.name = request.form['name']
                supplier.phone = request.form['phone']
                supplier.email = (request.form['email'])
                supplier.comments = (request.form['comments'])

                inventorydb.db.session.commit()

                return redirect(url_for('viewsuppliers'))

        #cancel button selected
        else: 
            return render_template('selectsupplier.html', suppliers=inventorydb.Supplier.query.all())

    return render_template('updatesupplier.html', query=inventorydb.Supplier.query.get(id))


#allow user to delete supplier
@app.route('/deletesupplier', methods=['GET', 'POST'])
@login_required
@requires_access_level(2)
def deletesupplier():
    if request.method == 'POST':
        id = request.form['supplier_id']

        #user selected delete
        if 'delete' in request.form:
            try:
                inventorydb.db.session.delete(inventorydb.Supplier.query.filter_by(supplier_id=id).one())
                inventorydb.db.session.commit()
            except:
                flash('Error: Unable to delete the supplier')
                return render_template('deletesupplier.html')
        #cancel was selected
        else: 
            return render_template('selectsupplier.html', suppliers=inventorydb.Supplier.query.all())

    return redirect(url_for('viewsuppliers', message='Supplier successfully deleted'))








#allow user to view categories
@app.route('/viewcategories', methods=['GET', 'POST'])
@login_required
@requires_access_level(1)
def viewcategories():
    return render_template('viewcategories.html', query=inventorydb.Category.query.all())


#allow user to add category
@app.route('/addcategory', methods=['GET', 'POST'])
@login_required
@requires_access_level(2)
def addcategory():
    if request.method == 'POST':
        #error check if all required info given by user
        if not request.form['name'] or not request.form['description']:
            flash('Error: all fields are required')

        #add category
        else:   
            category = inventorydb.Category(request.form['name'], request.form['description'])
            inventorydb.db.session.add(category)
            inventorydb.db.session.commit()
            flash('Supplier successfully added')

    return render_template('addcategory.html')

#allow user to delete category
@app.route('/deletecategory', methods=['GET', 'POST'])
@login_required
@requires_access_level(2)
def deletecategory():
    if request.method == 'POST':
        id = request.form['category_id']

        #user selected delete
        if 'delete' in request.form:

            try:
                inventorydb.db.session.delete(inventorydb.Category.query.filter_by(category_id=id).one())
                inventorydb.db.session.commit()
            except:
                flash("Error: Unable to delete category")
                return render_template('deletecategory.html')

        #cancel was selected
        else: 
            return render_template('selectcategory.html', categories=inventorydb.Category.query.all())

    return redirect(url_for('viewcategories', message='Category successfully deleted'))

#allow user to select a category
@app.route('/selectcategory', methods=['GET', 'POST'])
@login_required
@requires_access_level(2)
def selectcategory():

    if request.method == 'POST':

        id = request.form["category_id"]

        #if user chooses to update
        if 'update' in request.form:
            return render_template('updatecategory.html', query=inventorydb.Category.query.get(id))

        #user chooses to delete
        elif 'delete' in request.form:
            return render_template('deletecategory.html', query=inventorydb.Category.query.get(id))

    return render_template('selectcategory.html', categories=inventorydb.Category.query.all())

#allow user to update category
@app.route('/updatecategory', methods=['GET', 'POST'])
@login_required
@requires_access_level(2)
def updatecategory():
    if request.method == 'POST':
        id = request.form["category_id"]

        #user chooses to update
        if 'update' in request.form:
            #error check to ensure all details are provided
            if not request.form['name'] or not request.form['description']:
                flash('Error: all fields are required')

            #update category
            else:    
                category=inventorydb.Category.query.get(id)
        
                category.name = request.form['name']
                category.description = request.form['description']

                inventorydb.db.session.commit()

                return redirect(url_for('viewcategories'))

        #cancel button selected
        else: 
            return render_template('selectcategory.html', categories=inventorydb.Category.query.all())

    return render_template('updatecategory.html', query=inventorydb.Category.query.get(id))



if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT) #debug=True)
 




