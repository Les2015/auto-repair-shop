'''
Created on May 27, 2009

@author: 
'''

import os
from google.appengine.ext import db
from google.appengine.api import apiproxy_stub_map 
from google.appengine.api import datastore_file_stub 
from MaintAppObjects import Customer 
from MaintAppObjects import Vehicle 
from MaintAppObjects import Workorder 
from CustomerEnt import CustomerEnt
from VehicleEnt import VehicleEnt
from WorkorderEnt import WorkorderEnt

APP_ID = u'auto-repair-shop'
os.environ['APPLICATION_ID'] = APP_ID  

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
        if customer.id == '-1':
            entity = None
        else:
            try:
                entity = CustomerEnt.get(db.Key(customer.id))
            except Exception:
                entity = None

        if entity:
            #print "Entity is not None"
            entity.first_name = customer.first_name
            entity.last_name = customer.last_name
            entity.address1 = customer.address1
            entity.address2 = customer.address2
            entity.city = customer.city
            entity.state = customer.state
            entity.zip = customer.zip
            entity.phone1 = customer.phone1
            entity.phone2 = customer.phone2
            entity.email = customer.email
            entity.comments = customer.comments
        else:    
            #print "Entity is None"        
            entity = CustomerEnt(first_name=customer.first_name,
                                 last_name=customer.last_name,
                                 address1=customer.address1,
                                 address2=customer.address2,
                                 city=customer.city,
                                 state=customer.state,
                                 zip=customer.zip,
                                 phone1=customer.phone1,
                                 phone2=customer.phone2,
                                 email=customer.email,
                                 comments=customer.comments)
        key = entity.put()
        return str(key)
            
    def getCustomer(self, customer_id):
        """ Retrieve the customer record from the database whose primary key
            is the customer_id passed in.
        """
        try:
        #entity = CustomerEnt.get(db.Key.from_path('CustomerEnt', customer_id))
            entity = CustomerEnt.get(db.Key(customer_id))
        except Exception:
            entity = None

        if entity:
            return Customer(id=customer_id, 
                            first_name=entity.first_name, 
                            last_name=entity.last_name,
                            address1=entity.address1,
                            address2=entity.address2,
                            city=entity.city,
                            state=entity.state,
                            zip=entity.zip,
                            phone1=entity.phone1,
                            phone2=entity.phone2,
                            email=entity.email,
                            comments=entity.comments)
        else:
            return None
    
    def saveVehicleInfo(self, vehicle):
        """ Write vehicle object to data store.  If id in vehicle object is
            -1, create the record; otherwise, update the existing record
            in the database.  Return primary key of the vehicle.
        """
        if vehicle.id == '-1':
            entity = None
        else:
            try:
            #entity = VehicleEnt.get_by_key_name(str(vehicle.id))
            #entity = VehicleEnt.get(db.Key.from_path('VehicleEnt', vehicle.id))
                entity = VehicleEnt.get(db.Key(vehicle.id))
            except Exception:
                entity = None
        
        customer_ent = CustomerEnt.get(db.Key(vehicle.customer_id))    
        #print "-- In saveVehicleInfo, customer_ent: ", customer_ent
        if entity:
            entity.make = vehicle.make
            entity.model = vehicle.model
            entity.year = vehicle.year
            entity.license = vehicle.license
            entity.vin = vehicle.vin
            entity.notes = vehicle.notes
            entity.customer = customer_ent
        else:    
            entity = VehicleEnt(make=vehicle.make,
                                model=vehicle.model,
                                year=vehicle.year,
                                license=vehicle.license,
                                vin=vehicle.vin,
                                notes=vehicle.notes,
                                customer=customer_ent)
        
        key = entity.put()
        return str(key)
    
    def getVehicleFromVehicleEnt(self, vehicle_ent):
        """ Create a Vehicle object from a VehicleEnt; this is a helper method for getVehicleList
        """
        customer_key = '-1'
        if vehicle_ent:
            if vehicle_ent.customer:
                customer_key = str(vehicle_ent.customer.key())
                
            #print "--In getVehicleFromVehicleEnt, customer_key: " + customer_key    
            #print "--In getVehicleFromVehicleEnt, customer object:", vehicle_ent.customer    
            return Vehicle(id=str(vehicle_ent.key()), 
                           make=vehicle_ent.make, 
                           model=vehicle_ent.model, 
                           year=vehicle_ent.year,
                           license=vehicle_ent.license,
                           vin=vehicle_ent.vin,
                           notes=vehicle_ent.notes,
                           customer_id=customer_key)
        else:
            return None

    def getVehicle(self, vehicle_id):
        """ Retrieve the vehicle record from the database whose primary key
            is the vehicle_id passed in.
        """
        try:
            entity = VehicleEnt.get(db.Key(vehicle_id))
        except Exception:
            entity = None
        return self.getVehicleFromVehicleEnt(entity)
    
        """
        if entity:
            if entity.customer:
                customer_key = str(entity.customer.key())
                
            #print "--In getVehicle, customer_key: " + customer_key    
            #print "--In getVehicle, customer object:", entity.customer    
            return Vehicle(id=vehicle_id, 
                           make=entity.make, 
                           model=entity.model, 
                           year=entity.year,
                           license=entity.license,
                           vin=entity.vin,
                           notes=entity.notes,
                           customer_id=customer_key)
        else:
            return None
        """
        
    def getVehicleList(self, customer_id):
        """ This method queries the database for vehicles records belonging
            to the customer identified by customer_id. Return an empty list
            if no vehicles are found.
        """
        result = []
        #print "customer_id: " + str(customer_id)
        customer = CustomerEnt.get(db.Key(customer_id))
        
        query = VehicleEnt.gql("WHERE customer = :key", key=customer)
        vehicles = query.fetch(10) # get at most 10 vehicle for each customer
        for vehicle_ent in vehicles:
            result.append(self.getVehicleFromVehicleEnt(vehicle_ent))
        return result
    
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
    

