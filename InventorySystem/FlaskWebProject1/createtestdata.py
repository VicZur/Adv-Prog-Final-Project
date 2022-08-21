import inventorydb
from inventorydb import db, app


def create_test_suppliers():

    suppliers = [inventorydb.Supplier('Test Supplier', '1234567890', 'testsupplier@supplies.ie', '')
                , inventorydb.Supplier('Supplies R Us', '555-0123-5555', 'supplies@supplies.ie', 'Contact by phone only')
                , inventorydb.Supplier('RestaurantStuff', '9876543210', 'reststuff@stuff.ie', '')]

    for supplier in suppliers:
        #if not inventorydb.Supplier.query.filter_by(name=supplier).one(): #check for duplication of name for testing purposes only to ensure not continuously adding the same suppliers every time program is run
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
    
    #employees = [inventorydb.Employee('Jane', 'Doe', '12345678A', '01-01-1990', '14-08-2022', 'Server')
    #            , inventorydb.Employee('John', 'Doe', '987654321B', '08-01-1988', '14-08-2022', 'Supervisor')
    #            , inventorydb.Employee('TestAdmin', 'TestAdmin', '111222333C', '05-05-1995', '14-08-2022', 'Admin')]

    #for employee in employees:
    #    inventorydb.db.session.add(employee)
    
    employee = inventorydb.Employee('Jane', 'Doe', '12345678A', '01-01-1990', '14-08-2022', 'Supervisor')
    inventorydb.db.session.add(employee)
    inventorydb.db.session.commit()



#create_test_title()
#create_test_employee()
#create_test_suppliers()
#create_test_categories()
