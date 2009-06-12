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

import os, sys
from google.appengine.ext.webapp import template
from MaintAppObjects import Workorder
import Utilities


def doRender(handler,temp,dict):
    path = os.path.join ( os.path.dirname(__file__), 'templates/' + temp + '.html' )
    outstr = template.render ( path, dict )
    handler.response.out.write(outstr)
    
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
        self.__dialogPanel = None
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
        self.__customerPanel._configure_display_mode()
        
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
        self.__dialogPanel = DialogSubview(request_button, request_tag)
        return None
    
    def serve_content(self, reqhandler):         
        self.__serve_header(reqhandler)
        reqhandler.response.out.write("""
          <body>
            <form action="/Customer" method="post">
        """)         
        if self.__dialogPanel is not None:
            self.__dialogPanel._serve_content(reqhandler)
        reqhandler.response.out.write("""
              <table class="my_table">
                <tr>
                  <td rowspan="2" class="my_tleft">""")       
        #doRender (reqhandler, 'top', {})   #moving html to templates         
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
        #doRender(reqhandler, 'bottom', {})
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
        self.__openWorkorders = openWorkorders
        self.__completedWorkorders = completedWorkorders
        self.__comments = debug_message
        
    def _configure_hidden_fields(self, customer_id, vehicle_id, workorder_id):
        self.__customerId = customer_id
        self.__vehicleId = vehicle_id
        self.__workorderId = workorder_id
        return None
    
    def _configureErrorMessages(self, errorObj):
        self.__errorObj = errorObj
        
    def __serve_workorderList(self, reqhandler, woList):
        reqhandler.response.out.write("<div>\n")
        for pair in woList:
            vehicle = pair[0]
            workorder = pair[1]
            #sys.stderr.write(str(vehicle))
            #sys.stderr.write(str(workorder) + "\n")
            if vehicle is not None:
                if workorder.getId() == self.__workorderId:
                    button_class = "s_active_side_wo"
                else:
                    button_class = "s_side_wo"
                reqhandler.response.out.write( \
                    '<input class="%s" type="submit" name="submit_activewo_%s" value="%s %s %s, \nLic# %s" />' % \
                    (button_class, workorder.getId(), vehicle.year, vehicle.make, vehicle.model, vehicle.license))
        reqhandler.response.out.write("</div>\n")
        return None
        
    def _serve_content(self, reqhandler):
        linkClass = "s_side_links"
        activeLinkClass = "s_active_side_links"
        
        reqhandler.response.out.write('<p><strong>Customer Input:</strong></p>')
        css_class = activeLinkClass if (self.__itemSelected == 1) else linkClass
        reqhandler.response.out.write('<p><input class="%s" type="submit" name="submit_newcust" value="Add New Customer" /></p>' % css_class)
        css_class = activeLinkClass if (self.__itemSelected == 2) else linkClass
        reqhandler.response.out.write('<p><input class="%s" type="submit" name="submit_findcust" value="Find Customer" /></p>' % css_class)
        reqhandler.response.out.write('<p><strong>Open Work Orders:</strong></p>')
        if len(self.__openWorkorders) == 0: 
            reqhandler.response.out.write('<p style="margin-left:15px;">No Open Work Orders</p>')
        else:
            self.__serve_workorderList(reqhandler, self.__openWorkorders)
        reqhandler.response.out.write('<p><strong>Work Completed:</strong></p>')
        if len(self.__completedWorkorders) == 0: 
            reqhandler.response.out.write('<p style="margin-left:15px;">No Completed Work Orders</p>')
        else:
            self.__serve_workorderList(reqhandler, self.__completedWorkorders)
        reqhandler.response.out.write('<hr />')
        reqhandler.response.out.write('<p><strong>App Info:</strong></p>')
        reqhandler.response.out.write('<p style="margin-left:15px;">%s</p>' % self.__comments)
        if self.__errorObj is not None:
            errors = "<br />".join(str(self.__errorObj).split("\n"))
            reqhandler.response.out.write( \
                '<p style="margin-left:15px; color:red;">%s</p>' % errors)        
        reqhandler.response.out.write('<input type="hidden" name="customer_id"  value="%s" />' % self.__customerId)
        reqhandler.response.out.write('<input type="hidden" name="vehicle_id"   value="%s" />' % self.__vehicleId)
        reqhandler.response.out.write('<input type="hidden" name="workorder_id" value="%s" />' % self.__workorderId)
        return None
    
        
