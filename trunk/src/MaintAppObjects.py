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
        return self.first_name
    
    def setLastname(self, last_name):
        self.last_name = last_name
        
    def getLastName(self):
        return self.last_name
    
    def setComments(self, comments):
        self.comments = comments
        
    def getComments(self):
        return self.comments
    
    def loadFromDictionary(self, dictionary):
        """ Load values from dictionary passed over from the view. """
        customer_id = dictionary['customer_id']
        if customer_id == '-1':
            self.setId(None)
        else:
            self.setId(customer_id)
            
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
    
    def __eq__(self, testCustomer):
        """ Overload the == operator to do a field-by-field comparison of self
            against testCustomer """
        return self.firstName == testCustomer.firstName and \
               self.lastName  == testCustomer.lastName # and etc., etc.
    
    def __ne__(self, testCustomer):
        """ Overload the != operator to do a field-by-field comparison of self
            to testCustomer """
        return not self.__eq__(testCustomer)
    
    
class Vehicle(object):
    def __init__(self, id="-1", customer_id=None, make=None, model=None,
                 year=None, license=None, vin=None, notes=None):
        self.id = id
        self.customer_id = customer_id
        self.make = make
        self.model = model
        self.year = year
        #self.mileage = mileage
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
        vehicle_id = dictionary['vehicle_id']
        if vehicle_id == '-1':
            self.setId(None)
        else:
            self.setId(vehicle_id)
            
        self.make = dictionary['make']
        self.model = dictionary['model']
        self.year = int(dictionary['year'])
        #self.mileage = int(dictionary['mileage'])
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

    def __eq__(self, testVehicle):
        """ Overload the == operator to do a field-by-field comparison of self
            against testVehicle """
        return True
    
    def __ne__(self, testVehicle):
        """ Overload the != operator to do a field-by-field comparison of self
            to testVehicle """
        return not self.__eq__(testVehicle)
    
    
class Workorder(object):
    def __init__(self, id="-1", vehicle_id=None, mileage=None, 
                 date_created=None, date_closed=None, etc=None):
        self.id = id
        self.vehicle_id = vehicle_id
        self.mileage = mileage
        self.status = Workorder.OPEN
        self.date_created = date_created
        self.date_closed = date_closed
        return None
    
    OPEN = 1
    COMPLETED = 2
    CLOSED = 3
    
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
        self.date_created = time.time()
        
    def getDateCreated(self):
        """ Do we want to format this as a string or return it as a date/time type? """
        return self.date_created
    
    def setDateClosed(self):
        self.date_closed = time.time()
        
    def getDateClosed(self):
        """ Do we want to format this as a string or return it as a date/time type? """
        return self.date_closed
    
    def loadFromDictionary(self, dictionary):
        """ Load values from dictionary passed over from the view. 
            Data authentication is being done on client side with
            javascript.
        """
        # Load fields similarly to method sketched out in Customer class
        vehicle_id = dictionary['vehicle_id']
        if vehicle_id == '-1':
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
