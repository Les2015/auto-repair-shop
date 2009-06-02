'''
Created on May 27, 2009

@author: 
'''

from MaintAppObjects import Customer, Vehicle, Workorder

class MaintAppModel(object):
    def __init__(self):
        return None
    
    def initialize(self):
        """ Set up the connection.  This is being done as a means of controlling
            the timing of the creation of the instance vs. the connection to the
            database.  This app may not need this level of control, but it is
            available in the event there are timing issues between the setup of
            the UI and the setup of the database.
        """
        pass
    
    def saveCustomerInfo(self, customer):
        """ Write customer object to data store.  If id in customer is None,
            create the record; otherwise, update the record.  Return the 
            primary key of the customer (the new one if creating, the existing
            one if updating.)
        """
        return 24
    
    def getCustomer(self, customer_id):
        """ Retrieve the customer record from the database whose primary key
            is the customer_id passed in.
        """
        return Customer(id=customer_id, first_name="Wing", last_name="Wong")
    
    def saveVehicleInfo(self, vehicle):
        """ Write vehicle object to data store.  If id in vehicle object is
            -1, create the record; otherwise, update the existing record
            in the database.  Return primary key of the vehicle.
        """
        return 10344
    
    def getVehicle(self, vehicle_id):
        """ Retrieve the vehicle record from the database whose primary key
            is the vehicle_id passed in.
        """
        return Vehicle(id="10344", make="Honda", modle="Civic", year=1993)
    
    def getVehicleList(self, customer_id):
        """ This method queries the database for vehicles records belonging
            to the customer identified by customer_id. Return an empty list
            if no vehicles are found.
        """
        return [Vehicle(id="10344", make="Honda", model="Civic", year=1993),
                Vehicle(id="10346", make="Toyota", model="Tercel", year=2002)]
    
    def searchForMatchingCustomers(self, searchCriteria):
        """ The model forms a query based on AND logic for the various
            fields that have been entered into the searchCriteria object.
            The searchCriteria object is an instance of the Customer class.
            For now we will assume exact matches:
                e.g., 'SELECT .... WHERE (customer_table.first_name=%d)' %
                                                searchCriteria.getFirstName()
            In the future we may consider supporting wild card matching.
            A list of Customer objects corresponding to the customer records
            that were retrieved are returned to the caller.
        """
        return []
    
    def saveWorkorder(self, workorder):
        """ Write contents of workorder object to data store.  If id in workorder
            object is -1, create the record; otherwise, update the existing record
            in the database.  Return primary key of the workorder.
        """
        return 10344
    
    def getWorkorder(self, workorder_id):
        """ Return the workorder record whose id is given by the workorder_id
            parameter.
        """
        return Workorder(id=workorder_id)
    
    def getWorkorderList(self, vehicle_id):
        """ Return the list of workorders belonging to the vehicle identified
            by vehicle_id.  Return an empty list if no workorders are found.
        """
        return []
    
    def getOpenWorkorders(self):
        """ Query the database for all work orders where the work order status
            is 'open'.  Also retrieve the vehicle associated with each
            work order.  Return a list of (vehicle, workorder) tuples filled in
            with the results of the query.
        """
        return []
    
    def getCompletedWorkorders(self):
        """ Query the database for all work orders where the work order status
            is 'completed'.  Also retrieve the vehicle associated with each
            work order.  Return a list of (vehicle, workorder) tuples filled in
            with the results of the query.
        """
        return []
    
    def validateCustomerInfo(self, customer):
        """ Validate the data fields in the 'customer' object for data errors 
            and required fields before save to db.  Return list of 
            (field name, error type) tuples.
        """
        return []
    
    def validateVehicleInfo(self, vehicle):
        """ Validate the data fields in the 'vehicle' object for data errors 
            and required fields before save to db.  Return list of 
            (field name, error type) tuples.
        """
        return []
    
    def validateWorkorderInfo(self, workorder):
        """ Validate the data fields in the 'workorder' object for data errors 
            and required fields before save to db.  Return list of 
            (field name, error type) tuples.
        """
        return []
    
    