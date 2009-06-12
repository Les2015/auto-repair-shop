'''
Created on May 27, 2009

@author: Brad Gaiser, Wing Wong

This module implements a set of light weight objects for carrying information
back and forth between the View and the Model.  As such, it has to have some
knowledge of the data requirements on both sides in order to minimize the
need for special code on each side for reformatting data to meet either the
requirements of the UI or of the Data Store.
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

def nz(value):
	return ("" if value is None else value)
    
###########################################################################################

class Customer(object):
    """ Light weight class for passing the customer data around. """
    def __init__(self, id="-1", first_name=None, last_name=None,
                 address1=None, address2=None, city=None, state=None, zip=None,
                 phone1=None, phone2=None, email=None, comments=None):
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
        self.id = id    
    
    def getId(self):
        return self.id
    
    def setFirstName(self, first_name):
        self.first_name = first_name
        
    def getFirstName(self):
        return nz(self.first_name)
    
    def setLastname(self, last_name):
        self.last_name = last_name
        
    def getLastName(self):
        return nz(self.last_name)
    
    def setComments(self, comments):
        self.comments = comments
        
    def getComments(self):
        return nz(self.comments)
    
    def loadFromDictionary(self, dictionary):
        """ Load values from dictionary passed over from the view. """
        #customer_id = dictionary['customer_id']
        #if customer_id == '-1':
        #    self.setId(None)
        #else:
        #    self.setId(customer_id)
        
        self.setId(dictionary['customer_id'])   
        self.setFirstName(dictionary['first_name'])
        self.setLastname(dictionary['last_name'])
        self.address1 = dictionary['address1']
        self.city = dictionary['city']
        self.state = dictionary['state']
        self.zip = dictionary['zip']
        self.phone1 = dictionary['phone1']

        # The 'comments' field is not available when searching.
        # Another choice here would be to hide the comments field
        # in search mode so this if statement wouldn't be needed.
        if 'comments' in dictionary.keys():
            self.setComments(dictionary['comments'])
            
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
            if (nz(getattr(self,a)) != nz(getattr(other,a))):
                return False 
        return True

    def __ne__(self, other):
        """ Overload the != operator to do a field-by-field comparison of self
            with an other instance of the same class. See __eq__ for more details"""
        return not self.__eq__(other)
    
###########################################################################################
    
    
class Vehicle(object):
    """ Light weight class for passing the vehicle data around. """
    def __init__(self, id="-1", customer_id=None, make=None, model=None,
                 year=None, license=None, vin=None, notes=None):
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
        self.id = id
        
    def getId(self):
        return self.id
    
    def setCustomerId(self, id):
        self.customer_id = id
        
    def getCustomerId(self):
        return self.customer_id
    
    def loadFromDictionary(self, dictionary):
        """ Load values from dictionary passed over from the view. 
            Data authentication is being done on client side with
            javascript.
        """
        # Load fields similarly to method sketched out in Customer class
        #vehicle_id = dictionary['vehicle_id']
        #if vehicle_id == '-1':
        #    self.setId(None)
        #else:
        #    self.setId(vehicle_id)
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
            if (nz(getattr(self,a)) != nz(getattr(other,a))):
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
    
    def __init__(self, id="-1", vehicle_id=None, mileage=None,
                 status=OPEN, date_created=None, customer_request=None,
                 mechanic=None, task_list=None, work_performed=None,
                 notes=None, date_closed=None):
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
        self.id = id
        
    def getId(self):
        return self.id
    
    def setVehicleId(self, id):
        self.vehicle_id = id
        
    def getVehicleId(self):
        return self.vehicle_id
    
    def setDateCreated(self):
        self.date_created = \
            datetime.fromtimestamp(time())
        
    def getDateCreated(self):
        """ Do we want to format this as a string or return it as a date/time type? """
        if self.date_created == None:
            return None
        else:
            return self.date_created.strftime(Workorder.DATE_FORMAT)
    
    def setDateClosed(self):
        self.date_closed = \
            datetime.fromtimestamp(time())
        
    def getDateClosed(self):
        """ Do we want to format this as a string or return it as a date/time type? """
        if self.date_closed == None:
            return None
        else:
            return self.date_closed.strftime(Workorder.DATE_FORMAT)
    
    def loadFromDictionary(self, dictionary):
        """ Load values from dictionary passed over from the view. 
            Data authentication is being done on client side with
            javascript.
        """
        # Load fields similarly to method sketched out in Customer class
        #workorder_id = dictionary['workorder_id']
        #if workorder_id == '-1':
        #    self.setId(None)
        #else:
        #    self.setId(workorder_id)

        #vehicle_id = dictionary['vehicle_id']
        #if vehicle_id == '-1':
        #    self.setVehicleId(None)
        #else:
        #    self.setVehicleId(vehicle_id)
        self.setId(dictionary['workorder_id'])
        self.setVehicleId(dictionary['vehicle_id'])
        self.customer_request = dictionary['customer_request']
        self.mileage = dictionary['mileage']
        strDate = dictionary['date_created']
        if strDate == "":
            self.date_created = None
        else:
            self.date_created = \
                datetime.strptime(strDate, Workorder.DATE_FORMAT)
        strDate = dictionary['date_closed']
        if strDate == "":
            self.date_closed = None
        else:
            self.date_closed = \
                datetime.strptime(strDate, Workorder.DATE_FORMAT)
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
    
    def checkRequiredFieldsForCurrentState(self):
        """ Checks that the work order has all of the fields needed when
            work order is to be saved to database for the given internal
            status.  This should only report errors that are beyond the
            ones reported by MaintAppModel.validateWorkorderInfo().
        """
        if self.status == Workorder.COMPLETED or self.status == Workorder.CLOSED:
            # Check the final required fields for the work order and
            # generate list.
            retVal=[]
        else:
            # In the open state, the database validation is sufficient so this
            # routine does not need to generate additional errors.
            retVal = []
        return retVal
    
     
    def __eq__(self, other):
        '''
        Overload the == operator to do a field-by-field comparison of self
        with an other instance of the same class.
        Assumes the compared object is of the same type and that
        the class does not have any composite objects so that
        2 attributes can be compared using "=="
        '''
        for a in self.__dict__:
            if (nz(getattr(self,a)) != nz(getattr(other,a))):
                return False 
        return True

    def __ne__(self, other):
        """ Overload the != operator to do a field-by-field comparison of self
            with an other instance of the same class. See __eq__ for more details"""
        return not self.__eq__(other)
    