'''
Created on May 27, 2009

@author: 
'''

""" Wing, notice that I changed the Id value from None to -1 to indicate that
    the information has not been saved to the database.  I did this because
    I needed to save a value in hidden form fields to indicate that the current
    customer, vehicle, or work order form is being filled out for a new, or an
    existing item.  For new ones, I assume the value in the hidden form field
    will be -1, for existing ones being edited, I assume the hidden form field
    will hold the database id of the record being edited. -- bdg
"""

import time

class Customer(object):
    def __init__(self, id=-1, first_name="", last_name="",
                 address1="", address2="", city="", state="", zip="",
                 phone1="", phone2="", email="", comments=""):
        self.__id = id
        self.__firstName = first_name
        self.__lastName = last_name
        self.__address1 = address1
        self.__address2 = address2
        self.__city = city
        self.__state = state
        self.__zip = zip
        self.__phone1 = phone1
        self.__phone2 = phone2
        self.__email = email
        self.__comments = comments
        return None
    
    def setId(self, id):
        self.__id = id
        
    def getId(self):
        return self.__id
    
    def setFirstName(self, first_name):
        self.__firstName = first_name
        
    def getFirstName(self):
        return self.__firstName
    
    def setLastname(self, last_name):
        self.__lastName = last_name
        
    def getLastName(self):
        return self.__lastName
    
    def setComments(self, comments):
        self.__comments = comments
        
    def getComments(self):
        return self.__comments
    
    def loadFromDictionary(self, dictionary):
        """ Load values from dictionary passed over from the view.
            Data authentication is being done on client side with
            javascript.
        """
        customer_id = dictionary['customer_id']
        if customer_id == -1:
            self.setId(None)
        else:
            self.setId(customer_id)
            
        self.setFirstName(dictionary['first_name'])
        self.setLastname(dictionary['last_name'])
        # The 'comments' field is not available when searching.
        # Another choice here would be to hide the comments field
        # in search mode so this if statement wouldn't be needed.
        if 'comments' in dictionary.keys():
            self.setComments(dictionary['comments'])
        return None
    
    def __eq__(self, testCustomer):
        """ Overload the == operator to do a field-by-field comparison of self
            against testCustomer """
        return self.__firstName == testCustomer.getFirstName() and \
               self.__lastName  == testCustomer.getLastName() # and etc., etc.
    
    def __ne__(self, testCustomer):
        """ Overload the != operator to do a field-by-field comparison of self
            to testCustomer """
        return not self.__eq__(testCustomer)
    
    
class Vehicle(object):
    def __init__(self, id=-1, customer_id=None, make=None, model=None,
                 year=None, mileage=None, license=None, vin=None, notes=None):
        self.__id = id
        self.__customerId = customer_id
        self.__make = make
        self.__model = model
        self.__year = year
        self.__currentMileage = mileage
        self.__licensePlate = license
        self.__vin = vin
        self.__notes = notes
        return None
    
    """ Getters & setters go next. """
    
    def setId(self, id):
        self.__id = id
        
    def getId(self):
        return self.__id
    
    def setCustomerId(self, id):
        self.__customerId = id
        
    def getCustomerId(self):
        return self.__customerId
    
    def loadFromDictionary(self, dictionary):
        """ Load values from dictionary passed over from the view. 
            Data authentication is being done on client side with
            javascript.
        """
        # Load fields similarly to method sketched out in Customer class
        vehicle_id = dictionary['vehicle_id']
        if vehicle_id == -1:
            self.setId(None)
        else:
            self.setId(vehicle_id)
            
        return None

    def __eq__(self, testVehicle):
        """ Overload the == operator to do a field-by-field comparison of self
            against testVehicle """
        return True
    
    def __ne__(self, testVehicle):
        """ Overload the != operator to do a field-by-field comparison of self
            to testVehicle """
        return not self.__eq__(testVehicle)
    
    
class Workorder(object):
    def __init__(self, id=-1, vehicle_id=None, mileage=None, 
                 date_created=None, date_closed=None, etc=None):
        self.__id = id
        self.__vehicleId = vehicle_id
        self.__mileage = mileage
        self.__status = Workorder.OPEN
        self.__dateCreated = date_created
        self.__dateClosed = date_closed
        return None
    
    OPEN = 1
    COMPLETED = 2
    CLOSED = 3
    
    """ Getters & setters go next. """
    
    def setId(self, id):
        self.__id = id
        
    def getId(self):
        return self.__id
    
    def setVehicleId(self, id):
        self.__vehicleId = id
        
    def getVehicleId(self):
        return self.__vehicleId
    
    def setDateCreated(self):
        self.__dateCreated = time.time()
        
    def getDateCreated(self):
        """ Do we want to format this as a string or return it as a date/time type? """
        return self.__dateCreated
    
    def setDateClosed(self):
        self.__dateClosed = time.time()
        
    def getDateClosed(self):
        """ Do we want to format this as a string or return it as a date/time type? """
        return self.__dateClosed
    
    def loadFromDictionary(self, dictionary):
        """ Load values from dictionary passed over from the view. 
            Data authentication is being done on client side with
            javascript.
        """
        # Load fields similarly to method sketched out in Customer class
        vehicle_id = dictionary['vehicle_id']
        if vehicle_id == -1:
            self.setId(None)
        else:
            self.setId(vehicle_id)
            
        return None
    
    def checkRequiredFieldsForCurrentState(self):
        """ Checks that the work order has all of the fields needed when
            work order is to be saved to database for the given internal
            status.  This should only report errors that are beyond the
            ones reported by MaintAppModel.validateWorkorderInfo().
        """
        if self.__status == Workorder.COMPLETED or self.__status == Workorder.CLOSED:
            # Check the final required fields for the work order and
            # generate list.
            retVal=[('task_list', 'required')]
        else:
            # In the open state, the database validation is sufficient so this
            # routine does not need to generate additional errors.
            retVal = []
        return retVal
    
    def __eq__(self, testWO):
        """ Overload the == operator to do a field-by-field comparison of self
            against testWO """
        return True
    
    def __ne__(self, testWO):
        """ Overload the != operator to do a field-by-field comparison of self
            to testWO """
        return not self.__eq__(testWO)
