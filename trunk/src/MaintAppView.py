'''
Created on May 25, 2009

@author: Brad Gaiser

This module provides a prototype implementation of the View in the MVC
implementation of the Maintenance Records System for Dermico Auto.  The
UI code is a bit more complex, so has taken more time to get into place
than anticipated.  As a consequence, this quick & dirty code was written
to provide a framework for integration testing and making sure that the
control flow managed by the Controller classes works.

This also is providing a 'spec' for the full implementation of the UI
using Django templates to be provided by Jerome Calvo.  This code has
been written with the intent that all if not most of the code will be
replaced.  As such, minimal effort has been put into documention.
'''

NEW_CUSTOMER = 1
FIND_CUSTOMER = 2
INPUT_CUSTOMER = 3
INPUT_WORKORDER = 4

from datetime import datetime
from MaintAppObjects import nz
from MaintAppObjects import Workorder

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
        self.__workorderPanel = WorkorderSubview()
        self.__mainMode = NEW_CUSTOMER
        return None
    
    def set_new_customer_mode(self):
        self.__mainMode = NEW_CUSTOMER
        self.__customerPanel._configure_input_mode()
    
    def set_search_mode(self):
        self.__mainMode = FIND_CUSTOMER
        self.__customerPanel._configure_search_mode()
        
    def set_search_results_mode(self):
        self.__mainMode = FIND_CUSTOMER
    
    def set_customer_vehicle_mode(self):
        self.__mainMode = INPUT_CUSTOMER
        self.__customerPanel._configure_input_mode()
        
    def set_workorder_mode(self):
        self.__mainMode = INPUT_WORKORDER
        
    def configureHiddenFields(self, customer_id, vehicle_id, workorder_id):
        self.__sidePanel._configure_hidden_fields(customer_id, vehicle_id, workorder_id)
        self.__vehiclePanel._configureActiveVehicle(vehicle_id)
        self.__workorderPanel._configureActiveWorkorder(workorder_id)
        
    def configureErrorMessages(self, errorObj):
        """ Errors is a list of (field name, error type) tuples to be used to format
            errors and highlighting fields where data validation errors were detected.
        """
        self.__sidePanel._configureErrorMessages(errorObj)
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
        self.__workorderPanel._configureHeader(customer, vehicle)
    
    def configureWorkorderContent(self, workorder_list):
        self.__workorderPanel._configureWorkorderContent(workorder_list)
    
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
        
        if self.__mainMode == INPUT_WORKORDER:
            if self.__workorderPanel is not None:
                self.__workorderPanel._serve_content(reqhandler)
        else:
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
        self.__errorObj = None
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
    
    def _configureErrorMessages(self, errorObj):
        self.__errorObj = errorObj
        
    def _serve_content(self, reqhandler):
        linkClass = "s_side_links"
        activeLinkClass = "s_active_side_links"
        
        reqhandler.response.out.write('<p><strong>Customer Input:</strong></p>')
        css_class = activeLinkClass if (self.__itemSelected == 1) else linkClass
        reqhandler.response.out.write('<p><input class="%s" type="submit" name="submit_newcust" value="Add New Customer" /></p>' % css_class)
        css_class = activeLinkClass if (self.__itemSelected == 2) else linkClass
        reqhandler.response.out.write('<p><input class="%s" type="submit" name="submit_findcust" value="Find Customer" /></p>' % css_class)
        reqhandler.response.out.write('<p><strong>Open Work Orders:</strong></p>')
        reqhandler.response.out.write('<p style="margin-left:15px;">No Open Work Orders</p>')
        reqhandler.response.out.write('<p><strong>Work Completed:</strong></p>')
        reqhandler.response.out.write('<p style="margin-left:15px;">No Completed Work Orders</p>')
        reqhandler.response.out.write('<hr />')
        reqhandler.response.out.write('<p><strong>App Info:</strong></p>')
        reqhandler.response.out.write('<p style="margin-left:15px;">%s</p>' % self.__comments)
        if self.__errorObj is not None:
            reqhandler.response.out.write('<p style="margin-left:15px; color:red;">%s</p>' % \
                                          str(self.__errorObj))        
        reqhandler.response.out.write('<input type="hidden" name="customer_id"  value="%s" />' % self.__customerId)
        reqhandler.response.out.write('<input type="hidden" name="vehicle_id"   value="%s" />' % self.__vehicleId)
        reqhandler.response.out.write('<input type="hidden" name="workorder_id" value="%s" />' % self.__workorderId)
        return None
    
        
