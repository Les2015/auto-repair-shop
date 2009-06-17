from google.appengine.ext import db

class CustomerEnt(db.Model):
    """ Datastore model for Customer """
    first_name = db.StringProperty(verbose_name = "First Name", required=False)
    last_name = db.StringProperty(verbose_name = "Last Name", required=True)
    address1 = db.StringProperty(verbose_name = "Address 1", required=True)
    address2 = db.StringProperty(verbose_name = "Address 2", required=False)
    city = db.StringProperty(verbose_name = "City", required=True)
    state = db.StringProperty(verbose_name = "State", required=True)
    zip = db.StringProperty(verbose_name = "Zip", required=True)
    phone1 = db.StringProperty(verbose_name = "Primary Phone", required=True)
    phone2 = db.StringProperty(verbose_name = "Secondary Phone", required=False)
    email = db.StringProperty(verbose_name = "Email Address", required=False)
    comments = db.TextProperty(verbose_name = "Comments", required=False) 
    # these columns are for search only; user input for these fields are converted to all upper case for search
    first_name_search = db.StringProperty(required=False)
    last_name_search = db.StringProperty(required=False)

class VehicleEnt(db.Model):
    """ Datastore model for Vehicle """
    make = db.StringProperty(verbose_name = "Make", required=True)
    model = db.StringProperty(verbose_name = "Model", required=True)
    year = db.IntegerProperty(verbose_name = "Year", required=True)
    license = db.StringProperty(verbose_name = "License Plate Number", required=True)
    vin = db.StringProperty(verbose_name = "VIN", required=False)
    notes = db.TextProperty(verbose_name = "Other Characteristics", required=False) 
    customer = db.ReferenceProperty(CustomerEnt)

class WorkorderEnt(db.Model):
    """ Datastore model for Workorder """
    vehicle = db.ReferenceProperty(VehicleEnt)
    mileage = db.IntegerProperty(verbose_name = "Initial Mileage", required=True)
    status = db.IntegerProperty(verbose_name = "Work Order Status", required=True, choices=set([1,2,3]))
    date_created = db.DateTimeProperty(verbose_name = "Date Opened", required=True, auto_now_add=True)
    customer_request = db.TextProperty(verbose_name = "Customer Work Request", required=True) 
    mechanic =  db.StringProperty(verbose_name = "Responsible Mechanic", required =True)
    task_list = db.TextProperty(verbose_name = "Mechanic Task List", required=False)
    work_performed = db.TextProperty(verbose_name = "Mechanic Work Record", required=False)
    notes = db.TextProperty(verbose_name = "Mechanic Notes", required=False) 
    date_closed = db.DateTimeProperty(verbose_name = "Date Closed", required=False)
