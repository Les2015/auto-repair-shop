'''
Created on May 27, 2009

@author: Brad Gaiser, Wing Wong

This module implements a set of light weight objects for carrying information
back and forth between the View and the Model.  As such, it has to have some
knowledge of the data requirements on both sides in order to minimize the
need for special code on each side for reformatting data to meet either the
requirements of the UI or of the Data Store.

2009-06-11 Implemented __eq__ for deep comparison of objects      Les Faby
2009-06-12 Changed design of wrapper objects to only hold string information
           at all times.  Allowing the View to work with the fields directly
           greatly simplifies the data handling in the template code.  bdg
'''

""" Wing, notice that I changed the Id value from None to -1 to indicate that
    the information has not been saved to the database.  I did this because
    I needed to save a value in hidden form fields to indicate that the current
    customer, vehicle, or work order form is being filled out for a new, or an
    existing item.  For new ones, I assume the value in the hidden form field
    will be -1, for existing ones being edited, I assume the hidden form field
    will hold the database id of the record being edited. -- bdg
"""
from datetime import *
from time import *
from Utilities import dateToString, myLog

    
###########################################################################################

class Customer(object):
    """ Light weight class for passing the customer data around. """
    def __init__(self, id="-1", first_name="", last_name="",
                 address1="", address2="", city="", state="", zip="",
                 phone1="", phone2="", email="", comments=""):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.address1 = address1
        self.address2 = address2
        self.city = city
        self.state = state
        self.zip = zip
        self.phone1 = phone1
        self.phone2 = phone2
        self.email = email
        self.comments = comments
    
    """ In general, I don't think we want to change the id of an object once it is created.
        From the DataStore's perspective, it's not allowed. -- Wing
    """
    def setId(self, id):
        """ Save the primary key into object. """
        self.id = id    
    
    def getId(self):
        """ Retrieve primary customer key. """
        return self.id
    
    def loadFromDictionary(self, dictionary):
        """ Load values from dictionary passed over from the view. """
        self.setId(dictionary['customer_id'])   
        self.first_name = dictionary['first_name']
        self.last_name = dictionary['last_name']
        self.address1 = dictionary['address1']
        self.address2 = dictionary['address2']
        self.city = dictionary['city']
        self.state = dictionary['state']
        self.zip = dictionary['zip']
        self.phone1 = dictionary['phone1']
        self.phone2 = dictionary['phone2']
        self.email = dictionary['email']

        # The 'comments' field is not available when searching.
        # Another choice here would be to hide the comments field
        # in search mode so this if statement wouldn't be needed.
        if 'comments' in dictionary.keys():
            self.comments = dictionary['comments']
            
        return None
    
    def __str__(self):
        return "customer ID " + str(self.id) + ":\n" + \
                "\tfirst_name = " + self.first_name + "\n" + \
                "\tlast_name = " + self.last_name + "\n" + \
                "\taddress1 = " + self.address1 + "\n" + \
                "\taddress2 = " + self.address2 + "\n" + \
                "\tcity = " + self.city + "\n" + \
                "\tstate = " + self.state + "\n" + \
                "\tzip = " + self.zip + "\n" + \
                "\tphone1 = " + self.phone1 + "\n" + \
                "\tphone2 = " + self.phone2 + "\n" + \
                "\temail = " + self.email + "\n" + \
                "\tcomments = " + self.comments + "\n"            
    
    def __eq__(self, other):
        '''
        Overload the == operator to do a field-by-field comparison of self
        with an other instance of the same class.
        Assumes the compared object is of the same type and that
        the class does not have any composite objects so that
        2 attributes can be compared using "=="
        '''
        for a in self.__dict__:
            if (getattr(self,a) != getattr(other,a)):
                return False 
        return True

    def __ne__(self, other):
        """ Overload the != operator to do a field-by-field comparison of self
            with an other instance of the same class. See __eq__ for more details"""
        return not self.__eq__(other)
    