class CustomerSubview(object):
    def __init__(self):
        self.__customer = None
        self.__searchMode = False
        self.__searchResults = None
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
            if self.__searchResults is not None:
                reqhandler.response.out.write("<hr \>")
                if len(self.__searchResults) == 0:
                    reqhandler.response.out.write("""
                    <p><strong>No customers match the search you requested.
                    </strong></p>""")
                else:
                    for customer in self.__searchResults:
                        link = "/Search?cid=%s" % customer.getId()
                        reqhandler.response.out.write( \
                            '<p><a href="%s">%s %s</a></p>' % \
                            (link, nz(customer.first_name), nz(customer.last_name)))
        return None
    
class VehicleSubview(object):
    def __init__(self):
        return None
    
    def _configureActiveVehicle(self, vehicle_id):
        self.__activeVehicleId = vehicle_id
    
    def _configure_content(self, vehicle_list):
        self.__vehicles = vehicle_list
        self.__vehicle = self.__vehicles[0]
        return None
    
    def __retrieveActiveVehicle(self):
        for eachVehicle in self.__vehicles:
            if eachVehicle.getId() == self.__activeVehicleId:
                self.__vehicle = eachVehicle
                break
        return None
    
    def _serve_content(self, reqhandler):
        self.__retrieveActiveVehicle()
        reqhandler.response.out.write('<div style="width:100%">')
        tabNum = -1
        for eachVehicle in self.__vehicles:
            tabNum += 1
            if eachVehicle.getId() == self.__activeVehicleId:
                style = "selected_tab_button"
            else:
                style = "tab_button"
            if eachVehicle.getId() == "-1":
                reqhandler.response.out.write( \
                    '<input class="%s" type="submit" name="submit_vtab_%d" value="New Vehicle" />' % \
                    (style, tabNum, ))
            else:
                reqhandler.response.out.write( \
                    '<input class="%s" type="submit" name="submit_vtab_%d" value="%s" />' % \
                    (style, tabNum, str(eachVehicle.year)))
        #<input class="tab_button" type="submit" name="submit_vtab_1" value="2008 Toyota Tercel" />
        #<input class="selected_tab_button" type="submit" name="submit_vtab_2" value="New Vehicle" />
        reqhandler.response.out.write("""
            <hr style="width=102%; margin-top:-1px; padding-top:0px; padding-bottom:0px;" />
            </div>
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
    
class WorkorderSubview(object):
    def __init__(self):
        self.__customer = None
        self.__vehicle = None
        self.__activeWorkorderId = None
        self.__workorders = None
        self.__workorder = None
        return None
    
    def _configureHeader(self, customer, vehicle):
        self.__customer = customer
        self.__vehicle = vehicle
        return None
    
    def _configureActiveWorkorder(self, workorder_id):
        self.__activeWorkorderId = workorder_id
        return None

    def _configureWorkorderContent(self, workorder_list):
        self.__workorders = workorder_list
        return None
    
    def __retrieveActiveWorkorder(self):
        for eachWorkorder in self.__workorders:
            if eachWorkorder.getId() == self.__activeWorkorderId:
                self.__workorder = eachWorkorder
                break
        return None
    
    def _serve_content(self, reqhandler):
        self.__retrieveActiveWorkorder()
        self.__output_workorder_header(reqhandler)
        self.__output_workorder_form(reqhandler)
        return None
    
    def __output_workorder_header(self, reqhandler):
        reqhandler.response.out.write("""
            <table>
            <tr>
                <td>
                    Customer info:
                </td>
                <td>""")
        reqhandler.response.out.write("%s %s; Contact: %s" %
                                      (nz(self.__customer.first_name),
                                       nz(self.__customer.last_name),
                                       nz(self.__customer.phone1)))
        reqhandler.response.out.write("""
                </td>
            </tr>
            <tr>
                <td>
                    Vehicle info:
                </td>
                <td>""")
        reqhandler.response.out.write("%s %s %s; License: %s" %
                                      (nz(self.__vehicle.year),
                                       nz(self.__vehicle.make),
                                       nz(self.__vehicle.model),
                                       nz(self.__vehicle.license)))
        reqhandler.response.out.write("""
                </td>
            </tr>
            </table>""")
        return None
    
    def __format_tabs(self, reqhandler):
        woIndex = -1
        for workorder in self.__workorders:
            woIndex += 1
            selClass = "selected_tab_button" if workorder.id==self.__activeWorkorderId \
                                             else "tab_button"
            if workorder.id == "-1":
                label = "New Work Order"
            else:
                label = workorder.date_created.strftime("%b %d, %Y")
            reqhandler.response.out.write( \
                '<input style="margin-top:25px;" class="%s" type="submit" name="submit_wotab_%d" value="%s" />' %
                    (selClass, woIndex, label))
    
    def __output_workorder_form(self, reqhandler):
        reqhandler.response.out.write('<div style="width:100%">')
        self.__format_tabs(reqhandler)
        #<input style="margin-top:25px;" class="selected_tab_button" type="submit" name="submit_wotab_0" value="New Workorder" />
        #<input class="tab_button" type="submit" name="submit_wotab_1" value="12-Dec-2008" />
        #<input class="tab_button" type="submit" name="submit_wotab_2" value="04-Mar-2009" />
        reqhandler.response.out.write('<hr style="width=100%; margin-top:-1px; padding-top:0px; padding-bottom:0px;" />')
        reqhandler.response.out.write('</div>')
        dateText = nz(self.__workorder.getDateCreated())
        reqhandler.response.out.write( \
            '<input type="hidden" name="date_created" value="%s" />' % \
            dateText)
        reqhandler.response.out.write("""
            <table style="margin-top:30px;">
                <tr>
                    <td>
                        Customer's Service Request:
                    </td>
                    <td style="text-align:right;">
                        <label for="mileage">Odometer Reading:</label>""")
        reqhandler.response.out.write( \
            '<input type="text" name="mileage" value="%s" />' % \
            nz(self.__workorder.mileage))
        reqhandler.response.out.write("""
                    </td>
                </tr>
                <tr>
                    <td colspan="2">
                        <textarea name="customer_request" rows="3" cols="85">""")
        reqhandler.response.out.write(nz(self.__workorder.customer_request))
        reqhandler.response.out.write("""
                        </textarea>
                    </td>
                </tr>
                <tr><td colspan="2"><hr /></td></tr>
                <tr>
                    <td>""")
        reqhandler.response.out.write( \
            "Work Order Date: %s" % dateText)
        reqhandler.response.out.write("""
                    </td>
                    <td style="text-align:right;">
                        <label for "mechanic">Mechanic:</label>
                        <select name="mechanic">
                        <option value="mechanic_0">Select...</option>""")
        reqhandler.response.out.write( \
            '<option value="mechanic_1"%s>Jerome Calvo</option>' % \
                (' selected="selected"' if self.__workorder.mechanic=="mechanic_1" else ""))
        reqhandler.response.out.write( \
            '<option value="mechanic_2"%s>Les Faby</option>' % \
                (' selected="selected"' if self.__workorder.mechanic=="mechanic_2" else ""))
        reqhandler.response.out.write( \
            '<option value="mechanic_3"%s>Brad Gaiser</option>' % \
                (' selected="selected"' if self.__workorder.mechanic=="mechanic_3" else ""))
        reqhandler.response.out.write( \
            '<option value="mechanic_4"%s>Wing Wong</option>' % \
                (' selected="selected"' if self.__workorder.mechanic=="mechanic_4" else ""))
        reqhandler.response.out.write("""
                        </select>
                    </td>
                </tr>
                <tr>
                    <td>
                        <label for "mechanics_tasks">Mechanics Tasks:</label><br />
                        <textarea name="task_list" rows="7" cols="40">""")
        reqhandler.response.out.write(nz(self.__workorder.task_list))
        reqhandler.response.out.write("""
                        </textarea>
                    </td>
                    <td>
                        <label for "work_done">Work Performed:</label><br />
                        <textarea name="work_performed" rows="7" cols="40">""")
        reqhandler.response.out.write(nz(self.__workorder.work_performed))
        reqhandler.response.out.write("""
                        </textarea>
                    </td>
                </tr>
                <tr>
                    <td colspan="2">
                        <label for "next_service">Notes and next service recommendations:</label><br />
                        <textarea name="notes" rows="4" cols="85">""")
        reqhandler.response.out.write(nz(self.__workorder.notes))
        reqhandler.response.out.write("""
                        </textarea>
                    </td>
                </tr>
                <tr>
                    <td colspan="2" style="text-align:center;">
                        <label for "status">Work Order Status:</label>""")
        reqhandler.response.out.write( \
            '<input style="margin-left:15px;" type="radio" name="status" value="Open" %s /> Open' % \
                ('checked="checked"' if self.__workorder.status == Workorder.OPEN else ''))
        reqhandler.response.out.write( \
            '<input style="margin-left:25px;" type="radio" name="status" value="Completed" %s /> Completed' % \
                ('checked="checked"' if self.__workorder.status == Workorder.COMPLETED else ''))
        reqhandler.response.out.write( \
            '<input style="margin-left:15px;" type="radio" name="status" value="Closed" %s /> Closed' % \
                ('checked="checked"' if self.__workorder.status == Workorder.CLOSED else ''))
        reqhandler.response.out.write("""
                    </td>
                </tr>
                <tr>
                    <td colspan="2">
                        <p style="width:100%; text-align:center;">
                        <input type="submit" name="submit_savewo" value="Save Work Order" />
                        <input type="submit" name="submit_rstrwo" value="Restore Work Order" />
                        </p>
                    </td>
                </tr>
            </table>""")
        return None
    