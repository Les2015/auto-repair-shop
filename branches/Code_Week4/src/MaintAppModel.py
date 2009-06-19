'''
Created on May 27, 2009

@author: Wing Wong

2009-06-05  Add customer Validation   Les Faby
2009-06-05  Add vehicle Validation    Les Faby

'''

import os
import re
import datetime
from google.appengine.ext import db
from google.appengine.api import apiproxy_stub_map 
from google.appengine.api import datastore_file_stub 
from MaintAppObjects import Customer, Vehicle, Workorder 
from DatastoreModels import CustomerEnt, VehicleEnt, WorkorderEnt
from Utilities import myLog, dateToString, stringToDate

APP_ID = u'auto-repair-shop'
os.environ['APPLICATION_ID'] = APP_ID  

def nz(value):
    """ if input value is None, convert it to empty string """
    return ("" if value is None else value)

def zn(strValue):
    """ if input strValue is empty, convert it to None """
    return (None if strValue=="" else strValue)

#================================================================
class ValidationErrors(Exception):
    '''
    Exception raised in case of an invalid record.
    usage
    try: 
        ... 
    catch ValidationErrors, ve:
       print ve    prints all the error text for all the fields in error
       errorMsg = str(ve)  puts that text in the variable
       ve.getFieldsWithErrors() to get a list of the field names in error
    '''
    def __init__(self, errTxt, badFldLst):
        self.errTxt = errTxt
        self.badFldLst = badFldLst
        
    def __str__(self):
        '''returns error text for all fields in error or required and missing' fields.'''
        return self.errTxt
    
    def getFieldsWithErrors(self):
        '''returns a list of fields in error.'''
        return self.badFldLst
#================================================================
class InternalErrors(ValidationErrors):
    '''
    Exception raised in case of an invalid record.
    usage
    try: 
        ... 
    catch InternalErrors, ie:
       print ie    prints all the error text for all the fields in error
       errorMsg = str(ie)  puts that text in the variable
       ve.getFieldsWithErrors() to get a list of the field names in error
    '''
    pass
#================================================================

class DuplicateCustomer(ValidationErrors):
    '''
    Exception raised in case of duplicate record.
    usage
    try: 
        ... 
    catch DuplicateCustomer, de:
       print de    prints all the error text for all the fields in error
       errorMsg = str(de)  puts that text in the variable
       de.getDuplicateCustomer() to get the customer object that is already in the datastore
    '''
    def __init__(self, errTxt, badFldLst, duplicate):
        ValidationErrors.__init__(self, errTxt, badFldLst)
        self.duplicate = duplicate

    def getDuplicateCustomer(self):
        '''returns the customer that is already saved in the datastore.'''
        return self.duplicate

################################################
#    validated in View so no longer required
################################################

#def isState(s):
#   #states, DX, possesions, territories and military bases
#   states =  ("WA", "VA", "DE", "DC", "WI", "WV", "HI", "AE", "FL", "FM", "WY", "NH", "NJ", "NM", "TX", "LA", "NC", "ND", "NE", "TN", "NY", "PA", "CA", "NV", "AA", "PW", "GU", "CO", "VI", "AK", "AL", "AP", "AS", "AR", "VT", "IL", "GA", "IN", "IA", "OK", "AZ", "ID", "CT", "ME", "MD", "MA", "OH", "UT", "MO", "MN", "MI", "MH", "RI", "KS", "MT", "MP", "MS", "PR", "SC", "KY", "OR", "SD")
#  if s in states:
#       return (True,"")
#    return (False,"Illegal State Name")
   
def isPhone(s):
    """
    Since phone num info is so variable little validation is done
    More specific validation could be done if there is separate fields for extension and location (home, work, other)
    """
    #  return (True, "")
    # after Example 7.16. Parsing Phone Numbers (Final Version), Diving into PYTHON
    # note that we are allowing extra characters here because phone#s come in a myriad of formats
    phonePat = re.compile(r'''
                # don't match beginning of string, number can start anywhere
    (\d{3})     # area code is 3 digits (e.g. '800')
    \D*         # optional separator is any number of non-digits
    (\d{3})     # trunk is 3 digits (e.g. '555')
    \D*         # optional separator
    (\d{4})     # rest of number is 4 digits (e.g. '1212')
    \D*         # optional separator
    (\d*)       # extension is optional and can be any number of digits
                #$ end of string
    ''', re.VERBOSE)
    res = phonePat.search(s)
    if res == None:
       return  (False, "invalid phone number format")
    parts = res.groups()
    if (len(parts) < 3) | (len(parts) > 5): 
       return (False, "invalid phone number format")
    return (True, "")
    