class TestMaintAppModel(object):
    #def setUp(self): 
    def __init__(self): 
        # Start with a fresh api proxy. 
        apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap() 
        
        # Use a fresh stub datastore. 
        stub = datastore_file_stub.DatastoreFileStub(APP_ID, '', '') 
        apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', stub) 
        
    def testSaveAndGet(self):
        appModel = MaintAppModel()
        print "** testing customer save..."
        c1 = Customer(id='-1',
                      first_name='Fiona',
                      last_name='Wong',
                      address1='PO Box 3134',
                      address2='',
                      city='Santa Clara',
                      state='CA',
                      zip='95055',
                      phone1='111.111.1111',
                      phone2='222.222.2222',
                      email='fionawhwong@gmail.com',
                      comments='')
        #print "c1 created -", c1
        c1_key = appModel.saveCustomerInfo(c1)
        print "c1_key = " + c1_key
                        
        c2 = Customer(id='c2',
                      first_name='Wing',
                      last_name='Wong',
                      address1='c2 address1',
                      address2='',
                      city='c2 city',
                      state='CA',
                      zip='95055',
                      phone1='111.111.1111',
                      phone2='222.222.2222',
                      email='wingwong@gmail.com',
                      comments='')
        #print "c2 created -", c2
        c2_key = appModel.saveCustomerInfo(c2)
        print "c2_key = " + c2_key

        print "* all saved customers:"
        customers = CustomerEnt.all()
        for customer in customers:
            print customer.first_name, customer.last_name, ", object ", customer
        
        print "\n** testing customer retrieve..."
        print "c1_key = " + c1_key
        c1_retrived = appModel.getCustomer(c1_key)
        print "c1_retrived: ", c1_retrived
        print "c2_key = " + c2_key
        c2_retrived = appModel.getCustomer(c2_key)
        print "c2_retrived: ", c2_retrived

        print "\n** testing vehicle save..."
        v1 = Vehicle(id='-1',
                     make='Honda', 
                     model='Civic', 
                     year=2001,
                     license='AB1234',
                     vin='VIN',
                     notes='',
                     customer_id=c1_key)
        v1_key = appModel.saveVehicleInfo(v1)
        print "v1_key = " + v1_key

        v2 = Vehicle(id='v2',
                     make='Honda', 
                     model='Accord', 
                     year=2007,
                     license='XY1234',
                     vin='VIN',
                     notes='',
                     customer_id=c2_key)
        v2_key = appModel.saveVehicleInfo(v2)
        print "v2_key = " + v2_key
        
        v3 = Vehicle(id='v3',
                     make='Honda', 
                     model='SUV', 
                     year=2008,
                     license='XY9999',
                     vin='VIN',
                     notes='also belong to c2',
                     customer_id=c2_key)
        v3_key = appModel.saveVehicleInfo(v3)
        print "v3_key = " + v3_key

        print "* all saved vehicles:"
        vehicles = VehicleEnt.all()
        for vehicle in vehicles:
            print vehicle.make, vehicle.model, ", owner by customer with id ", str(vehicle.customer.key()), "(object ", vehicle.customer, ")"
        
    
        print "\n** testing vehicle retrieve..."
        print "v1_key = " + v1_key
        v1_retrived = appModel.getVehicle(v1_key)
        print "v1_retrived: ", v1_retrived    
        print "v2_key = " + v2_key
        v2_retrived = appModel.getVehicle(v2_key)
        print "v2_retrived: ", v2_retrived
        print "v3_key = " + v3_key
        v3_retrived = appModel.getVehicle(v3_key)
        print "v3_retrived: ", v3_retrived


        print "\n** testing vehicleList retrieve..."
        """
        nonexist_list = appModel.getVehicleList('-1')
        print "list of vehicle owned by non-exist customer", nonexist_list
        """
        c1_list = appModel.getVehicleList(c1_key)
        print "list of vehicle owned by c1: " 
        for i in c1_list:
            print i
        print 
        c2_list = appModel.getVehicleList(c2_key)
        print "list of vehicle owned by c2: "
        for i in c2_list:
            print i
        print
        
        
def main( ):
    #run_wsgi_app(application)
    test = TestMaintAppModel()
    test.testSaveAndGet()

if __name__ == '__main__' :
    main()
    
    