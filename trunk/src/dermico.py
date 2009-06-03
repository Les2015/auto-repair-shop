""" dermico.py  Author:  Brad Gaiser  CIS 68K Final Project  Team 2

    This module provides the main routine and the implementation of the
    Contoller class in the MVC implementation of the Auto Shop Maintenance
    Records System.
"""

import sys

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from MaintAppView import MaintAppView
from MaintAppModel import MaintAppModel
from MaintAppObjects import Customer, Vehicle, Workorder


class DefaultConfiguration(webapp.RequestHandler):
    def get(self):
        """ Callback for handling the initial startup configuration of the
            Maintenance Records System.
        """
        MaintAppController.theController().handle_button_events(self, "newcust", "STARTUP")
        return None

    
    
class SearchLinkHandler(webapp.RequestHandler):
    def get(self):
        """ Callback for 'get' events from user clicking on hyperlinks generated
            from the results of a customer search.  The results are fed back to the
            server as get request:  http://...../Search?cid=#### where #### is the
            database primary key for the customer information being displayed.
        """
        customer_id = self.request.get('cid')
        MaintAppController.theController().handle_button_events(self, "showcust", customer_id)
        return None
    
    
class CustomerInput(webapp.RequestHandler):
    def post(self):
        button_pressed = self.__getbutton()
        button_fields = button_pressed.split("_")
        button = button_fields[0]
        tag = (None if len(button_fields) < 2 else button_fields[1])
        MaintAppController.theController().handle_button_events(self, button, tag)
        return None
    
    def __getbutton(self):
        """ Get the dispatch name for a button.  This routine assumes that all
            buttons are named using the convention:  submit_command_index
            "submit_" is simply removed.  "command" is the string that will be
            used to look up the callback function.  "index" is additional info
            needed to select some items (e.g. vehicle tabs, multiple search
            results and open/completed work order list entries.)
        """
        arguments = self.request.arguments()
        button_info = None
        for arg in arguments:
            if str(arg).startswith("submit_"):
                button_info = str(arg)
                break
        if button_info is not None:
            button_info = button_info[len("submit_"):]
        else:
            button_info = "null"
        return button_info
    
            
class SaveDialogHandler(webapp.RequestHandler):
    def put(self):
        """ Callback for 'put' events from form buttons on Save Data dialog.
        """
        response = self.request.get('submit')
        whichButton = self.request.get('request_button')
        tag = self.request.get('request_tag')
        MaintAppController.theController().handle_dialog_event(self, response, 
                                                               whichButton, tag)
        return None
    
    
