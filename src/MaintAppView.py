'''
Created on May 25, 2009

@author: Brad Gaiser, Jerome Calvo

This module was first implemented as a prototype of the View in the MVC
implementation of the Maintenance Records System for Dermico Auto.
The code was written to provide a framework for integration testing and 
making sure that the control flow managed by the Controller classes works.

The current version has been partially re-written to support a set of templates
(available in the /templates directory) and using a subset of the Django
templating engine bundled with Google App Engine.


06/12/09 Template code for customerSubview and vehicleSubview completed
         with support for error handling
06/13/09 Template code for workorderSubview Header and Form completed
06/14/09 Template code for workorderSubview Tab completed
06/15/09 Added support for drop-down menu with list of States in 
         customerSubview.html
06/16/09 Added validation error handling in workorderSubviewForm
         Added handling of former mechanic no longer in the mechanic list.
06/17/09 Fixed issue with None value in mechanic list
06/18/09 Moved some HTML code from MaintAppView() to templates 'top.html'
         and 'bottom.html'.
         Added display of Python version and Server Software info.
'''


""" UI modes """
NEW_CUSTOMER = 1
FIND_CUSTOMER = 2
INPUT_CUSTOMER = 3
INPUT_WORKORDER = 4

import os, sys
from google.appengine.ext.webapp import template
from MaintAppObjects import Workorder
import Utilities


