import inventorydb
from inventorydb import db, app
from flask import Flask, request, flash, url_for, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
import datetime

if __name__ == '__main__':
    db.create_all
    db.init_app(app)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app


@app.route('/')
def index():
    return render_template('index.html')









@app.route('/additem', methods=['GET', 'POST'])
def additem():

    if request.method == 'POST':
    #  if not request.form['name'] or not request.form['salary'] or not request.form['age']:
    #     flash('Please enter all the fields', 'error')
    # else:

        item = inventorydb.Item(int(request.form['item_id']), request.form['name'], request.form['description'], int(request.form['unit_cost']), int(request.form['sale_price']), int(request.form['units_in_stock']), request.form['expiration_date'], int(request.form['supplier_id']), int(request.form['category_id']))


        inventorydb.db.session.add(item)
        inventorydb.db.session.commit()
  #      flash('Record was successfully added')

    return render_template('additem.html')



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


@app.route('/searchitem', methods=['GET', 'POST'])
def searchitem():

    if request.method == 'POST':
        id = request.form["item_id"]
        return render_template('updateitem.html', query=inventorydb.Item.query.get(id))#filter_by(item_id=id).one())

    return render_template('searchitem.html')



@app.route('/updateitem', methods=['GET', 'POST'])
def updateitem():
    if request.method == 'POST':

        #item=inventorydb.Item.query.get(5)

        id = request.form["item_id"]
        item=inventorydb.Item.query.get(id)
        
        item.name = request.form['name']
        item.description = request.form['description']
        item.unit_cost = int(request.form['unit_cost'])
        item.sale_price = int(request.form['sale_price'])
        item.units_in_stock = int(request.form['units_in_stock'])
        item.expiration_date = request.form['expiration_date']
        item.supplier_id = int(request.form['supplier_id'])
        item.category_id = int(request.form['category_id'])

        inventorydb.db.session.commit()

        return render_template('viewitem.html')

    return render_template('updateitem.html')


















@app.route('/addemployee', methods=['GET', 'POST'])
def addemployee():

    if request.method == 'POST':
    #  if not request.form['name'] or not request.form['salary'] or not request.form['age']:
    #     flash('Please enter all the fields', 'error')
    # else:

        employee = inventorydb.Employee(int(request.form['emp_id']), request.form['first_name'], request.form['last_name'], request.form['pps_number'], request.form['dob'], request.form['hire_date'])

        inventorydb.db.session.add(employee)
        inventorydb.db.session.commit()
  #      flash('Record was successfully added')

    return render_template('addemployee.html')


@app.route('/viewemployee', methods=['GET', 'POST'])
def viewemployee():

    return render_template('viewemployee.html', query=inventorydb.Employee.query.all())


@app.route('/deleteemployee', methods=['GET', 'POST'])
def deleteemployee():

    if request.method == 'POST':
        id = request.form["emp_id"]
    
        inventorydb.db.session.delete(inventorydb.Employee.query.filter_by(emp_id=id).one())
        inventorydb.db.session.commit()

    return render_template('deleteemployee.html')












if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)




