"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

import inventorydb
from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import datetime
app = Flask(__name__)

db = SQLAlchemy(app)


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
        item = inventorydb.Item(request.form['item_id'], request.form['name'], request.form['description'], request.form['unit_cost'], request.form['sale_price'], request.form['units_in_stock'], datetime.date(itemdate), request.form['supplier_id'], request.form['category_id'])

        db.session.add(item)
        db.session.commit()
        flash('Record was successfully added')

    return render_template('additem.html')



@app.route('/viewitem', methods=['GET', 'POST'])
def viewitem():
    return render_template('viewitem.html')


if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
