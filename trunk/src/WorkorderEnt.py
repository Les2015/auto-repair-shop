from google.appengine.ext import db
from VehicleEnt import VehicleEnt

class SubTask:
    def __init__(self, task):
        self.task = task
        # valid values are "TO-DO", "DONE"
        self.status = "TO-DO"

class WorkorderEnt(db.Model):
    #orderID = db.IntegerProperty(verbose_name = "Work Order ID", required=True, indexed=True)
    vehicle = db.ReferenceProperty(VehicleEnt)
    # could  have validator=checkMileage where this is a function?
    mileage = db.IntegerProperty(verbose_name = "Initial Mileage", required=True)
    status = db.IntegerProperty(verbose_name = "Work Order Status", required=True, choices=set([1,2,3]))
    date_created = db.DateTimeProperty(verbose_name = "Date Opened", required=True, auto_now_add=True)
    customer_request = db.TextProperty(verbose_name = "Customer Work Request", required=True) 
    mechanic =  db.StringProperty(verbose_name = "Responsible Mechanic", required =True)
    #subTasks = db.ListProperty(SubTask, required=False)
    task_list = db.TextProperty(verbose_name = "Mechanic Task List", required=False)
    work_performed = db.TextProperty(verbose_name = "Mechanic Work Record", required=False)
    notes = db.TextProperty(verbose_name = "Mechanic Notes", required=False) 
    date_closed = db.DateTimeProperty(verbose_name = "Date Closed", required=False)
 
  

