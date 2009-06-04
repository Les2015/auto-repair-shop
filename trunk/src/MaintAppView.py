'''
Created on May 25, 2009

@author: bradg
'''

NEW_CUSTOMER = 1
FIND_CUSTOMER = 2
INPUT_CUSTOMER = 3

from MaintAppObjects import nz

class MaintAppView(object):
    """ Class to implement the View part of the MVC implementation of the
        Maintenance Records System.  This class provides the public interface
        that the Controller works with to specify which parts of the interface
        are active and what the default values are for the various form fields
        (and in some cases buttons and links.)
        
        There are three primary assumptions behind this interface:
        1 - The View is stateless with all configuration information needed to
            render the screen at any one time being passed in from the controller.
        2 - The order in which the methods for setting the mode and configuration
            information should be considered 'random'.
        3 - The serve_content method will be called after all mode and configuration
            information has been loaded.  In general 2 & 3 imply that almost all of
            the html data stream preparation happens during the serve_content call
            and that the mode and configuration are cached until that call.
            (Of course item 1 implies that all of the cached information is lost
            once the html is fully served.) 
    """
    
    def __init__(self, controller):
        self.__macController = controller
        self.__sidePanel = SidePanelSubview()
        self.__customerPanel = CustomerSubview()
        self.__vehiclePanel = VehicleSubview()
        self.__mainMode = NEW_CUSTOMER
        return None
    
    def set_new_customer_mode(self):
        self.__mainMode = NEW_CUSTOMER
        self.__customerPanel._configure_input_mode()
    
    def set_search_mode(self):
        self.__mainMode = FIND_CUSTOMER
        self.__customerPanel._configure_search_mode()
        
    def set_search_results_mode(self):
        pass
    
    def set_customer_vehicle_mode(self):
        self.__mainMode = INPUT_CUSTOMER
        self.__customerPanel._configure_input_mode()
        
    def set_workorder_mode(self):
        pass
        
    def configureHiddenFields(self, customer_id, vehicle_id, workorder_id):
        self.__sidePanel._configure_hidden_fields(customer_id, vehicle_id, workorder_id)
        
    def configureErrorMessages(self, errors):
        """ Errors is a list of (field name, error type) tuples to be used to format
            errors and highlighting fields where data validation errors were detected.
        """
        pass
        
    def configureSidePanelContent(self, activeElement,
                                  openWorkorders,
                                  completedWorkorders,
                                  debug_message):
        self.__sidePanel._configure_selection(activeElement)
        self.__sidePanel._configure_content(openWorkorders, 
                                            completedWorkorders, 
                                            debug_message)
        
    def configureCustomerContent(self, customer_info):
        self.__customerPanel._configure_content(customer_info)

    def configureSearchResults(self, customer_list):
        self.__customerPanel._configure_search_results(customer_list)
        
    def configureVehicleContent(self, vehicle_list):
        self.__vehiclePanel._configure_content(vehicle_list)
        
    def configureWorkorderHeader(self, customer, vehicle):
        pass
    
    def configureWorkorderContent(self, workorder_list):
        pass
    
    def showSaveDialog(self, request_button, request_tag):
        """ This method is called to set the UI up to display a save dialog
            on the browser with Yes/No/Cancel buttons.  This dialog should be
            in a separate html Form with the callback being directed to a
            different page... <form action="/Dialog" method="post">.  In
            addition, all other form fields should be disabled so the user
            cannot change anything while the dialog is active.
            
            The string in 'request_button' and the one in 'request_tag' 
            should be saved in hidden form fields of the same names and
            associated with this dialog form so they get submitted when
            the user responds to the dialog.
        """
        pass
    
    def serve_content(self, reqhandler):
        self.__serve_header(reqhandler)
        reqhandler.response.out.write("""
          <body>
            <form action="/Customer" method="post">
              <table class="my_table">
                <tr>
                  <td rowspan="2" class="my_tleft">""")
        if self.__sidePanel is not None:
            self.__sidePanel._serve_content(reqhandler)
        reqhandler.response.out.write("""
                  </td>
                  <td class="my_tright">""")
        
        if self.__customerPanel is not None:
            self.__customerPanel._serve_content(reqhandler)
        reqhandler.response.out.write("""
                  </td>
                </tr>
                """)
        
        if self.__mainMode == INPUT_CUSTOMER:
            reqhandler.response.out.write("""
                    <tr>
                      <td class="my_tright_bottom">""")
            if self.__vehiclePanel is not None:
                self.__vehiclePanel._serve_content(reqhandler)
            reqhandler.response.out.write("""
                      </td>
                    </tr>
                    """)
            
        reqhandler.response.out.write("""
              </table>
            </form>
          </body>
        </html>
        """)
        return None
    
    def __serve_header(self, reqhandler):
        reqhandler.response.out.write(
"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
       "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
    <head>
        <title>Dermico Auto Maintenance Records System</title>
        <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
        <link href="/stylesheets/dermico.css" rel="stylesheet" type="text/css" />
    </head>
    """)
        return None

    
class SidePanelSubview(object):
    def __init__(self):
        self.__itemSelected = 1
        self.__comments = ""
        self.__customerId = "-1"
        self.__vehicleId = "-1"
        self.__workorderId = "-1"
        return None
    
    def _configure_selection(self, whichItem):
        """ whichItem is an integer indicating what is to be highlighted in the
            side panel:
                0 - Nothing is highlighted.
                1 - The New Customer button is highlighted
                2 - The Find Customer button is highlighted
                3 - The open or completed workorder whose primary key matches the
                    value of the __workorderId member variable is to be highlighted.
                    If no match is found, nothing is highlighted. 
        """
        self.__itemSelected = whichItem
    
    def _configure_content(self, openWorkorders, completedWorkorders, debug_message):
        self.__comments = debug_message
        
    def _configure_hidden_fields(self, customer_id, vehicle_id, workorder_id):
        self.__customerId = customer_id
        self.__vehicleId = vehicle_id
        self.__workorderId = workorder_id
        return None
    
    def _serve_content(self, reqhandler):
        linkClass = "s_side_links"
        activeLinkClass = "s_active_side_links"
        
        reqhandler.response.out.write('<p>Customer Input:</p>')
        css_class = activeLinkClass if (self.__itemSelected == 1) else linkClass
        reqhandler.response.out.write('<p><input class="%s" type="submit" name="submit_newcust" value="Add New Customer" /></p>' % css_class)
        css_class = activeLinkClass if (self.__itemSelected == 2) else linkClass
        reqhandler.response.out.write('<p><input class="%s" type="submit" name="submit_findcust" value="Find Customer" /></p>' % css_class)
        reqhandler.response.out.write('<p>Open Work Orders:</p>')
        reqhandler.response.out.write('<p>%s</p>' % self.__comments)
        reqhandler.response.out.write('<p>Work Completed:</p>')
        reqhandler.response.out.write('<input type="hidden" name="customer_id"  value="%s" />' % self.__customerId)
        reqhandler.response.out.write('<input type="hidden" name="vehicle_id"   value="%s" />' % self.__vehicleId)
        reqhandler.response.out.write('<input type="hidden" name="workorder_id" value="%s" />' % self.__workorderId)
        return None
    
        
class CustomerSubview(object):
    def __init__(self):
        self.__customer = None
        self.__searchMode = False
        return None
    
    def _configure_content(self, customerInfo):
        self.__customer = customerInfo
        return None
    
    def _configure_search_mode(self):
        self.__searchMode = True
        return None
    
    def _configure_input_mode(self):
        self.__searchMode = False
        return None
    
    def _configure_search_results(self, customer_list):
        self.__searchMode = True
        self.__searchResults = customer_list
        return None
    
    def _serve_content(self, reqhandler):
        reqhandler.response.out.write("""
            <table style="margin-top:15px; margin-left:auto; margin-right:auto;">
            <tr>
            <td>
            <label for="first_name">First Name: </label>
            </td>
            <td>""")
        reqhandler.response.out.write('<input type="text" name="first_name" value="%s" />' %
                                        nz(self.__customer.first_name))
        reqhandler.response.out.write("""
            </td>
            <td>
            <label for="last_name" style="padding-left:10px">Last Name: </label>
            </td>
            <td>""")
        reqhandler.response.out.write('<input type="text" name="last_name" value="%s" />' %
                                        nz(self.__customer.last_name))
        reqhandler.response.out.write("""
            </td>
            </tr>
            <tr>
            <td>
            <label for="address1">Address1: </label>
            </td>
            <td>""")
        reqhandler.response.out.write('<input type="text" name="address1" value="%s" />' %
                                        nz(self.__customer.address1))
        reqhandler.response.out.write("""
            </td>
            <td>
            <label for="city" style="padding-left:10px">City: </label>
            </td>
            <td>""")
        reqhandler.response.out.write('<input type="text" name="city" value="%s" />' %
                                        nz(self.__customer.city))
        reqhandler.response.out.write("""
            </td>
            </tr>
            <tr>
            <td>
            <label for="state">State: </label>
            </td>
            <td>""")
        reqhandler.response.out.write('<input type="text" name="state" value="%s" />' %
                                        nz(self.__customer.state))
        reqhandler.response.out.write("""
            </td>
            <td>
            <label for="zip" style="padding-left:10px">Zip: </label>
            </td>
            <td>""")
        reqhandler.response.out.write('<input type="text" name="zip" value="%s" />' %
                                        nz(self.__customer.zip))
        reqhandler.response.out.write("""
            </td>
            </tr>
            <tr>
            <td>
            <label for="phone1">Primary Phone: </label>
            </td>
            <td>""")
        reqhandler.response.out.write('<input type="text" name="phone1" value="%s" />' %
                                            nz(self.__customer.phone1))
        reqhandler.response.out.write("""
            </td>
            <td></td><td></td>
            </tr>""")
        if not self.__searchMode:
            reqhandler.response.out.write("""
            <tr><td colspan="4"><br />
            <label for="comments">Comments:</label><br />
            <textarea name="comments" rows="3" cols="60">""" + self.__customer.getComments() +  
              """</textarea>
            <p style="width:100%; text-align:center;"><input type="submit" name="submit_savecust" value="Save Customer Info" />
                <input type="submit" name="submit_resetcust_0" value="Reset Customer Info" />
            </p>
            </td></tr>
            </table>""")
        else:
            reqhandler.response.out.write("""
            <tr><td colspan="4">
            <p style="width:100%; text-align:center;">
                <input type="submit" name="submit_search" value="Find Customer(s)" />
                <input type="submit" name="submit_resetcust_1" value="Clear Customer Info" />
            </p>
            </td></tr>
            </table>""")
        return None
    
class VehicleSubview(object):
    def __init__(self):
        return None
    
    def _configure_content(self, vehicle_list):
        self.__vehicles = vehicle_list
        self.__vehicle = self.__vehicles[0]
        return None
    
    def _serve_content(self, reqhandler):
        reqhandler.response.out.write("""
            <p>
            <input class="tab_button" type="submit" name="submit_vtab_0" value="1999 Honda Accord" />
            <input class="tab_button" type="submit" name="submit_vtab_1" value="2008 Toyota Tercel" />
            <input class="selected_tab_button" type="submit" name="submit_vtab_2" value="New Vehicle" />
            </p>
            <table style="margin-top:15px; width:90%; margin-left:auto; margin-right:auto;">
            <tr>
            <td>
            <label for="make">Make: </label>
            </td>
            <td>""")
        reqhandler.response.out.write('<input type="text" name="make" value="%s" />' %
                                        nz(self.__vehicle.make))
        reqhandler.response.out.write("""
            </td>
            <td>
            <label for="model" style="padding-left:10px">Model: </label>
            </td>
            <td>""")
        reqhandler.response.out.write('<input type="text" name="model" value="%s" />' %
                                        nz(self.__vehicle.model))
        reqhandler.response.out.write("""
            </td>
            <td>
            <label for="year" style="padding-left:10px">Year: </label>
            </td>
            <td>""")
        reqhandler.response.out.write('<input type="text" name="year" size="8" value="%s" />' %
                                        nz(self.__vehicle.year))
        reqhandler.response.out.write("""
            </td>
            </tr>
            <tr>
            <td>
            <label for="license">License Plate: </label>
            </td>
            <td>""")
        reqhandler.response.out.write('<input type="text" name="license" value="%s" />' %
                                        nz(self.__vehicle.license))
        reqhandler.response.out.write("""
            <input type="hidden" name="mileage" value="150000" />
            </td>
            <td>
            <label for="vin" style="padding-left:10px">VIN: </label>
            </td>
            <td colspan="3">""")
        reqhandler.response.out.write('<input type="text" name="vin" size="40" value="%s" />' %
                                        nz(self.__vehicle.vin))
        reqhandler.response.out.write("""
            </td>
            </tr>
            <tr>
            <td colspan="6"><br />
            <label for="notes">Notes: </label><br />
            <textarea name="notes" rows="3" cols="65">""")
        reqhandler.response.out.write(nz(self.__vehicle.notes))
        reqhandler.response.out.write("""
            </textarea>
            </td>
            </tr>            
        """)
        reqhandler.response.out.write("""
            <tr><td colspan="3">
            <p style="width:100%; text-align:left;">
            <input type="submit" name="submit_savevhcl" value="Save Vehicle Info" />
            <input type="submit" name="submit_rstrvhcl" value="Clear Vehicle Info" />
            </p>
            </td><td colspan="3">
            <p style="width:100%; text-align:right;">
            <input type="submit" name="submit_newwo" value="New Work Order" />
            <input type="submit" name="submit_showwos" value="Show Work Order History" />
            </p>
            </td></tr>
            </table>
            """)
        return None
    
