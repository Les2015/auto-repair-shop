from google.appengine.ext import db

class CustomerEnt(db.Model):
    #custID = db.IntegerProperty(verbose_name = "Customer ID", required=True, indexed=True)
    first_name = db.StringProperty(verbose_name = "First Name", required=False)
    last_name = db.StringProperty(verbose_name = "Last Name", required=True)
    #address = db.PostalAddressProperty( ) 
  
    #ADDRESS REPLACES
    address1 = db.StringProperty(verbose_name = "Address 1", required=True)
    address2 = db.StringProperty(verbose_name = "Address 2", required=False)
    city = db.StringProperty(verbose_name = "City", required=True)
    state = db.StringProperty(verbose_name = "State", required=True)
    zip = db.StringProperty(verbose_name = "Zip", required=True)
  
    phone1 = db.StringProperty(verbose_name = "Primary Phone", required=True)
    phone2 = db.StringProperty(verbose_name = "Secondary Phone", required=False)
    email = db.StringProperty(verbose_name = "Email Address", required=False)
    #contactHow = db.StringProperty(verbose_name = "Preferred Contact Method", 
    #        choices=set(["phone1", "phone2", "email","smoke signals"]) , required=False) 
    comments = db.TextProperty(verbose_name = "Comments", required=False) 
    """
      # TODO: check that this is not ReferenceType of some list of vehicles
       # I think this is right but I'm not sure
      vehicles = db.ListProperty(Vehicle)
    """
  
def main( ):
    for p in CustomerEnt.properties() :
        print p

if __name__ == '__main__' :
    main()

"""
Examples of using these fields:

c = CustomerEnt()
c.email_address = db.Email("larry@example.com")
c.phone1 = db.PhoneNumber("1 (206) 555-1212")
c.address = db.PostalAddress("1600 Ampitheater Pkwy., Mountain View, CA")
c.get(keys) 
c.put()      // or db.put(models)
c.delete()  // or db.delete(models)
optional attributes:
Property( ..... validator=validatorFunc, indexed= boolean, default = defaultVal)

"""


