from google.appengine.ext import db
from CustomerEnt import CustomerEnt

class VehicleEnt(db.Model):
    #vehicID = db.IntegerProperty(verbose_name = "Vehicle ID", required=True, indexed=True)
    make = db.StringProperty(verbose_name = "Make", required=True)
    model = db.StringProperty(verbose_name = "Model", required=True)
    # should it have validator=checkYr where this is a function?
    year = db.IntegerProperty(verbose_name = "Year", required=True)
    mileage = db.IntegerProperty(verbose_name = "Initial Mielage", required=True)
    license = db.StringProperty(verbose_name = "License Plate Number", required=True)
    vin = db.StringProperty(verbose_name = "VIN", required=False)
    #email = db.EmailProperty(verbose_name = "Email Address", required=False)
    notes = db.TextProperty(verbose_name = "Other Characteristics", required=False) 
    customer = db.ReferenceProperty(CustomerEnt)