def isZip(s):
    aLen = len(s)
    if (aLen == 5) | (aLen == 9):
       if s.isdigit():
          return (True,"")
       else:
          return (False,"bad zip code")
    elif aLen != 10:
         return (False,"bad zip code")
    elif (s[:5].isdigit())  &  \
       (s[5] == '-') & \
       (s[6:].isdigit()):
            return (True,"") 
    return (False,"bad zip code")
    
def lenOK(s,minLen, maxLen):
    if s == None:
       return (False,"needs to have a length between %i and %i" % ( minLen, maxLen))
    if minLen <= len(s) <= maxLen: 
       return (True, "")
    else:
       return (False, "needs to have a length between %i and %i" % ( minLen, maxLen))
   
def isMissing(s):
       return (s == None) | (s == '')

class MaintAppModel(object):
    requiredCust = ('last_name', 'address1', 'city', 'state', 'zip', 'phone1')
    requiredVehicle = ('customer_id', 'make', 'model', 'year', 'license')
    requiredWorkOrdAll = ('vehicle_id', 'mileage', 'status',
                       'customer_request', 'mechanic', 'date_created')
    # additional required fields for work orders that are ready for customer pickup (not open) 
    requiredWorkOrdDone = ('task_list', 'work_performed', 'notes')

    OK, MISSING, INVALID = (0,1,2)
    
    def __init__(self):
         self.__valid = True
         self.missing = []
         self.errTxt = ""
         self.invFld = []
         return
      
    #---------------------------- customer -----------------------------------------------
    
    #================================================================================
    #  For each customer attribute to validate, there is a chk_attribute method that
    #  returns True if valid, else False
    #================================================================================
    
    
    def chk_id(self,id):
        return True
    
    def chk_first_name(self,first_name):
        status, msg = lenOK(first_name,1,50)
        return status
    
    def chk_last_name(self,last_name):
        status, msg = lenOK(last_name,1,50)
        return status
    
    def chk_address1(self,address):
        status, msg = lenOK(address,1,50)
        return status
 
    def chk_address2(self,address):
          status, msg = lenOK(address,1,50)
          return status
      
    def chk_city(self,city):
          status, msg = lenOK(city,1,50)
          return status