class CustomerSubview(object):
    def __init__(self):
        self.__customer = None
        self.__searchMode = False
        self.__dispMode = False
        self.__searchResults = None
        return None
    
    def _configure_content(self, customerInfo):
        self.__customer = customerInfo
        return None
    
    def _configure_search_mode(self):
        self.__searchMode = True
        self.__displayMode = False
        return None
    
    def _configure_input_mode(self):
        self.__searchMode = False
        self.__displayMode = False
        return None
    
    def _configure_display_mode(self):
        self.__searchMode = False
        self.__displayMode = True
        return None
 
    
    def _configure_search_results(self, customer_list):
        self.__searchMode = True
        self__displayMode = False
        self.__searchResults = customer_list
        return None

    def _serve_content_old(self, reqhandler):
        """ Uses template customerSubview.html and its children to compose and display customer info sub view
            as well as search results while in find mode 
        """ 
        tempValuesDict = {'customer_first_name':self.__customer.first_name,
                'customer_last_name':self.__customer.last_name,
                'customer_address1':self.__customer.address1,
                'customer_address2':self.__customer.address2,
                'customer_city':self.__customer.city,
                'customer_state':self.__customer.state,
                'customer_zip':self.__customer.zip,
                'customer_phone1':self.__customer.phone1,
                'customer_phone2':self.__customer.phone2,
                'customer_email':self.__customer.email,
                'customer_comments': self.__customer.comments
                }
              
        if (self.__searchMode == False):
            if self.__displayMode:
                doRender (reqhandler, 'customerSubviewDispCust', tempValuesDict)
            else:
                doRender (reqhandler, 'customerSubviewNewCust', tempValuesDict)
        else: 
            doRender (reqhandler, 'customerSubviewFindCust', tempValuesDict) 
            if self.__searchResults is not None:          
                tempValuesDict = { 'customers':self.__searchResults }    
                doRender (reqhandler, 'customerSearchResults', tempValuesDict)
        return None
    
    def _serve_content(self, reqhandler):
        """ Uses template customerSubview.html and its children to compose and display customer info sub view
            as well as search results when in find mode 
        """            
        if ( self.__customer.getId() == "-1" ):
            tempValuesDict = {}  # take care of None values if database object is empty.
        else:
            tempValuesDict = { 'customer':self.__customer }              
        if (self.__searchMode == False):
            if self.__displayMode:
                doRender (reqhandler, 'customerSubviewDispCust', tempValuesDict)
            else:
                doRender (reqhandler, 'customerSubviewNewCust', tempValuesDict)
        else: 
            doRender (reqhandler, 'customerSubviewFindCust', tempValuesDict) 
            if self.__searchResults is not None:          
                tempValuesDict = { 'customers':self.__searchResults }    
                doRender (reqhandler, 'customerSearchResults', tempValuesDict)
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
    
    def _serve_content_old(self, reqhandler):
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
                                        self.__vehicle.make)
        reqhandler.response.out.write("""
            </td>
            <td>
            <label for="model" style="padding-left:10px">Model: </label>
            </td>
            <td>""")
        reqhandler.response.out.write('<input type="text" name="model" value="%s" />' %
                                        self.__vehicle.model)
        reqhandler.response.out.write("""
            </td>
            <td>
            <label for="year" style="padding-left:10px">Year: </label>
            </td>
            <td>""")
        reqhandler.response.out.write('<input type="text" name="year" size="8" value="%s" />' %
                                        self.__vehicle.year)
        reqhandler.response.out.write("""
            </td>
            </tr>
            <tr>
            <td>
            <label for="license">License Plate: </label>
            </td>
            <td>""")
        reqhandler.response.out.write('<input type="text" name="license" value="%s" />' %
                                        self.__vehicle.license)
        reqhandler.response.out.write("""
            <input type="hidden" name="mileage" value="150000" />
            </td>
            <td>
            <label for="vin" style="padding-left:10px">VIN: </label>
            </td>
            <td colspan="3">""")
        reqhandler.response.out.write('<input type="text" name="vin" size="40" value="%s" />' %
                                        self.__vehicle.vin)
        reqhandler.response.out.write("""
            </td>
            </tr>
            <tr>
            <td colspan="6"><br />
            <label for="notes">Notes: </label><br />
            <textarea name="notes" rows="3" cols="65">""")
        reqhandler.response.out.write(self.__vehicle.notes)
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
            </div>""")
        if ( self.__vehicle.getId() == "-1" ):
            tempValuesDict = {}
        else:
            tempValuesDict = { 'vehicle':self.__vehicle }    
        doRender (reqhandler, 'vehicleSubview', tempValuesDict)       
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
                                      (self.__customer.first_name,
                                       self.__customer.last_name,
                                       self.__customer.phone1))
        reqhandler.response.out.write("""
                </td>
            </tr>
            <tr>
                <td>
                    Vehicle info:
                </td>
                <td>""")
        reqhandler.response.out.write("%s %s %s; License: %s" %
                                      (self.__vehicle.year,
                                       self.__vehicle.make,
                                       self.__vehicle.model,
                                       self.__vehicle.license))
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
                label = Utilities.shortDate(workorder.date_created)
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
        dateText = self.__workorder.getDateCreated() # Reused below for visible text
        reqhandler.response.out.write( \
            '<input type="hidden" name="date_created" value="%s" />' % \
            dateText)
        reqhandler.response.out.write( \
            '<input type="hidden" name="date_closed" value="%s" />' % \
            self.__workorder.getDateClosed())
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
            self.__workorder.mileage)
        reqhandler.response.out.write("""
                    </td>
                </tr>
                <tr>
                    <td colspan="2">
                        <textarea name="customer_request" rows="3" cols="85">""")
        reqhandler.response.out.write(self.__workorder.customer_request)
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
                        <select name="mechanic">""")
        reqhandler.response.out.write( \
            '<option value="%s">Select...</option>' % Workorder.NO_MECHANIC)
        reqhandler.response.out.write( \
            '<option value="Jerome Calvo"%s>Jerome Calvo</option>' % \
                (' selected="selected"' if self.__workorder.mechanic=="Jerome Calvo" else ""))
        reqhandler.response.out.write( \
            '<option value="Les Faby"%s>Les Faby</option>' % \
                (' selected="selected"' if self.__workorder.mechanic=="Les Faby" else ""))
        reqhandler.response.out.write( \
            '<option value="Brad Gaiser"%s>Brad Gaiser</option>' % \
                (' selected="selected"' if self.__workorder.mechanic=="Brad Gaiser" else ""))
        reqhandler.response.out.write( \
            '<option value="Wing Wong"%s>Wing Wong</option>' % \
                (' selected="selected"' if self.__workorder.mechanic=="Wing Wong" else ""))
        reqhandler.response.out.write("""
                        </select>
                    </td>
                </tr>
                <tr>
                    <td>
                        <label for "mechanics_tasks">Mechanics Tasks:</label><br />
                        <textarea name="task_list" rows="7" cols="40">""")
        reqhandler.response.out.write(self.__workorder.task_list)
        reqhandler.response.out.write("""
                        </textarea>
                    </td>
                    <td>
                        <label for "work_done">Work Performed:</label><br />
                        <textarea name="work_performed" rows="7" cols="40">""")
        reqhandler.response.out.write(self.__workorder.work_performed)
        reqhandler.response.out.write("""
                        </textarea>
                    </td>
                </tr>
                <tr>
                    <td colspan="2">
                        <label for "next_service">Notes and next service recommendations:</label><br />
                        <textarea name="notes" rows="4" cols="85">""")
        reqhandler.response.out.write(self.__workorder.notes)
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

class DialogSubview(object):
    def __init__(self, request_button, request_tag):
        self.__request_button = request_button
        self.__request_tag = request_tag
        return None
    
    def _serve_content(self, reqhandler):
        dialogTemp = os.path.join ( os.path.dirname(__file__), 'templates/dialogTemplate.html' )
        tempValuesDict = {'request_button':self.__request_button,
                          'request_tag':self.__request_tag }
                
        outstr = template.render ( dialogTemp, tempValuesDict )
        reqhandler.response.out.write(outstr)
        return None
    
    