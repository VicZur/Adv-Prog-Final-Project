import inventorydb
from inventorydb import db, app


def create_test_title():
    
    title1 = inventorydb.Title('Server','100', '1') 
    title2 = inventorydb.Title('Bartender','100', '1')
    title3 = inventorydb.Title('Supervisor','100', '2')
    title4 = inventorydb.Title('Bar Manager','100', '2')
    title5 = inventorydb.Title('Admin','300', '3')
    title6 = inventorydb.Title('Accounts','200', '2')

    titles = [title1, title2, title3, title4, title5, title6]

    for title in titles:
        if not inventorydb.Title.query.get(title.job_title):
            inventorydb.db.session.add(title)

    inventorydb.db.session.commit()



def create_test_employee():
    
    employee = inventorydb.Employee('Jane', 'Doe', '12345678A', '01-01-1990', '14-08-2022')

    inventorydb.db.session.add(employee)
    inventorydb.db.session.commit()


def test_job_title():
    jobtest = inventorydb.EmployeeTitle(1, 'Server', 14082022, '')

    inventorydb.db.session.add(jobtest)
    inventorydb.db.session.commit()


create_test_title()
#create_test_employee()
#test_job_title()