###################### 
#  validation done in View so now
#   always returns True
###################### 
    def chk_state(self,state):
        #status, msg = isState(state)
        return True
    
    def chk_zip(self,zip):
        status, msg = isZip(zip)
        return status
        
    def chk_phone1(self,phone):
        status, msg = isPhone(phone)
        return status
        
    def chk_phone2(self,phone):
        status, msg = isPhone(phone)
        return status
    
    def chk_email(self,email):
        status,msg = lenOK(email,1,50)
        return status
    
    def chk_comments(self, comments):
        status, msg = lenOK(comments,1,5000)
        return status
    
    def getInvFldNames(self):
        """ 
        returns a list of field names that need to be highlighted to indicate errors. 
        Missing fields are also included.
        """
        resLst = self.invFld
        resLst.extend(self.missing)
        return resLst

    def validateCust(self,customer):
        """
        given a customer instance,
        returns boolean: True if valid else False
        for each attribute, 
             check the attribute by calling corresponding chk_attribute(customer.attribute)
             method.
             Save a list of missing and invalid attributes and add errortext
             for each missing or invalid field.
        """
        
        for a in customer.__dict__.keys():
             check_attr_meth = getattr(self, 'chk_'+a, None)
             if check_attr_meth == None: continue
             anAttr = getattr(customer, a, None)
             if isMissing(anAttr):
                 if a in MaintAppModel.requiredCust:
                     self.missing.append(a)
                     self.errTxt += 'missing ' + a + '\n'
                 else: pass
             elif check_attr_meth(anAttr)  == False: 
                  self.invFld.append(a)
                  self.errTxt += 'invalid ' + a + '\n'    
        # if there are no required missing fields  or invalid fields, everything is ok
        return (len(self.missing) + len(self.invFld)) == 0
    
    def saveCustomerInfo(self, customer):
        """ 
        If customer is invalid, raise exception.
        Write customer object to data store.  If id in customer is '-1',
            create the record; otherwise, update the record.  Return the 
            primary key of the customer (the new one if creating, the existing
            one if updating.)
        """
        if self.validateCust(customer) == False: 
           resLst = self.getInvFldNames()
           raise ValidationErrors(self.errTxt, resLst)
       
        if customer.id == '-1':
            # supposed to be new record here; check if it is a duplicate of an existing record before trying to add
            # if it is a duplicate (defined by first_name, last_name and phone1), raise exception (DuplicateCustomer);  
            searchCriteria = Customer(first_name=customer.first_name, 
                                      last_name=customer.last_name, 
                                      phone1=customer.phone1)
            match = self.searchForMatchingCustomers(searchCriteria)
            if len(match) > 0:
                self.errTxt = 'Customer ' + customer.first_name + ' ' + customer.last_name + ' already in database\n'
                raise DuplicateCustomer(self.errTxt, [], match[0])          
            entity = None
        else:
            try:
                entity = CustomerEnt.get(db.Key(customer.id))
            except Exception:
                entity = None
       
        if entity:
            entity.first_name = zn(customer.first_name)
            entity.last_name = zn(customer.last_name)
            entity.address1 = zn(customer.address1)
            entity.address2 = zn(customer.address2)
            entity.city = zn(customer.city)
            entity.state = zn(customer.state)
            entity.zip = zn(customer.zip)
            entity.phone1 = zn(customer.phone1)
            entity.phone2 = zn(customer.phone2)
            entity.email = zn(customer.email)
            entity.comments = zn(customer.comments)
            entity.first_name_search = zn(customer.first_name.upper())
            entity.last_name_search = zn(customer.last_name.upper())
        else:    
            entity = CustomerEnt(first_name=zn(customer.first_name),
                                 last_name=zn(customer.last_name),
                                 address1=zn(customer.address1),
                                 address2=zn(customer.address2),
                                 city=zn(customer.city),
                                 state=zn(customer.state),
                                 zip=zn(customer.zip),
                                 phone1=zn(customer.phone1),
                                 phone2=zn(customer.phone2),
                                 email=zn(customer.email),
                                 comments=zn(customer.comments),
                                 first_name_search = zn(customer.first_name.upper()),
                                 last_name_search = zn(customer.last_name.upper()))
        key = entity.put()
        return str(key)
            
    def getCustomerFromCustomerEnt(self, customer_ent):
        """ Create a Customer object from a CustomerEnt; this is a helper method for searchForMatchingCustomers
        """
        if customer_ent:
            return Customer(id=str(customer_ent.key()), 
                            first_name=nz(customer_ent.first_name), 
                            last_name=nz(customer_ent.last_name),
                            address1=nz(customer_ent.address1),
                            address2=nz(customer_ent.address2),
                            city=nz(customer_ent.city),
                            state=nz(customer_ent.state),
                            zip=nz(customer_ent.zip),
                            phone1=nz(customer_ent.phone1),
                            phone2=nz(customer_ent.phone2),
                            email=nz(customer_ent.email),
                            comments=nz(customer_ent.comments))
        else:
            return None

    def getCustomer(self, customer_id):
        """ Retrieve the customer record from the database whose primary key
            is the customer_id passed in.
        """
        try:
        #entity = CustomerEnt.get(db.Key.from_path('CustomerEnt', customer_id))
            entity = CustomerEnt.get(db.Key(customer_id))
        except Exception:
            entity = None

        return self.getCustomerFromCustomerEnt(entity)
        
    def searchForMatchingCustomers(self, searchCriteria):
        """ The model forms a query based on AND logic for the various
            fields that have been entered into the searchCriteria object.
            The searchCriteria object is an instance of the Customer class.
            For now we will assume exact matches except for last_name and first_name:
                e.g., 'SELECT .... WHERE (customer_table.first_name=%d)' %
                                                searchCriteria.first_name
            last_name and first_name are matched in a case insensitive manner.
            In the future we may consider supporting wild card matching as well.
            Returns a list of Customer objects corresponding to the customer records
            ordered by last_name, then first_name
        """
        result = []
        limit = 50 # return at most 50 customers matching the search criteria        
        #query = db.Query(CustomerEnt)
        query = CustomerEnt.all()
        if searchCriteria.first_name: 
            query.filter("first_name_search =", searchCriteria.first_name.upper())
        if searchCriteria.last_name: 
            query.filter("last_name_search =", searchCriteria.last_name.upper())
        if searchCriteria.address1: 
            query.filter("address1 =", searchCriteria.address1)
        if searchCriteria.city: 
            query.filter("city =", searchCriteria.city)
        if searchCriteria.state: 
            query.filter("state =", searchCriteria.state)
        if searchCriteria.zip: 
            query.filter("zip =", searchCriteria.zip)
        if searchCriteria.phone1: 
            query.filter("phone1 =", searchCriteria.phone1)
        if searchCriteria.email: 
            query.filter("email =", searchCriteria.email)
        query.order("last_name_search")
        query.order("first_name_search")

        customers = query.fetch(limit) 
        for customer_ent in customers:
            result.append(self.getCustomerFromCustomerEnt(customer_ent))
        return result
         
    #---------------------------- vehicle -----------------------------------------------
    
    #================================================================================
    #  For each vehicle attribute to validate, there is a chk_attribute method that
    #  returns True if valid, else False
    #================================================================================
    def chk_customer_id(self, customer_id):
        return True
    
    def chk_make(self, make):
        status,msg = lenOK(make,1,30)
        return status
      
    def chk_model(self, model):
        status,msg = lenOK(model,1,30)
        return status
      
    def chk_year(self, year):
        # FIXME: is year already an integer, not a string????
        if (year.isdigit() == False):
            return False
        maxYr = datetime.datetime.today().year + 3
        myLog.write("maxYr = %i\nyear=%s" % (maxYr, year ))
        if  not (1925 < int(year) <  maxYr) :
            return False
        status,msg = lenOK(year,4,4)
        return status
              
    def chk_license(self, license):
        status,msg = lenOK(license,1,30)
        return status
      
    def chk_vin(self, vin):
        # Note:  see http://www.vinguard.org/vin.htm for the full story. This is not a complete check
        # For example, the year is encoded (vin[9]) as well as a check digit (vin[8])
        if (vin.isalnum() == False):
            return False
        status,msg = lenOK(vin,16,17)
        return status
      
    def chk_notes(self, notes):
        status,msg = lenOK(notes,1,5000)
        return status
    
    def validateVehicle(self,vehicle):
        """
        given a vehicle instance,
        returns boolean: True if valid else False
        for each attribute, 
             check the attribute by calling corresponding chk_attribute(vehicle.attribute)
             Save a list of missing and invalid attributes and add errortext
             for each missing or invalid field.
        """
        myLog.write('validateVehicle')
        for a in vehicle.__dict__.keys():
             myLog.write('validating ' +a)
             check_attr_meth = getattr(self, 'chk_'+a, None)
             if check_attr_meth == None: continue
             anAttr = getattr(vehicle, a, None)
             if isMissing(anAttr):
                 if a in MaintAppModel.requiredVehicle:
                     self.missing.append(a)
                     self.errTxt += 'missing ' + a + '\n'
                 else: pass
             elif check_attr_meth(anAttr)  == False: 
                  self.invFld.append(a)
                  self.errTxt += 'invalid ' + a + '\n'    
        # if there are no required missing fields  or invalid fields, everything is ok
        return (len(self.missing) + len(self.invFld)) == 0
       
    def saveVehicleInfo(self, vehicle):
        """ 
        If vehicle is invalid, raise exception.
        Write vehicle object to data store.  If id in vehicle object is
            -1, create the record; otherwise, update the existing record
            in the database.  Return primary key of the vehicle.
        """
        myLog.write('saveVehicleInfo')
        if self.validateVehicle(vehicle) == False: 
           resLst = self.getInvFldNames()
           if 'customer_id' in resLst:
              trap = InternalErrors
           else:
              trap = ValidationErrors
           raise trap(self.errTxt, resLst)
        myLog.write('validated Vehicle')
        if vehicle.id == '-1':
            entity = None
        else:
            try:
                entity = VehicleEnt.get(db.Key(vehicle.id))
            except Exception:
                entity = None
        
        customer_ent = CustomerEnt.get(db.Key(vehicle.customer_id))    
        #print "-- In saveVehicleInfo, customer_ent: ", customer_ent
        if entity:
            entity.make = zn(vehicle.make)
            entity.model = zn(vehicle.model)
            entity.year = int(vehicle.year)
            entity.license = zn(vehicle.license)
            entity.vin = zn(vehicle.vin)
            entity.notes = zn(vehicle.notes)
            entity.customer = customer_ent
        else:    
            entity = VehicleEnt(make=zn(vehicle.make),
                                model=zn(vehicle.model),
                                year=int(vehicle.year),
                                license=zn(vehicle.license),
                                vin=zn(vehicle.vin),
                                notes=zn(vehicle.notes),
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
                           make=nz(vehicle_ent.make), 
                           model=nz(vehicle_ent.model), 
                           year=str(vehicle_ent.year),
                           license=nz(vehicle_ent.license),
                           vin=nz(vehicle_ent.vin),
                           notes=nz(vehicle_ent.notes),
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
            
    def getVehicleList(self, customer_id):
        """ This method queries the database for vehicles records belonging
            to the customer identified by customer_id. Return an empty list
            if no vehicles are found.
        """
        result = []
        limit = 10 # get at most 10 vehicles for each customer
        try:
            customer = CustomerEnt.get(db.Key(customer_id))
        except Exception:
            return result
        
        query = VehicleEnt.gql("WHERE customer = :key", key=customer)
        vehicles = query.fetch(limit) 
        for vehicle_ent in vehicles:
            result.append(self.getVehicleFromVehicleEnt(vehicle_ent))
        return result
    
    #---------------------------- work order -----------------------------------------------
    
    #================================================================================
    #  For each workOrder attribute to validate, there is a chk_w_attribute method
    # that returns True if valid, else False
    #================================================================================
    
    def chk_w_vehicle_id(self, vehicle_id):
        return True
    
    def chk_w_date_created(self, date_created):
        return True
    
    def chk_w_date_closed(self, date_closed):
        return True
    
    def chk_w_mileage(self, mileage):
        status,msg = lenOK(mileage, 1,7)
        if status == False:
            return False
        if mileage.isdigit():
            return ( 0 < int(mileage)  < 1000000)
        else:
            return False
    
    def chk_w_status(self, status):
        return status in (Workorder.OPEN, Workorder.COMPLETED, Workorder.CLOSED )
    
    def chk_w_customer_request(self, customer_request):
        status,msg = lenOK(customer_request,1,5000)
        return status
 
    def chk_w_mechanic(self, mechanic):
        status,msg = lenOK(mechanic, 1,50)
        return status
    
    def chk_w_task_list(self, task_list):
        isOK,msg = lenOK(task_list, 1,5000)
        return isOK
    
    def chk_w_work_performed(self, work_performed):
        status,msg = lenOK(work_performed,1,5000)
        return status
    
    #FIXME: what about date fields?
    
    def validateWorkOrder(self,workOrder):
        """
        given a work order instance,
        returns True if valid else False
        for each attribute, 
             check the attribute by calling corresponding chk_attribute(vehicle.attribute)
             Save a list of missing and invalid attributes and add errortext
             for each missing or invalid field.
        """
        requiredWorkOrd = list(MaintAppModel.requiredWorkOrdAll)
        if workOrder.status != Workorder.OPEN:
            requiredWorkOrd.extend(MaintAppModel.requiredWorkOrdDone)
        if workOrder.status == Workorder.CLOSED:
             requiredWorkOrd.append('date_closed') 
           
        
        
        for a in workOrder.__dict__.keys():
             myLog.write('checking ' + a + '...')
             check_attr_meth = getattr(self, 'chk_w_'+a, None)
             if check_attr_meth == None: continue
             anAttr = getattr(workOrder, a, None)
             if isMissing(anAttr):
                 if a in requiredWorkOrd:
                     self.missing.append(a)
                     self.errTxt += 'missing ' + a + '\n'
                 else: pass
             elif check_attr_meth(anAttr)  == False: 
                  self.invFld.append(a)
                  self.errTxt += 'invalid ' + a + '\n'  
        
        # if there are no required missing fields  or invalid fields, everything is ok
        return (len(self.missing) + len(self.invFld)) == 0
       
    def saveWorkorder(self, workorder):
        """ 
        If workorder is invalid, raise exception.
        Write contents of workorder object to data store.  
        If id in workorder object is -1, create the record; 
        otherwise, update the existing record
        in the database.  Return primary key of the workorder.
        """
        if self.validateWorkOrder(workorder) == False: 
           resLst = self.getInvFldNames()
           if ('date_created' in resLst) or \
              ('date_closed' in resLst) or \
               ('vehicle_id' in resLst) :
              trap = InternalErrors
           else:
              trap = ValidationErrors   
           raise trap(self.errTxt, resLst)
        
        myLog.write("----> %s" % workorder.id)
        if workorder.id == '-1':
            entity = None
        else:
            try:
                entity = WorkorderEnt.get(db.Key(workorder.id))
            except Exception, e:
                myLog.write("db error: " + str(e))
                entity = None

        vehicle_ent = VehicleEnt.get(db.Key(workorder.vehicle_id))    
        if entity:
            entity.mileage = int(workorder.mileage)
            entity.status = zn(workorder.status)
            entity.date_created = stringToDate(workorder.date_created)
            entity.customer_request = zn(workorder.customer_request)
            entity.mechanic = zn(workorder.mechanic)
            entity.task_list = zn(workorder.task_list)
            entity.work_performed = zn(workorder.work_performed)
            entity.notes = zn(workorder.notes)
            entity.date_closed = stringToDate(workorder.date_closed)
            entity.vehicle = vehicle_ent
        else:    
            entity = WorkorderEnt(mileage=int(workorder.mileage),
                                  status=zn(workorder.status),
                                  date_created=stringToDate(workorder.date_created),
                                  customer_request=zn(workorder.customer_request),
                                  mechanic=zn(workorder.mechanic),
                                  task_list=zn(workorder.task_list),
                                  work_performed=zn(workorder.work_performed),
                                  notes=zn(workorder.notes),
                                  date_closed=stringToDate(workorder.date_closed),
                                  vehicle = vehicle_ent)
        key = entity.put()
        return str(key)
    
    def getWorkorderFromWorkorderEnt(self, workorder_ent):
        """ Create a Workorder object from a WorkorderEnt; this is a helper method for getWorkorferList
        """
        vehicle_key = '-1'
        if workorder_ent:
            if workorder_ent.vehicle:
                vehicle_key = str(workorder_ent.vehicle.key())
                
            return Workorder(id=str(workorder_ent.key()), 
                             mileage=str(workorder_ent.mileage), 
                             status=nz(workorder_ent.status), 
                             date_created=dateToString(workorder_ent.date_created),
                             customer_request=nz(workorder_ent.customer_request),
                             mechanic=nz(workorder_ent.mechanic),
                             task_list=nz(workorder_ent.task_list),
                             work_performed=nz(workorder_ent.work_performed),
                             notes=nz(workorder_ent.notes),
                             date_closed=dateToString(workorder_ent.date_closed),
                             vehicle_id=vehicle_key)
        else:
            return None

    def getWorkorder(self, workorder_id):
        """ Return the workorder record whose id is given by the workorder_id parameter.
        """
        try:
            entity = WorkorderEnt.get(db.Key(workorder_id))
        except Exception:
            entity = None
        return self.getWorkorderFromWorkorderEnt(entity)
    
    def getWorkorderList(self, vehicle_id):
        """ Return the list of workorders belonging to the vehicle identified
            by vehicle_id.  Return an empty list if no workorders are found.
        """
        result = []
        limit = 10 # get at most 10 work orders for each vehicle
        try:
            vehicle = VehicleEnt.get(db.Key(vehicle_id))
        except Exception:
            return result
        
        query = WorkorderEnt.gql("WHERE vehicle = :key ORDER BY date_created DESC", key=vehicle)
        workorders = query.fetch(limit) 
        for workorder_ent in workorders:
            result.append(self.getWorkorderFromWorkorderEnt(workorder_ent))
        return result
    
    def getOpenWorkorders(self):
        """ Query the database for all work orders where the work order status
            is 'open'.  Also retrieve the vehicle associated with each
            work order.  Return a list of (vehicle, workorder) tuples filled in
            with the results of the query.
            The list is sorted by workorder date_created in descending order
        """
        result = []
        limit = 100 # get at most 100 open workorders 
        
        query = WorkorderEnt.gql("WHERE status = :status ORDER BY date_created DESC", status=Workorder.OPEN)
        workorders = query.fetch(limit) 
        for workorder_ent in workorders:
            vehicle = self.getVehicleFromVehicleEnt(workorder_ent.vehicle)
            result.append((vehicle, self.getWorkorderFromWorkorderEnt(workorder_ent)))
        return result
    
    def getCompletedWorkorders(self):
        """ Query the database for all work orders where the work order status
            is 'completed'.  Also retrieve the vehicle associated with each
            work order.  Return a list of (vehicle, workorder) tuples filled in
            with the results of the query.
            The list is sorted by workorder date_created in descending order
        """
        result = []
        limit = 100 # get at most 100 completed workorders 
        
        query = WorkorderEnt.gql("WHERE status = :status ORDER BY date_created DESC", status=Workorder.COMPLETED)
        workorders = query.fetch(limit) 
        for workorder_ent in workorders:
            vehicle = self.getVehicleFromVehicleEnt(workorder_ent.vehicle)
            result.append((vehicle, self.getWorkorderFromWorkorderEnt(workorder_ent)))
        return result    
    
    def getNumberOfWorkorders(self, vehicle_id):
        """ Returns the number of workorders that have been saved for the
            vehicle specified by 'vehicle_id'
        """
        try:
            vehicle = VehicleEnt.get(db.Key(vehicle_id))
        except Exception:
            return 0
        
        query = WorkorderEnt.gql("WHERE vehicle = :key", key=vehicle)
        workorders = query.fetch(limit=1000)
        return len(workorders) 
    
        #workorders = self.getWorkorderList(vehicle_id)
        #return len(workorders)
        
    def hasUnclosedWorkorder(self, vehicle_id):
        """ Determine if the vehicle specified by 'vehicle_id' has any 
            unclosed workorders.  Returns True if there is an unclosed
            workorder for the vehicle.  Returns False if there are no
            workorders, if the vehicle_id=='-1' (unsaved, new vehicle)
            or if all of them are closed. 
        """
        retVal = False
        if vehicle_id != "-1":
            try:
                vehicle = VehicleEnt.get(db.Key(vehicle_id))
            except Exception:
                return retVal
            
            query = WorkorderEnt.gql("WHERE vehicle = :key AND status = :status", key=vehicle, status=Workorder.OPEN)
            open_workorders = query.fetch(limit=100) 
            query = WorkorderEnt.gql("WHERE vehicle = :key AND status = :status", key=vehicle, status=Workorder.COMPLETED)
            completed_workorders = query.fetch(limit=100) 
            if (len(open_workorders)>0 or len(completed_workorders)>0):
                retVal = True

#            unclosedWorkorders = self.getOpenWorkorders() + \
#                                 self.getCompletedWorkorders()
#            for vehicle, workorder in unclosedWorkorders:
#                if vehicle is not None and vehicle.getId() == vehicle_id:
#                    retVal = True
#                    break
        return retVal
        
    #---------------------------- List of Mechanics --------------------------------
    
    def getMechanics(self):
        """ Open and read the contents of config/mechanics.cfg and return
            the contents as a list of strings, skipping comment lines and
            blank lines. """ 
        mechPath = os.path.join ( os.path.dirname(__file__), 'config/mechanics.cfg' )
        mechanics = []
        for line in  file(mechPath,'r'):
              mechanic = line.rstrip('\n ').strip()
              if len(mechanic) == 0:
                  continue
              if mechanic[0] in "\"\'\#":
                 continue
              mechanics.append(mechanic)
        return mechanics
    

class TestMaintAppModel(object):
    ''' unit test '''
    def __init__(self): 
        # Start with a fresh api proxy. 
        apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap() 
        
        # Use a fresh stub datastore. 
        stub = datastore_file_stub.DatastoreFileStub(APP_ID, '', '') 
        apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', stub) 
        
    def testSaveAndGet(self):
        ''' unit test '''
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
        c1_retrieved = appModel.getCustomer(c1_key)
        print "c1_retrieved: ", c1_retrieved
        print "c2_key = " + c2_key
        c2_retrieved = appModel.getCustomer(c2_key)
        print "c2_retrieved: ", c2_retrieved

        print "\n** testing vehicle save..."
        v1 = Vehicle(id='-1',
                     make='Honda', 
                     model='Civic', 
                     year="2001",
                     license='AB1234',
                     vin='',
                     notes='',
                     customer_id=c1_key)
        v1_key = appModel.saveVehicleInfo(v1)
        print "v1_key = " + v1_key

        v2 = Vehicle(id='v2',
                     make='Honda', 
                     model='Accord', 
                     year="2007",
                     license='XY1234',
                     vin='',
                     notes='',
                     customer_id=c2_key)
        v2_key = appModel.saveVehicleInfo(v2)
        print "v2_key = " + v2_key
        
        v3 = Vehicle(id='v3',
                     make='Honda', 
                     model='SUV', 
                     year="2008",
                     license='XY9999',
                     vin='',
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
        v1_retrieved = appModel.getVehicle(v1_key)
        print "v1_retrieved: ", v1_retrieved    
        print "v2_key = " + v2_key
        v2_retrieved = appModel.getVehicle(v2_key)
        print "v2_retrieved: ", v2_retrieved
        print "v3_key = " + v3_key
        v3_retrieved = appModel.getVehicle(v3_key)
        print "v3_retrieved: ", v3_retrieved


        print "\n** testing vehicleList retrieve..."
        nonexist_list = appModel.getVehicleList('-1')
        print "list of vehicle owned by non-exist customer:", nonexist_list
        
        c1_list = appModel.getVehicleList(c1_key)
        print "list of vehicle owned by c1:", c1_list 
        for i in c1_list:
            print i
        print 
        c2_list = appModel.getVehicleList(c2_key)
        print "list of vehicle owned by c2:", c2_list
        for i in c2_list:
            print i
        print
        
        print "\n** testing customer search..."
        searchCriteria = Customer()
        customer_list = appModel.searchForMatchingCustomers(searchCriteria)
        print "customer_list, searchCriteria is blank:", customer_list
        for i in customer_list:
            print i
        print
        searchCriteria = Customer(last_name='Wong', city='Santa Clara')
        customer_list = appModel.searchForMatchingCustomers(searchCriteria)
        print "customer_list, searchCriteria last_name='Wong', city='Santa Clara':", customer_list
        for i in customer_list:
            print i
        print
        searchCriteria = Customer(first_name='Brad')
        customer_list = appModel.searchForMatchingCustomers(searchCriteria)
        print "customer_list, searchCriteria first_name='Brad':", customer_list
        for i in customer_list:
            print i
        print
        
        print "\n** testing duplicate customer"
        duplicate_c = Customer(id='-1',
                      first_name='Fiona',
                      last_name='Wong',
                      address1='addr',
                      address2='',
                      city='San Jose',
                      state='CA',
                      zip='95135',
                      phone1='111.111.1111',
                      phone2='222.222.2222',
                      email='fionawhwong@yahoo.com',
                      comments='')
        try:
            duplicate_key = appModel.saveCustomerInfo(duplicate_c)
        except DuplicateCustomer, e:
            print e
            print "duplicate found: ", e.getDuplicateCustomer()
        
        print "\n** testing duplicate customer; case-insensitive search on"
        duplicate_c = Customer(id='-1',
                      first_name='WING',
                      last_name='WONG',
                      address1='addr',
                      address2='',
                      city='San Jose',
                      state='CA',
                      zip='95135',
                      phone1='111.111.1111',
                      phone2='222.222.2222',
                      email='fionawhwong@yahoo.com',
                      comments='')
        try:
            duplicate_key = appModel.saveCustomerInfo(duplicate_c)
        except DuplicateCustomer, e:
            print e
            print "duplicate found: ", e.getDuplicateCustomer()
        

def main( ):
    ''' unit test '''
    test = TestMaintAppModel()
    test.testSaveAndGet()

if __name__ == '__main__' :
    main()
    
    
