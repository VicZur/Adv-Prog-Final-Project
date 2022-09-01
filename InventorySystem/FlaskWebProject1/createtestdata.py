import inventorydb
from inventorydb import db, app


def create_test_suppliers():

    suppliers = [inventorydb.Supplier('Test Supplier', '1234567890', 'testsupplier@supplies.ie', '')
                , inventorydb.Supplier('Supplies R Us', '555-0123-5555', 'supplies@supplies.ie', 'Contact by phone only')
                , inventorydb.Supplier('RestaurantStuff', '9876543210', 'reststuff@stuff.ie', '')]

    for supplier in suppliers:
        inventorydb.db.session.add(supplier)

    inventorydb.db.session.commit()
    

def create_test_categories():

    categories = [inventorydb.Category('Beer Draft', 'Alcoholic beer by keg')
                 , inventorydb.Category('Beer Btl', 'Alcoholic beer in bottles')
                 , inventorydb.Category('Misc. Draft', 'Non-beer items by keg')
                 , inventorydb.Category('Wine', 'Wine bottles any size')
                 , inventorydb.Category('Misc Alc Btls', 'Other bottled Alcoholic beverage')
                 , inventorydb.Category('Non-alc beer', 'Non-alcoholic beer in btl or keg')
                 , inventorydb.Category('Soft drink btl', 'Bottles of juice, coke, sprite, to be sold by bottle')
                 , inventorydb.Category('Soft drink bulk', 'Non-alch drinks in larger bottles, not sold individually')
                 , inventorydb.Category('Fruit', 'Fresh Fruit')
                 , inventorydb.Category('Syrups', 'Any syrups made or bought')
                 , inventorydb.Category('Garnish', 'Any item specifically used as garnish')
                 , inventorydb.Category('Misc', 'Any other item in stock')]

    for cat in categories:
        inventorydb.db.session.add(cat)

    inventorydb.db.session.commit()


def create_test_title():

    titles = [inventorydb.Title('Server','Floor', '1') 
             , inventorydb.Title('Bartender','Floor', '1')
             , inventorydb.Title('Supervisor','Floor', '2')
             , inventorydb.Title('Bar Manager','Floor', '2')
             , inventorydb.Title('Admin','Admin', '3')
             , inventorydb.Title('Payroll Specialist','Accounting', '2')]

    for title in titles:
        if not inventorydb.Title.query.get(title.job_title):
            inventorydb.db.session.add(title)

    inventorydb.db.session.commit()



def create_test_employee():
   
    employee1 = inventorydb.Employee('Admin', 'Admin', '111000222B', '08-08-1988', '08-08-2022','Admin')
    employee_title = inventorydb.EmployeeTitle(1, 'Admin', '08-08-2022', '')

    inventorydb.db.session.add(employee1)
    inventorydb.db.session.add(employee_title)
    inventorydb.db.session.commit()



#create_test_title()
#create_test_employee()
#create_test_suppliers()
#create_test_categories()