def doRender(handler,temp,dict):
    """ Helper function rendering a template given 'temp' a template name and
        'dict' a dictionary of place holder names matching the template design
        and their corresponding values. 
        Format for 'temp':
        If template name is 'my_template.html' then temp = "my_template"       
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
        """ Constructor for MaintAppView(). Initialize state of the main screen UI
            when called by the controller"
        """
        self.__macController = controller
        self.__sidePanel = SidePanelSubview()
        self.__customerPanel = CustomerSubview()
        self.__vehiclePanel = VehicleSubview()
        self.__workorderPanel = WorkorderSubview()
        self.__dialogPanel = None
        self.__mainMode = NEW_CUSTOMER
        return None
    
    def set_new_customer_mode(self):
        """ set UI to New Customer mode 
        """
        self.__mainMode = NEW_CUSTOMER
        self.__customerPanel._configure_input_mode()
    
    def set_search_mode(self):
        """ set UI to Find Customer mode 
        """
        self.__mainMode = FIND_CUSTOMER
        self.__customerPanel._configure_search_mode()
        
    def set_search_results_mode(self):
        """ Set UI to Search Results mode 
        """
        self.__mainMode = FIND_CUSTOMER
    
    def set_customer_vehicle_mode(self):
        """ Set UI to Vehicle mode 
        """
        self.__mainMode = INPUT_CUSTOMER
        self.__customerPanel._configure_display_mode()
        
    def set_workorder_mode(self):
        """ Set UI to Work order mode 
        """
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
        self.__workorderPanel._configureErrorFields(errorObj.getFieldsWithErrors())
        self.__sidePanel._configureErrorMessages(errorObj)
        
    def configureDuplicateCustomerMessage(self, errorObj):
        """ Set up to report duplicate customer information to user. 
        """
        self.__customerPanel._configureDuplicateCustomerMessage(errorObj.getDuplicateCustomer())
        self.__sidePanel._configureErrorMessages(errorObj)
        
    def configureSidePanelContent(self, activeElement,
                                  openWorkorders,
                                  completedWorkorders,
                                  debug_message):
        """ Configure the Side Panel on the left side of the main screen 
            with active buttons, list of open and completed orders, and
            validation error messages.
        """
        self.__sidePanel._configure_selection(activeElement)
        self.__sidePanel._configure_content(openWorkorders, 
                                            completedWorkorders, 
                                            debug_message)
        
    def configureCustomerContent(self, customer_info):
        """ Configure Customer Subview with customer data passed by 
            the controller.
        """
        self.__customerPanel._configure_content(customer_info)

    def configureSearchResults(self, customer_list):
        """ Configure Customer Subview with customer list passed by 
            the controller as the result of Find Customer operation.
        """
        self.__customerPanel._configure_search_results(customer_list)
        
    def configureVehicleContent(self, vehicle_list):
        """ Configure Vehicle Subview with a vehicle list for a given customer.
        """
        self.__vehiclePanel._configure_content(vehicle_list)
    
    def configureWorkorderCount(self, workorder_count):
        """ Configure Vehicle Subview with # of work orders
        """
        self.__vehiclePanel._configure_workorder_count(workorder_count)
        
    def configureWorkorderStatus(self, has_unclosed_workorder):
        self.__vehiclePanel._configure_workorder_status(has_unclosed_workorder)
        """ Configure Vehicle Subview with work orders status
        """
        
    def configureWorkorderHeader(self, customer, vehicle):
        self.__workorderPanel._configureHeader(customer, vehicle)
        """ Configure Work order Subview header with data from a given customer 
            and vehicle.
        """
    
    def configureWorkorderContent(self, mechanics, workorder_list):
        self.__workorderPanel._configureWorkorderContent(mechanics, workorder_list)
        """ Configure Work order Subview with data from a list of work orders for
            a given customer and vehicle.
        """

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
    
    def reportInternalError(self, reqhandler, errorMessage):
        """ Display error message and Traceback in case of internal error not
            trapped elsewhere
        """
        dict = {'error_message':errorMessage}
        doRender(reqhandler, 'internalError', dict)
        return None
    
    def serve_content(self, reqhandler): 
        """ Configure main screen UI based on UI modes:
            NEW_CUSTOMER, FIND_CUSTOMER, INPUT_CUSTOMER and,
            INPUT_WORKORDER      
        """  
         # moving some html code to templates      
        doRender (reqhandler, 'top', {})
        #               
        if self.__dialogPanel is not None:
            self.__dialogPanel._serve_content(reqhandler)
        rowspan = (2 if self.__mainMode == INPUT_CUSTOMER else 1)
        reqhandler.response.out.write("""
              <table class="my_table">
                <tr>""")
        reqhandler.response.out.write('<td rowspan="%d" class="my_tleft">' % rowspan)       
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
        #moving some html code to templates            
        tempValuesDict = { 'server_software': os.environ['SERVER_SOFTWARE'],
                          'python_version': sys.version }                          
        doRender(reqhandler, 'bottom', tempValuesDict)   
        #
        return None
    
class SidePanelSubview(object):
    """ Configure and render content of the Side Panel Subview on the left side
        of the main screen UI
    """
    def __init__(self):
        """ 
        Constructor for SidePanelSubview(). Initialize Side Panel UI
        with default values.
        """
        self.__itemSelected = 1  # New Customer
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
        """ Configure Side Panel with open and completed work orders and validation
            error messages if any.
        """
        self.__openWorkorders = openWorkorders
        self.__completedWorkorders = completedWorkorders
        self.__comments = debug_message
        
    def _configure_hidden_fields(self, customer_id, vehicle_id, workorder_id):
        """ Configure hidden field in form """
        self.__customerId = customer_id
        self.__vehicleId = vehicle_id
        self.__workorderId = workorder_id
        return None
    
    def _configureErrorMessages(self, errorObj):
        """ Get error messages if any. 
        """
        self.__errorObj = errorObj
        
    def __build_workorderList(self, reqhandler, woList):
        """ Build from woList a list of dictionaries to be used by
            template sidePanelSubview.html to display Open and 
            Completed work orders in the side panel.
            Return 'workorders', a list of dictionaries.
        """
        workorders = []
        if len(woList) != 0:
            for pair in woList:
                vehicle = pair[0]
                workorder = pair[1]
                if vehicle is not None:
                    if workorder.getId() == self.__workorderId:
                        button_class = "s_active_side_wo"
                    else:
                        button_class = "s_side_wo"              
                    workorders.append({"button_class":button_class, "id":workorder.getId(),\
                                       "vehicle_info": "%s %s %s, \nLic# %s" % \
                                       (vehicle.year,vehicle.make, vehicle.model, vehicle.license) })
        return workorders
         
    def _serve_content(self, reqhandler):
        """ Uses template sidePanelSubview.html to compose and display the side panel
            with 3 sections:
            - Buttons New & Find Customer
            - Open & Completed work orders
            - Messages: Application state and validation errors
            and 3 hidden fields.
        """
        # Buttons New & Find Customer
        linkClass = "s_side_links"
        activeLinkClass = "s_active_side_links"        
        tempValuesDict = { 'new_css_class':(activeLinkClass if (self.__itemSelected == 1) else linkClass),
                          'find_css_class':(activeLinkClass if (self.__itemSelected == 2) else linkClass) }
        # Open & completed work orders
        tempValuesDict['openWos'] = self.__build_workorderList(reqhandler, self.__openWorkorders)
        tempValuesDict['completedWos'] = self.__build_workorderList(reqhandler, self.__completedWorkorders)
        # Application state & validation error messages
        errors = ""
        if self.__errorObj is not None:
            errors = str(self.__errorObj)
        tempValuesDict['comments'] = self.__comments
        tempValuesDict['errors'] = errors
        tempValuesDict['customerId'] = self.__customerId
        tempValuesDict['vehicleId'] = self.__vehicleId
        tempValuesDict['workorderId'] = self.__workorderId
        doRender( reqhandler, 'sidePanelSubview', tempValuesDict )
        return None   
        
class CustomerSubview(object):
    """ Configure and render content of the Customer Subview on the top right
        side of the main screen UI
    """
    def __init__(self):
        """ Constructor for CustomerSubview(). Initialize Customer subview
            UI with default state and values.
        """
        self.__customer = None
        self.__searchMode = False
        self.__dispMode = False
        self.__searchResults = None
        self.__errorFields = None
        self.__duplicateCustomerInfo = None
        return None
    
    def _configure_content(self, customerInfo):
        """ Configure UI with content from customer data """
        self.__customer = customerInfo
        return None
    
    def _configure_search_mode(self):
        """ Configure UI for search mode """
        self.__searchMode = True
        self.__displayMode = False
        return None
    
    def _configure_input_mode(self):
        """ Configure UI for input mode (New Customer input or edit mode for 
            existing customer data)
        """
        self.__searchMode = False
        self.__displayMode = False
        return None
    
    def _configure_display_mode(self):
        """ Configure UI for display mode.
        """
        self.__searchMode = False
        self.__displayMode = True
        return None
 
    def _configure_search_results(self, customer_list):
        """ Configure UI for displaying search results after a 'Find Customer'
            request.
        """
        self.__searchMode = True
        self__displayMode = False
        self.__searchResults = customer_list
        return None

    def _configureErrorFields(self, error_fields):
        """ Get list of fields with validation error if any 
        """
        self.__errorFields = error_fields
        return None
    
    def _configureDuplicateCustomerMessage(self, duplicateCustomerInfo):
        """ Get duplicate customer info after New Customer input 
        """
        self.__duplicateCustomerInfo = duplicateCustomerInfo
        
    def _serve_content(self, reqhandler):
        """ Uses template customerSubview.html and its children to compose and display customer info sub view
            as well as search results when in find mode.  
        """
        states =  ('AA', 'AE', 'AK', 'AL', 'AP', 'AR', 'AS', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'FM', 'GA', \
                   'GU', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MH', 'MI', 'MN', 'MO', \
                   'MP', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'PR', \
                   'PW', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VI', 'VT', 'WA', 'WI', 'WV', 'WY')         
        tempValuesDict = { 'customer':self.__customer }    
        tempValuesDict['states'] = states                         
        if self.__errorFields is not None:
            for field in self.__errorFields:
                tempValuesDict["e_" + field] = True                
        if (self.__searchMode == False):
            if self.__displayMode:
                doRender (reqhandler, 'customerSubviewDispCust', tempValuesDict)
            else:
                doRender (reqhandler, 'customerSubviewNewCust', tempValuesDict)
                if  self.__duplicateCustomerInfo is not None:
                    tempValuesDict['dupCustomer'] = self.__duplicateCustomerInfo
                    doRender (reqhandler, 'customerSubviewDupCust', tempValuesDict)
        else: 
            doRender (reqhandler, 'customerSubviewFindCust', tempValuesDict) 
            if self.__searchResults is not None:          
                tempValuesDict = { 'customers':self.__searchResults }    
                doRender (reqhandler, 'customerSearchResults', tempValuesDict)
        return None
   
class VehicleSubview(object):
    """ Configure and render content of the Vehicle Subview under Customer panel
        of the main screen UI
    """
    def __init__(self):
        """ Constructor for VehicleSubview(). Initialize UI with default values
        """
        self.__errorFields = None
        self.__workorderCount = 0
        self.__hasUnclosedWorkorder = False
        return None
    
    def _configureActiveVehicle(self, vehicle_id):
        """ Get Id for active vehicle """
        self.__activeVehicleId = vehicle_id
    
    def _configure_content(self, vehicle_list):
        """ Set content for list of vehicle from 'vehicle_list'
        """
        self.__vehicles = vehicle_list
        self.__vehicle = self.__vehicles[0]
        return None
    
    def __retrieveActiveVehicle(self):
        """ Get data for active vehicle. 
        """
        for eachVehicle in self.__vehicles:
            if eachVehicle.getId() == self.__activeVehicleId:
                self.__vehicle = eachVehicle
                break
        return None
    
    def _configureErrorFields(self, error_fields):
        """ Get list of fields with validation error if any
        """
        self.__errorFields = error_fields
        return None

    def _configure_workorder_count(self, workorder_count):
        """ Get # of work orders for given vehicle
        """
        self.__workorderCount = workorder_count
        return None
    
    def _configure_workorder_status(self, has_unclosed_workorder):
        """ Get work order status for given vehicle
        """
        self.__hasUnclosedWorkorder = has_unclosed_workorder
        
    def _serve_content(self, reqhandler):
        """ Uses template vehicleSubview.html to compose and display vehicle info
        """
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
    """ Configure and render content of the Workorder Subview on the right side
        of main screen UI.
    """
    def __init__(self):
        """ Constructor for WorkorderSubview(). Initialize UI with default values
        """
        self.__customer = None
        self.__vehicle = None
        self.__activeWorkorderId = None
        self.__errorFields = None
        self.__workorders = None
        self.__workorder = None
        return None
    
    def _configureHeader(self, customer, vehicle):
        """ Configure subview UI with data from a given customer 
            and vehicle.
        """
        self.__customer = customer
        self.__vehicle = vehicle
        return None
    
    def _configureActiveWorkorder(self, workorder_id):
        """ Set active work order
        """
        self.__activeWorkorderId = workorder_id
        return None

    def _configureWorkorderContent(self, mechanics, workorder_list):
        """ Set content for list of vehicle from 'vehicle_list' and a list
            of mechanic's names
        """

        self.__mechanics = mechanics
        self.__workorders = workorder_list
        return None
    
    def __retrieveActiveWorkorder(self):
        """ Retrieve active work order data.
        """
        for eachWorkorder in self.__workorders:
            if eachWorkorder.getId() == self.__activeWorkorderId:
                self.__workorder = eachWorkorder
                break
        return None
    
    def _configureErrorFields(self, error_fields):
        """ Get list of fields with validation error if any
        """
        self.__errorFields = error_fields
        return None    
    
    def _serve_content(self, reqhandler):
        """ Composes and renders the content of a work order 
        """
        self.__retrieveActiveWorkorder()
        self.__output_workorder_header(reqhandler)
        self.__output_workorder_form(reqhandler)
        return None    

    def __output_workorder_header(self, reqhandler):
        """ Composes and renders the header section of the work order form 
        """
        tempValuesDict = { 'customer':self.__customer, 'vehicle':self.__vehicle }    
        doRender (reqhandler, 'workorderSubviewHeader', tempValuesDict)      
        return None
    
    def __format_tabs(self, reqhandler):
        """ Composes and renders the tab section of the work order form 
        """
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
        """ Composes and renders the form section of the work order form 
            with validation error(s) handling 
        """
        self.__format_tabs(reqhandler)
        tempValuesDict = { 'date_created':self.__workorder.getDateCreated(),
                          'date_closed':self.__workorder.getDateClosed() }  
        if ( self.__workorder.mechanic != "" and self.__workorder.mechanic is not None and \
                    self.__workorder.mechanic not in self.__mechanics ):
            self.__mechanics.append(self.__workorder.mechanic) 
        mechanics =[{'value':mechanic,'name':mechanic} for mechanic in self.__mechanics]
        mechanics.insert(0, { 'value':Workorder.NO_MECHANIC,'name':'Select...' })
        if self.__errorFields is not None:
            for field in self.__errorFields:
                tempValuesDict["e_" + field] = True               
        tempValuesDict ['mechanics'] = mechanics
        tempValuesDict ['workorder'] = self.__workorder
        doRender( reqhandler,'workorderSubviewForm', tempValuesDict )
        return None

class DialogSubview(object):
    """ Composes and renders a save dialog using dialogTemplate.html
    """
    def __init__(self, request_button, request_tag):
        """ Constructor for DialogSubview().Initialize dialog UI with 
            request_button and request_tag.
        """
        self.__request_button = request_button
        self.__request_tag = request_tag
        return None
    
    def _serve_content(self, reqhandler):
        """ Composes and renders the dialog.
        """
        tempValuesDict = { 'request_button':self.__request_button,
                          'request_tag':self.__request_tag }
        doRender( reqhandler,"dialogTemplate",tempValuesDict )
        return None
    
    
