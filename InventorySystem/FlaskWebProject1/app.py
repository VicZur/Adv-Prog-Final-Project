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

        itemdate = request.form['expiration_date']
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

    return render_template('deleteitem.html')

if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)