class MaintAppController(object):
    __theController = None
    
    def __init__(self):
        MaintAppController.__theController = self
        self.__view = MaintAppView(self)
        self.__app = webapp.WSGIApplication(
                                            [('/',         DefaultConfiguration),
                                             ('/Customer', CustomerInput),
                                             ('/Search',   SearchLinkHandler),
                                             ('/Dialog',   SaveDialogHandler)],
                                             debug=True)

        self.__dispatch_table = {"newcust"   : MaintAppController.addNewCustomer,
                                 "findcust"  : MaintAppController.setupCustomerSearch,
                                 "savecust"  : MaintAppController.saveCustomerInfo,
                                 "showcust"  : MaintAppController.showCustomer,
                                 "resetcust" : MaintAppController.clearCustomerInfo,
                                 "rstrcust"  : MaintAppController.restoreCustomerInfo,
                                 "search"    : MaintAppController.doSearch,
                                 "savevhcl"  : MaintAppController.saveVehicleInfo,
                                 "rstrvhcl"  : MaintAppController.restoreVehicleInfo,
                                 "vtab"      : MaintAppController.vehicleTabClicked,
                                 "newwo"     : MaintAppController.newWorkOrder,
                                 "showwos"   : MaintAppController.showWorkOrderHistory,
                                 "savewo"    : MaintAppController.saveWorkOrder,
                                 "wotab"     : MaintAppController.workOrderTabClicked,
                                 "activewo"  : MaintAppController.displayActiveWorkOrder,
                                 "rstrwo"    : MaintAppController.restoreWorkOrder}
        
        self.__contextChangingActions = \
            ["newcust", "findcust", "vtab", "showwos", "wotab", "activewo"]
        self.__model = MaintAppModel()
        self.__model.initialize()
        self.__userValues = None
        self.__clearHiddenIdFields()
        
        return None
    
    @staticmethod
    def theController():
        return MaintAppController.__theController

    def view(self):
        return self.__view
    
    def handle_button_events(self, reqhandler, whichButton, bIndex):
        """ Retrieve form fields from request handler, then call the
            handler for the particular button or link that resulted 
            in the current html request.
        """
        
        self.__getValues(reqhandler)
        if bIndex != "STARTUP":
            self.__getHiddenIdFields()
        
        # If button would result in context change where edits might be lost, 
        # display dialog prompting for save or not.
        if whichButton in self.__contextChangingActions and self.__fieldsNeedSaving():
            self.__view.showSaveDialog(whichButton)
            self.__regenerateCurrentView()
        else:    
            dispatch_function = self.__dispatch_table[whichButton]
            if dispatch_function is not None:
                dispatch_function(self, reqhandler, bIndex)
            else:
                sys.stderr.write("Button '%s' not found in dispatch list." % whichButton)
                self.__regenerateCurrentView()
                
            self.__configureHiddenIdFields()
            self.__view.serve_content(reqhandler)
        return None
    
    def handle_dialog_event(self, reqhandler, response, whichButton, tag):
        """ User requested context change that required a confirmation dialog for
            saving or not before leaving the current context.  Based on the response,
            perform the save operation, ignore it, or cancel the operation and
            stay in current context.  If save is successful, change to the context
            specified by the requested_change string.
        """
        if response == "Yes":
            # Do the save.  The only tricky issue here is what to do if the
            # save operation cannot be performed because of bad data...
            self.__saveOk = True
            if self.__customerFieldsChanged():
                # QQQQ Do customer save operation
                pass
            if self.__saveOk and self.__vehicleFieldsChanged():
                # QQQQ Do vehicle save operation
                pass
            if self.__saveOk and self.__workorderFieldsChanged():
                # QQQQ Do workorder save operation
                pass
            if self.__saveOk:
                self.handle_button_events(reqhandler, whichButton, tag)
            else:
                self.__regenerateCurrentView()
        elif response == "No":
            # Continue on to originally required context.  Edits will be lost.
            self.handle_button_events(reqhandler, whichButton, tag)
        else: # response == "Cancel"
            self.__regenerateCurrentView()
        
    # Misc. helper functions.
    
    def __getValues(self, reqhandler):
        """ Generates a dictionary of the values that were passed to the server
            as a consequence of the post request.  Don't include any button 'events'.
        """
        values = {}
        arguments = reqhandler.request.arguments()
        for arg in arguments:
            if not str(arg).startswith("submit_"):
                values[arg] = reqhandler.request.get(arg).strip()
        self.__userValues = values
        return None
        
    def __fieldsNeedSaving(self):
        """ Compare the form fields on the screen with the version saved in the
            database (or against an empty record if creating a new item).  Return
            True if any field has changed.  False otherwise.
        """
        # return self.__customerFieldsChanged() or \
        #        self.__vehicleFieldsChanged() or \
        #        self.__workorderFieldsChanged()
        return False # Stub this out so we don't go through the save dialog path for now.
    
    def __customerFieldsChanged(self):
        """ Compares the form fields for the customer section against the 
            corresponding database information or against an empty Customer
            record if entering a new customer to see if any edits have been
            made.  Return True if edits have been made, False otherwise.
            Also, returns False if the customer form fields are not active.
        """
        if self.__customerActive():
            if self.__activeCustomerId == "-1":
                compCust = Customer()
            else:
                compCust = self.__model.getCustomer(self.__activeCustomerId)
            activeCust = Customer()
            activeCust.loadFromDictionary(self.__userValues)
            retVal = (compCust == activeCust)
        else:
            retVal = False
            
        return retVal
    
    def __vehicleFieldsChanged(self):
        """ Compares the form fields for the customer section against the 
            corresponding database information or against an empty Vehicle
            record if entering a new vehicle to see if any edits have been
            made.  Return True if edits have been made, False otherwise.
            Also, returns False if the customer or vehicle form fields are
            not active.
        """
        if self.__vehicleActive():
            if self.__activeVehicleId == "-1":
                compVehicle = Vehicle()
            else:
                compVehicle = self.__model.getCustomer(self.__activeVehicleId)
            activeVehicle = Vehicle()
            activeVehicle.loadFromDictionary(self.__userValues)
            retVal = (compVehicle == activeVehicle)
        else:
            retVal = False
            
        return retVal
    
    def __workorderFieldsChanged(self):
        """ Compares the form fields for the work order section against the 
            corresponding database information or against an empty Workorder
            record if entering a new customer to see if any edits have been
            made.  Return True if edits have been made, False otherwise.
            Also, returns False if the work order view is not active.
        """
        if self.__workorderActive():
            if self.__activeWorkorderId == "-1":
                compWorkorder = Workorder()
            else:
                compWorkorder = self.__model.getCustomer(self.__activeWorkorderId)
            activeWorkorder = Workorder()
            activeWorkorder.loadFromDictionary(self.__userValues)
            retVal = (compWorkorder == activeWorkorder)
        else:
            retVal = False
            
        return retVal
    
    def __customerActive(self):
        """ See if the 'first_name' form field for the customer was submitted.  If
            it is, the form is active (return True, False otherwise).
        """
        return ('first_name' in self.__userValues.keys())
    
    def __vehicleActive(self):
        """ See if the 'model' form field for the vehicle was submitted.  If
            it is, the form is active (return True, False otherwise).
        """
        return ('model' in self.__userValues.keys())
    
    def __workorderActive(self):
        """ Determine whether or not the work order is active.  Since the work order
            is never on the screen when the customer fields are active, we negate
            the customerActive test.
        """
        return not self.__customerActive()
    
    def __getHiddenIdFields(self):
        """ Extract the three active ids (customer_id, vehicle_id, and workorder_id) from
            the dictionary of values returned from the hidden fields in the form.
        """
        self.__activeCustomerId  = self.__userValues['customer_id']
        self.__activeVehicleId   = self.__userValues['vehicle_id']
        self.__activeWorkorderId = self.__userValues['workorder_id']
        return None
    
    def __configureHiddenIdFields(self):
        """ Send ids off to the View to populate the hidden field values. """
        self.__view.configureHiddenFields(self.__activeCustomerId,
                                          self.__activeVehicleId,
                                          self.__activeWorkorderId)
        return None
    
    def __clearHiddenIdFields(self):
        """ Utility function to set all hidden fields to -1 to indicate no customer
            vehicle or workorder is currently active.
        """
        self.__activeCustomerId = "-1"
        self.__activeVehicleId = "-1"
        self.__activeWorkorderId = "-1"
        return None

    def __findActiveVehicle(self, vehicleList):
        """ Search the list of vehicles for the entry whose primary key matches
            the __activeVehicleId.
        """
        retVehicle = None
        for vehicle in vehicleList:
            sys.stderr.write("%s -- %s\n" % (vehicle.getId(), self.__activeVehicleId))
            if vehicle.getId() == self.__activeVehicleId:
                retVehicle = vehicle
                break
        return retVehicle
    
    def __findActiveWorkorder(self, workorderList):
        """ Search the list of work orders for the entry whose primary key matches
            the __activeWorkorderId.
        """
        retWorkorder = None
        for workorder in workorderList:
            if workorder.getId() == self.__activeWorkorderId:
                retWorkorder = workorder
                break
        return retWorkorder
    
    def __configureSidePanel(self, activeElement, debug_message):
        """ Retrieve the open work order list and completed work order list
            from database.  Configure the side panel with these lists and
            inform the side panel which is the active element:
                0 = No item highlighted,
                1 = New Customer Button, 
                2 = Find Customer Button,
                3 = Item in one of work order lists corresponding to
                     activeWorkorderId)
        """
        openWorkorders = self.__model.getOpenWorkorders()
        completedWorkorders = self.__model.getCompletedWorkorders()
        
        self.__view.configureSidePanelContent(activeElement,
                                              openWorkorders,
                                              completedWorkorders,
                                              debug_message)
        return None
    
    def __configureVehicleInfo(self):
        """ Reconstitute the vehicle information for display in the vehicle tab.
        
            The following is a bit state dependent.  If this request was a result of
            the creation (save) of a new customer, we need to build a list with an empty
            vehicle object for the "new vehicle" tab.  Otherwise we need to retrieve
            the vehicle list from the Model, fill in the fields for the active vehicle
            from the form fields (the user may have made changes) and send to View.
        """
        
        if self.__activeCustomerId == "-1":
            activeVehicle = Vehicle()
            activeVehicleList = [activeVehicle]
            self.__activeVehicleId = "-1"
        else:
            activeVehicleList = self.__model.getVehicleList(self.__activeCustomerId)
            # There is always an unsaved vehicle record at the end of the list for
            # entering new vehicle information.
            newVehicleSlot = Vehicle()
            activeVehicleList.append(newVehicleSlot)
            # The user might have done a customer save in the middle of generating
            # information for a new vehicle...
            if self.__activeVehicleId == "-1":
                # Since the customer id was not "-1" and the active vehicle id was
                # "-1", the user was entering information for a new vehicle.
                activeVehicle = newVehicleSlot
            else:
                activeVehicle = self.__findActiveVehicle(activeVehicleList)
        # Load any information that might have already been entered into the
        # form fields into the active vehicle.
        if self.__vehicleActive():
            activeVehicle.loadFromDictionary(self.__userValues)
        self.__view.configureVehicleContent(activeVehicleList)
        return None
    
    def __configureWorkorderCustomerVehicleInfo(self):
        """ The work order form has some basic information for the active customer
            and the active vehicle to which the work order belongs.  This method
            requests those records from the Model and sends them to the View to
            configure this part of the form.
        """
        customer = self.__model.getCustomer(self.__activeCustomerId)
        vehicle = self.__model.getVehicle(self.__activeVehicleId)
        self.__view.configureWorkorderHeader(customer, vehicle)
        return None
    
    
    ##############################################################################
    # Button event handlers follow.
    
    def addNewCustomer(self, reqhandler, tag):
        """ Set up the user interface to enter a new customer.  Start by
            clearing the Customer input part of form.  Request view to
            display just the customer input form.
            
            Configure customer panel with empty Customer object.
            Tell view to go into New Customer configuration.
            Ask view to re-render display.
        """
        self.__clearHiddenIdFields()
        self.__view.configureCustomerContent(Customer())
        self.__configureSidePanel(1, "Add New Customer") # For debugging
        self.__view.set_new_customer_mode()
        return None
        
    def saveCustomerInfo(self, reqhandler, tag):
        """ Save the customer information entered by the user to the data store.
        
            Retrieve Customer object filled in with form data.
            Ask Model to save Customer object, Model returns customer id.  This
              might be a new one if the Customer record is for a new one.
            If this is a new customer:
              Create an empty Vehicle Record as only item in a list.
              Configure vehicle panel with this list.
              Tell view to go into Enter Customer/Vehicle mode
            Ask view to re-render display
        """
        activeCustomer = Customer()
        activeCustomer.loadFromDictionary(self.__userValues)
        errorList = self.__model.validateCustomerInfo(activeCustomer)
        if len(errorList) == 0:
            customerDbId = self.__model.saveCustomerInfo(activeCustomer)
            activeCustomer.setId(customerDbId)
            self.__view.configureCustomerContent(activeCustomer)
            
            self.__configureVehicleInfo()
            
            self.__activeCustomerId = customerDbId
            self.__configureSidePanel(0, "Save Customer Info")
            self.__view.set_customer_vehicle_mode()
        else:
            self.__view.configureErrorMessages(errorList)
            self.__regenerateCurrentView()
        return None
    
    def setupCustomerSearch(self, reqhandler, tag):
        """ Setup a customer search as a result of click on Find Customer button in
            side panel:
            
            Highlight side panel search button.
            Configure customer panel with empty Customer object.
            Clear active element fields.
            Tell view to go into Search configuration.
            Ask view to re-render display.
        """
        self.__view.configureCustomerContent(Customer())
        self.__clearHiddenIdFields()
        self.__configureSidePanel(2, "Find Customer Info")
        self.__view.set_search_mode()
        return None
    
    def doSearch(self, reqhandler, tag):
        """ Call back for search request.  Request list of Customer records from
            Model matching the search criteria.  Display result.

            Retrieve Customer object filled in with form field values
            Ask Model to perform search based on supplied information.
            Model returns a list of matching Customer records
            Tell view to go into Search/Results configuration with current Customer
              record and list of matching Customer records.  View will leave form
              field filled in and will format a set of hyperlinks to be displayed
              below the search boxes per item 3 in mockup.  The hyperlink target
              will be /Search?cid=### where ### corresponds to the customer id
              for the Customer represented by the hyperlink.
        """
        searchCriteria = Customer()
        searchCriteria.loadFromDictionary(self.__userValues)
        
        searchResults = self.__model.searchForMatchingCustomers(searchCriteria)
        self.__view.configureSearchResults(searchResults)
        self.__configureSidePanel(2, "Search Results")
        self.__view.set_search_results_mode()
        return None
    
    def saveVehicleInfo(self, reqhandler, tag):
        """ Save the Vehicle information to the data store.  Redisplay the current
            set of vehicles with an empty slot for the New Vehicle tab.
        
            Load vehicle data from form fields, then have the model save the
                vehicle.
            Retrieve the full vehicle list from Model.  Append empty vehicle for
                New Vehicle tab.
            Retrieve the customer fields from the form field info since the user
                can save the vehicle with unsaved changes in the customer fields.
            Configure the various pieces of the UI and tell it to rerender.
        """
        vehicle = Vehicle()
        vehicle.loadFromDictionary(self.__userValues)
        vehicle.setCustomerId(self.__activeCustomerId)
        vehicleList = self.__model.getVehicleList(self.__activeCustomerId)
        errorList = self.__model.validateVehicleInfo(vehicle)
        if len(errorList) == 0:
            self.__activeVehicleId = self.__model.saveVehicleInfo(vehicle)
            vehicleList.append(Vehicle())
        else:
            self.__view.configureErrorMessages(errorList)
            if self.__activeVehicleId == "-1":
                # User was entering info for a new vehicle.  Just append the
                # vehicle loaded from the UI to the end of the list as the
                # new vehicle place holder.
                vehicleList.append(vehicle)
            else:
                # Replace entry in list with the active one whose values were
                #   loaded from the form fields.
                vehicleIndex = self.__findActiveVehicle(vehicleList)
                vehicleList.pop(vehicleIndex)
                vehicleList.insert(vehicleIndex, vehicle)
            
        customer = Customer()
        customer.loadFromDictionary(self.__userValues)
        self.__view.configureCustomerContent(customer)
    
        self.__view.configureVehicleContent(vehicleList)
        self.__configureSidePanel(0, "Save Vehicle Info")
        self.__view.set_customer_vehicle_mode()
        return None

    def vehicleTabClicked(self, reqhandler, tag):
        """ The user clicked on one of the vehicle tabs.  Activate the selected tab
            and display the contents of the vehicle corresponding to that tab.  
            Here, 'tag' parameter is the zero based index into the list of vehicles
            represented by the tabs.
            
            IMPORTANT:  The primary assumption here is that the user is prompted to
            save information that has been edited on the current tab before this
            method is called.
            
            Retrieve list of vehicles from Model.
            Add empty vehicle to end for 'New Vehicle' tab
            Use the tag to retrieve the id for the vehicle to be made active.
            Retrieve the customer information from the form fields since the
                user may have edited some of the customer fields.
            Configure the customer and vehicle information in the View.
            Ask the View to rerender.
        """
        vehicleList = self.__model.getVehicleList(self.__activeCustomerId)
        vehicleList.append(Vehicle())
        self.__activeVehicleId = vehicleList[int(tag)].getId()
        
        customer = Customer()
        customer.loadFromDictionary(self.__userValues)
        self.__view.configureCustomerContent(Customer())

        self.__view.configureVehicleContent(vehicleList)
        self.__configureSidePanel(0, "Vehicle Tab Change")
        self.__view.set_customer_vehicle_mode()
        return None
    
    def newWorkOrder(self, reqhandler, tag):
        """ User clicked on 'New Work Order' button.  Setup user interface to
            display an empty work order form.

            Retrieve Work Order list for active Vehicle Id from Model
            Create empty Work Order object and add to front of work order list
            Tell view to go into Create Work Order mode passing in list of work orders
               and active work order index of 0 to display first tab
        """
        self.__configureWorkorderCustomerVehicleInfo()
        workorders = self.__model.getWorkorderList(self.__activeVehicleId)
        self.__activeWorkorderId == "-1"  # Creating a new work order.
        workorders.insert(0, Workorder())
        self.__view.configureWorkorderContent(workorders)
        self.__configureSidePanel(0, "New Workorder")
        self.__view.set_workorder_mode()
        return None
    
    def showWorkOrderHistory(self, reqhandler, tag):
        """ Display minimal customer and vehicle information then show a tabbed
            list of all past (and currently active) work orders for that customer/
            vehicle.

            Retrieve list of Work Orders from Model using Vehicle Id for active Vehicle
            Tell view to go into Show Work Order mode passing in list of work orders and
              active work order index of 0 to display first tab
        """
        workorders = self.__model.getWorkorderList(self.__activeVehicleId)
        self.__activeWorkorderId = workorders[0].getId()
        self.__configureWorkorderCustomerVehicleInfo()
        self.__view.configureWorkorderContent(workorders)
        self.__configureSidePanel(3, "Show Workorder History")
        self.__view.set_workorder_mode()
        return None
    
    def saveWorkOrder(self, reqhandler, tag):
        """ Callback for both "Create Work Order" and "Save Work Order".
            Either create a new Work Order record in the database from the submitted
            form data of save changes to an existing one.  Since the differences
            between the initial creation of a work order and the updating of one
            are minor from the perspective of the controller, I thought we could 
            do this with one callback instead of 2.
            
            Retrieve Work Order object filled in with form data
            Load system date/time into creation time field for new work order.
            Load system date/time into completion time field for closed work order if
                the completion date is none.  If date already set, this corresponds
                to a clean up edit after job completed.
            Add vehicle id for new work order.
            Ask Model to save Work Order object.  Model returns Work Order Id.
            Retrieve list of Work Orders from Model using active Vehicle Id
            Since open/closed/completed state may change and committed on a Save
              operation and of course a new one is added on the Create operation,
              ask Model for list of open work orders and for the list of completed
              work orders
            Configure side panel with the lists of open and completed work orders
            Tell view to go into Show Work Order mode passing in list of work orders
              and the active work order index so that correct tab will be made active
        """
        workorder = Workorder()
        workorder.loadFromDictionary(self.__activeWorkorderId)
        errorList = self.__model.validateWorkorderInfo(workorder) + \
                    workorder.checkRequiredFieldsForCurrentState()
        if len(errorList) == 0:
            if self.__activeWorkorderId == "-1": # New workorder to be saved.
                workorder.setDateCreated()
                workorder.setVehicleId(self.__activeVehicleId)
            elif workorder.getState() == Workorder.CLOSED and \
                    workorder.getDateClosed() is not None:
                workorder.setDateClosed()
            self.__activeWorkorderId = self.__model.saveWorkorder(workorder)
            
            workorders = self.__model.getWorkorderList(self.__activeVehicleId)
        else:
            self.__view.configureErrorMessages(errorList)
            workorders = self.__model.getWorkorderList(self.__activeVehicleId)
            if self.__activeWorkorderId == "-1":
                # User is entering a new workorder.
                workorders.insert(0, workorder)
            else:
                # Replace entry in list with the active one whose values were
                #   loaded from the form fields.
                workorderIndex = self.__findActiveWorkorder(workorders)
                workorders.pop(workorderIndex)
                workorders.insert(workorderIndex, workorder)
                
        self.__configureWorkorderCustomerVehicleInfo()
        self.__view.configureWorkorderContent(workorders)
        self.__configureSidePanel(3, "Save Workorder")
        self.__view.set_workorder_mode()
        return None
    
    def workOrderTabClicked(self, reqhandler, tag):
        """ The user clicked on one of the work order tabs.  If the tab is not the
            currently active tab, activate the selected tab and display the contents
            of the work order corresponding to that tab.  Here, tag is the zero based
            index into the list of work orders represented by the tabs.
            
            Tell view to go into Show Work Order mode passing in list of work orders
              and the selected work order index associated with the tab selected
              It is unknown at this point whether the Work Order list is cached or
              not and whether it is cached by the view or by the controller.
        """
        workorders = self.__model.getWorkorderList(self.__activeVehicleId)
        self.__activeWorkorderId = workorders[0].getId()
        self.__configureWorkorderCustomerVehicleInfo()
        self.__view.configureWorkorderContent(workorders)
        self.__configureSidePanel(3, "Workorder Tab Change")
        self.__view.set_workorder_mode()
        return None
    
    
    def displayActiveWorkOrder(self, reqhandler, tag):
        """ Display either an open work order or a completed work order in response
            to the user clicking on one of these items in the left hand pane.  For
            this callback the tag is the primary key of the work order.  The button
            encoding is "submit_activewo_123455".
            
            Request Work Order record from Model based on Work Order ID associated
              with the open work order button that was pressed.
            Request Vehicle record from Model using Vehicle Id foreign key in Work
              Order that was returned.
            Request Customer record from Model using Customer Id foreign key in 
              Vehicle record that was returned.
            Configure customer & vehicle information in Work Order panel
            Request list of work orders using the Vehicle Id used in step 2
            Configure View with list of work orders.
            Set active customer/vehicle/workorder ids.
            Tell view to rerender.
        """
        self.__activeWorkorderId = int(tag)
        activeWorkorder = self.__model.getWorkorder(self.__activeWorkorderId)
        self.__activeVehicleId = activeWorkorder.getVehicleId()
        vehicle = self.__model.getVehicle(self.__activeVehicleId)
        self.__activeCustomerId = vehicle.getCustomerId()
        
        workorders = self.__model.getWorkorderList(self.__activeVehicleId)
        self.__configureWorkorderCustomerVehicleInfo()
        self.__view.configureWorkorderContent(workorders)
        self.__configureSidePanel(3, "Display Open/Completed Workorder")
        self.__view.set_workorder_mode()
        return None
    
    def showCustomer(self, reqhandler, tag):
        """ Display the customer and vehicle list where tag specifies the 
            primary key of the Customer record in the database.  This handler
            is called in response to clicking on one of the search results
            customer hyperlinks.

            This gets processed through a slightly different path than the standard
            button events.  See description of handler for "Find Customer(s)" above.
            
            Request Customer record from Model using id associated with the hyperlink
              that was clicked to get here.
            Request list of Vehicles from Model using the Customer Id
            Configure customer panel using the Customer Record
            Configure vehicle panel with vehicle list.
            Set the active vehicle id to the first vehicle in the list.
            Tell view to go into Customer/Vehicle mode.
            Tell the View to rerender.
        """
        customer = self.__model.getCustomer(self.__activeCustomerId)
        self.__view.configureCustomerContent(customer)

        vehicleList = self.__model.getVehicleList(self.__activeCustomerId)
        self.__view.configureVehicleContent(vehicleList)
        self.__activeCustomerId = vehicleList[0].getId()
        self.__configureSidePanel(0, "Showing Customer")
        self.__view.set_customer_vehicle_mode()
        return None
    
    def clearCustomerInfo(self, reqhandler, tag):
        """ Response to button to clear the customer form.  This has to be done in
            response to a submit button because the UI has been sending 'bad' fields
            back around for redisplay when errors have occurred in the data entry.
            As a consequence, a reset request would leave this info in as the 
            specified 'default' values. (Activated by button in New Customer mode
            before Save button has been hit and in Find Customer mode.)
            
            I'm going to need the tag field to be set differently for the new
            customer clear button and the find customer clear button.  This
            needs to be done so that the appropriate button in the side panel
            can be rehighlighted.
            
            Let tag = 0 be for new customer & tag = 1 for find customer.

            An empty customer Record is created and is used to configure the
              Customers panel.
            The View is then requested to refresh (the configuration didn't change
              so we simply request a refresh.
        """
        if self.__vehicleActive(): # This is a hack until the UI can reset the button
                                   # this should really be going directly to the
                                   # restore call.
            self.restoreCustomerInfo(reqhandler, tag)
        else:
            self.__clearHiddenIdFields()
            self.__view.configureCustomerContent(Customer())
            activeConfig = int(tag)
            if activeConfig == 0:
                self.__configureSidePanel(1, "Clearing Customer Info")
                self.__view.set_new_customer_mode()
            else:
                self.__configureSidePanel(2, "Clearing Customer Info")
                self.__view.set_search_mode()
        return None
    
    def restoreCustomerInfo(self, reqhandler, tag):
        """ Restores customer information to the values saved in the database.

            The Model is asked to retrieve the Customer record using the Customer
                Id of the active customer.
            The Customer panel is configured with the retrieved Customer Record
            Since the vehicle information will be displayed, we need to restore
                this info as well.
            The View is then requested to refresh.
        """
        customer = self.__model.getCustomer(self.__activeCustomerId)
        self.__view.configureCustomerContent(customer)
        self.__configureVehicleInfo()
        self.__configureSidePanel(0, "Restoring Customer Info")
        self.__view.set_customer_vehicle_mode()
        return None
    
    def restoreVehicleInfo(self, reqhandler, tag):
        """ Restores vehicle information to the values saved in the database.

            The Customer info is retrieved from the form fields and used
                to reconfigure the form.  (User may have made changes that
                have not yet been saved.)
            The Model is asked to return a list of Vehicle records using
                the Customer Id as the search criteria.
            The Vehicle panel is configured with the work order list and
                index of the active vehicle.
            The View is then requested to refresh.
        """
        customer = Customer()
        customer.loadFromDictionary(self.__userValues)
        self.__view.configureCustomerContent(customer)
        
        vehicleList = self.__model.getVehicleList(self.__activeCustomerId)
        vehicleList.append(Vehicle())
        self.__view.configureVehicleContent(vehicleList)
        
        self.__configureSidePanel(0, "Restoring Vehicle Info")
        self.__view.set_customer_vehicle_mode()
        return None

    def restoreWorkOrder(self, reqhandler, tag):
        """ Restores work order to the values saved in the database (or blank if
            it has not been saved yet.)
        
            The Model is asked to return a list of Work Order records using
              the Vehicle Id as the search criteria.  Note that we need
              to add an empty work order to the list if we are in the middle
              of creating a work order. 
            The Work Order panel is configured with the work order list and
              the index of the active work order.
            The View is then requested to refresh.
        """
        self.__configureWorkorderCustomerVehicleInfo()
        workorders = self.__model.getWorkorderList(self.__activeVehicleId)
        if self.__activeWorkorderId == "-1":  # Creating a new work order.
            workorders.insert(0, Workorder())
        self.__view.configureWorkorderContent(workorders)
        self.__configureSidePanel(3, "Restoring Workorder Info")
        self.__view.set_workorder_mode()
        return None
    
    def __regenerateCurrentView(self):
        """ Restore the form fields to the state that the user left them so that
            from the user's perspective their last action had no effect.  Used in
            the dialog handling when save can't be performed or action was cancelled.
        """
        if self.__customerActive():
            self.__regenerateCustomerView()
            if self.__activeCustomerId == "-1":
                # This situation will correspond to new vehicle mode rather than
                # search mode because error dialog only occurs for when entering
                # info that might be lost. (We don't care in search mode.
                self.__configureSidePanel(1, "Regenerated New Veh. Mode")
                self.__view.set_new_customer_mode()
            else:
                self.__regenerateVehicleView()
                self.__configureSidePanel(0, "Regenerated Cust./Veh. Mode")
                self.__view.set_customer_vehicle_mode()
        else:
            self.__regenerateWorkorderView()
            self.__configureSidePanel(3, "Regenerated Workorder Mode")
            self.__view.set_workorder_mode()
        return None
   
    def __regenerateCustomerView():
        """ Restore the customer form fields to the state that the user left them
            when attempting to move to another configuration.
        """
        customer = Customer()
        customer.loadFromDictionary(self.__userValues)
        self.__view.configureCustomerContent(customer)
        return None
    
    def __regenerateVehicleView(self):
        """ Restore the vehicle form fields to the state that the user left them
            when attempting to move to another configuration.
        """
        self.__configureVehicleInfo()
        return None
    
    def __regenerateWorkorderView(self):
        """ Restore the work order form fields to the state that the user left them
            when attempting to move to another configuration.
        """
        workorder = Workorder()
        workorder.loadFromDictionary(self.__userValues)
        
        workorders = self.__model.getWorkorderList(self.__activeVehicleId)
        if self.__activeWorkorderId == "-1":
            # User is entering a new work order.
            workorders.insert(0, workorder)
        else:
            # Replace entry in list with the active one whose values were
            #   loaded from the form fields.
            workorderIndex = self.__findActiveWorkorder(workorders)
            workorders.pop(workorderIndex)
            workorders.insert(workorderIndex, workorder)
            
        self.__configureWorkorderCustomerVehicleInfo()
        self.__view.configureWorkorderContent(workorders)
        return None

    def run(self):
        run_wsgi_app(self.__app)

        
def main():
    MaintAppController().run()
    
    
if __name__ == "__main__":
    main()