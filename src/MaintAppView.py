'''
Created on May 25, 2009

@author: Brad Gaiser, Jerome Calvo

This module provides a prototype implementation of the View in the MVC
implementation of the Maintenance Records System for Dermico Auto.  The
UI code is a bit more complex, so has taken more time to get into place
than anticipated.  As a consequence, this quick & dirty code was written
to provide a framework for integration testing and making sure that the
control flow managed by the Controller classes works.

This also is providing a 'spec' for the full implementation of the UI
using Django templates to be provided by Jerome Calvo.  This code has
been written with the intent that all if not most of the code will be
replaced.  As such, minimal effort has been put into documentation.

06/12/09 Template code for customerSubview and vehicleSubview completed
         with support for error handling
06/13/09 Template code for workorderSubview Header and Form completed
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
    """ Helper function rendering a template given a template name and
        a dictionary of values.
    """
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
        self.__customerPanel._configureErrorFields(errorObj.getFieldsWithErrors())
        self.__vehiclePanel._configureErrorFields(errorObj.getFieldsWithErrors())
        self.__sidePanel._configureErrorMessages(errorObj)
        
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
    
    def configureWorkorderCount(self, workorder_count):
        self.__vehiclePanel._configure_workorder_count(workorder_count)
        
    def configureWorkorderStatus(self, has_unclosed_workorder):
        self.__vehiclePanel._configure_workorder_status(has_unclosed_workorder)
        
    def configureWorkorderHeader(self, customer, vehicle):
        self.__workorderPanel._configureHeader(customer, vehicle)
    
    def configureWorkorderContent(self, mechanics, workorder_list):
        self.__workorderPanel._configureWorkorderContent(mechanics, workorder_list)
    
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
        #doRender (reqhandler, 'top', dict)   #moving some html code to templates         
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
                '<p style="margin-left:15px; color:red; font-weight:bold">%s</p>' % errors)        
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
        self.__errorFields = None
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

    def _configureErrorFields(self, error_fields):
        self.__errorFields = error_fields
        return None
        
    def _serve_content(self, reqhandler):
        """ Uses template customerSubview.html and its children to compose and display customer info sub view
            as well as search results when in find mode 
        """            
        tempValuesDict = { 'customer':self.__customer }                                
        if self.__errorFields is not None:
            for field in self.__errorFields:
                tempValuesDict["e_" + field] = True                
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
        self.__errorFields = None
        self.__workorderCount = 0
        self.__hasUnclosedWorkorder = False
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
    
    def _configureErrorFields(self, error_fields):
        self.__errorFields = error_fields
        return None

    def _configure_workorder_count(self, workorder_count):
        self.__workorderCount = workorder_count
        return None
    
    def _configure_workorder_status(self, has_unclosed_workorder):
        self.__hasUnclosedWorkorder = has_unclosed_workorder
        
    def _serve_content(self, reqhandler):
        self.__retrieveActiveVehicle()
        tabNum = -1       
        tabs=[]
        for eachVehicle in self.__vehicles:
            tab = {}
            tabNum += 1
            tab['num'] = tabNum
            if eachVehicle.getId() == self.__activeVehicleId:
                tab['style'] = "selected_tab_button"
            else:
                tab['style'] = "tab_button"
            if eachVehicle.getId() == "-1":
                tab['vehicle'] = "New Vehicle"
            else:
                tab['vehicle'] = "%s %s %s" % (str(eachVehicle.year),\
                                               str(eachVehicle.make),\
                                               str(eachVehicle.model))
            tabs.append(tab)
        tempValuesDict = { 'tabs':tabs }
        if self.__errorFields is not None:
            for field in self.__errorFields:
                tempValuesDict["e_" + field] = True                
        tempValuesDict ['vehicle' ] = self.__vehicle  
        tempValuesDict['workorder_unavail'] = (self.__workorderCount == 0)
        tempValuesDict['new_wo_button_inactive'] = \
            (self.__activeVehicleId == "-1") or self.__hasUnclosedWorkorder
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

    def _configureWorkorderContent(self, mechanics, workorder_list):
        self.__mechanics = mechanics
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
        tempValuesDict = { 'customer':self.__customer, 'vehicle':self.__vehicle }    
        doRender (reqhandler, 'workorderSubviewHeader', tempValuesDict)      
        return None
    
    def __format_tabs_old(self, reqhandler):
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

    def __format_tabs(self, reqhandler):
        """ templatized! """
        woIndex = -1
        tabs=[]
        for workorder in self.__workorders:
            tab={}
            woIndex += 1
            tab['num'] = woIndex
            tab['style'] = "selected_tab_button" if ( workorder.id==self.__activeWorkorderId ) \
                                             else "tab_button"
            tab['label'] = "New Work Order" if ( workorder.id == "-1" ) \
                                        else Utilities.shortDate(workorder.date_created)           
            tabs.append(tab)
        tempValuesDict = { 'tabs':tabs }
        doRender( reqhandler, 'workorderSubviewTabs', tempValuesDict )

    def __output_workorder_form(self, reqhandler):
        #reqhandler.response.out.write('<div style="width:100%">')
        self.__format_tabs(reqhandler)
        #reqhandler.response.out.write('<hr style="width=100%; margin-top:-1px; padding-top:0px; padding-bottom:0px;" />')
        #reqhandler.response.out.write('</div>')        
        tempValuesDict = { 'date_created':self.__workorder.getDateCreated(),
                          'date_closed':self.__workorder.getDateClosed() }
        """ 
        mechanics = [{ 'value':Workorder.NO_MECHANIC,'name':'Select...' },
                     { 'value':'Jerome Calvo','name':'Jerome Calvo' },
                     { 'value':'Les Faby','name':'Les Faby' },
                     { 'value':'Brad Gaiser','name':'Brad Gaiser' },
                     { 'value':'Win Wong','name':'Win Wong' },]
        """
                     
        """ Code to support a list of Mechanics.
            Another way will be to inject {'value':Workorder.NO_MECHANIC,'name':'Select...'}
            for the first input (value,name) and {'mechanics':self.__mechanics} for the rest
            of the drop down list with associated changes in the form template. """
        
        mechanics =[{'value':mechanic,'name':mechanic} for mechanic in self.__mechanics]
        mechanics.insert(0, { 'value':Workorder.NO_MECHANIC,'name':'Select...' })        
        tempValuesDict ['mechanics'] = mechanics
        tempValuesDict ['workorder'] = self.__workorder
        doRender( reqhandler,'workorderSubviewForm', tempValuesDict )
        return None

class DialogSubview(object):
    def __init__(self, request_button, request_tag):
        self.__request_button = request_button
        self.__request_tag = request_tag
        return None
    
    def _serve_content(self, reqhandler):
        tempValuesDict = { 'request_button':self.__request_button,
                          'request_tag':self.__request_tag }
        doRender( reqhandler,"dialogTemplate",tempValuesDict )
        return None
    
    