###########################################################################################
    
    
class Vehicle(object):
    """ Light weight class for passing the vehicle data around. """
    def __init__(self, id="-1", customer_id="", make="", model="",
                 year="", license="", vin="", notes=""):
        self.id = id
        self.customer_id = customer_id
        self.make = make
        self.model = model
        self.year = year
        self.license = license
        self.vin = vin
        self.notes = notes
    
    """ Getters & setters go next. """
    
    def setId(self, id):
        """ Save the primary key into object. """
        self.id = id
        
    def getId(self):
        """ Retrieve the vehicle primary key from object. """
        return self.id
    
    def setCustomerId(self, id):
        """ Save the customer foreign key in vehicle object. """
        self.customer_id = id
        
    def getCustomerId(self):
        """ Retrieve the customer foreign key from object. """
        return self.customer_id
    
    def loadFromDictionary(self, dictionary):
        """ Load values from dictionary passed over from the view. 
            Data authentication is being done on client side with
            javascript.
        """
        self.setId(dictionary['vehicle_id'])
        self.setCustomerId(dictionary['customer_id'])
        self.make = dictionary['make']
        self.model = dictionary['model']
        self.year = dictionary['year']
        self.license = dictionary['license']
        self.vin = dictionary['vin']
        self.notes = dictionary['notes']
            
        return None

    def __str__(self):
        return "vehicle ID " + str(self.id) + ":\n" + \
                "\tmake = " + self.make + "\n" + \
                "\tmodel = " + self.model + "\n" + \
                "\tyear = " + str(self.year) + "\n" + \
                "\tlicense = " + self.license + "\n" + \
                "\tvin = " + self.vin + "\n" + \
                "\tnotes = " + self.notes + "\n" + \
                "\tcustomer_id = " + self.customer_id + "\n"            

 
    def __eq__(self, other):
        '''
        Overload the == operator to do a field-by-field comparison of self
        with an other instance of the same class.
        Assumes the compared object is of the same type and that
        the class does not have any composite objects so that
        2 attributes can be compared using "=="
        '''
        for a in self.__dict__:
            if (getattr(self,a) != getattr(other,a)):
                return False 
        return True

    def __ne__(self, other):
        """ Overload the != operator to do a field-by-field comparison of self
            with an other instance of the same class. See __eq__ for more details"""
        return not self.__eq__(other)
    
  
    
###########################################################################################
    
class Workorder(object):
    """ Light weight class for passing the workorder data around. """
    
    OPEN = 1; COMPLETED = 2; CLOSED = 3
    _status_map = { 'open':OPEN, 'completed':COMPLETED, 'closed':CLOSED }
    DATE_FORMAT = "%b %d, %Y  %H:%M:%S"
    NO_MECHANIC = "NO_MECHANIC"
    
    def __init__(self, id="-1", vehicle_id="", mileage="",
                 status=OPEN, date_created="", customer_request="",
                 mechanic="", task_list="", work_performed="",
                 notes="", date_closed=""):
        self.id = id
        self.vehicle_id = vehicle_id
        self.mileage = mileage
        self.status = status
        self.customer_request = customer_request
        self.mechanic = mechanic 
        self.task_list = task_list 
        self.work_performed = work_performed
        self.notes = notes 
        self.date_created = date_created
        self.date_closed = date_closed
       	return None
    
    """ Getters & setters go next. """
    
    def setId(self, id):
        """ Save the workorder primary key in object. """
        self.id = id
        
    def getId(self):
        """ Retrieve the workorder primary key from object. """
        return self.id
    
    def setVehicleId(self, id):
        """ Save the vehicle foreign key in object. """
        self.vehicle_id = id
        
    def getVehicleId(self):
        """ Retrieve the vehicle foreign key from object. """
        return self.vehicle_id
    
    def setDateCreated(self):
        """ Trigger the setting of the date_created field for this object. 
            Dates (like all fields) are saved in this object as strings. 
        """
        self.date_created = dateToString(datetime.fromtimestamp(time()))
        
    def getDateCreated(self):
        """ Retrieve the date_created string value. """
        return self.date_created
    
    def setDateClosed(self):
        """ Trigger the setting of the date_closed field for this object. 
            Dates (like all fields) are saved in this object as strings. 
        """
        self.date_closed = dateToString(datetime.fromtimestamp(time()))
        
    def getDateClosed(self):
        """ Retrieve the date_closed string value. """
        return self.date_closed
    
    def loadFromDictionary(self, dictionary):
        """ Load values from dictionary passed over from the view. 
            Data authentication is being done on client side with
            javascript.
        """
        self.setId(dictionary['workorder_id'])
        self.setVehicleId(dictionary['vehicle_id'])
        self.customer_request = dictionary['customer_request']
        self.mileage = dictionary['mileage']
        self.date_created = dictionary['date_created']
        self.date_closed = dictionary['date_closed']
        mechanic = dictionary['mechanic']
        if mechanic == Workorder.NO_MECHANIC:
            self.mechanic = None
        else:
            self.mechanic = dictionary['mechanic']
        self.status = self._status_map[dictionary['status'].lower()]
        self.task_list = dictionary['task_list'] 
        self.work_performed = dictionary['work_performed']
        self.notes = dictionary['notes'] 
        
        return None
    
    def __eq__(self, other):
        '''
        Overload the == operator to do a field-by-field comparison of self
        with an other instance of the same class.
        Assumes the compared object is of the same type and that
        the class does not have any composite objects so that
        2 attributes can be compared using "=="
        '''
        for a in self.__dict__:
            if (getattr(self,a) != getattr(other,a)):
                myLog.write(">>>> %s: %s != %s" % (a, getattr(self,a), getattr(other,a)))
                return False 
        return True

    def __ne__(self, other):
        """ Overload the != operator to do a field-by-field comparison of self
            with an other instance of the same class. See __eq__ for more details"""
        return not self.__eq__(other)
    