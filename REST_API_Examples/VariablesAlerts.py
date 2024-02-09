import random
import ProcessMining_API as IPM
import json
import time
import sys


def is_same_alert(variableValues, widgetAlert):
    # compare the fields that are common between the variable values and the widget data
    for key in widgetAlert.keys() & variableValues.keys():
        if variableValues[key] != widgetAlert[key]:
            return 0
    return 1

def is_alert_obsolete(variableValues, widgetAlerts):
    # Obsolete alerts are still stored in a variable, but not anymore in the widget
    for widgetAlert in widgetAlerts:
        if is_same_alert(variableValues, widgetAlert):
            # this alert from this widget exists already
            return 0
    # This alert is from this widget, but not anymore in the widget, it is obsolete
    return 1

def get_variables_from_widget(config):
    # Return the variables associated with this widget 
    
    variables = IPM.ws_get_variables(config)
    widget_variables = []
    for variable in variables:
        value = json.loads(variable['value'])
        if (variable['name'][:7] == 'Alert__') and (value['widget_id'] == config['widget_id']) :
            # This variable is an alert and is coming from this widget
            widget_variables.append(variable)
    return widget_variables

def classify_alerts_from_widget(config, widgetAlerts):
    variables = get_variables_from_widget(config)
    
    res = {"current_alerts": [], "obsolete_alerts": []}
    for variable in variables:
        variableValue = json.loads(variable['value'])
        if is_alert_obsolete(variableValue, widgetAlerts):
            res["obsolete_alerts"].append(variable)
        else:
            res['current_alerts'].append(variable)
    return res

def create_variables_from_widget(config, variableSets, widgetAlerts):
    
    # Get the current variables for this widget
    currentVariables = variableSets['current_alerts']
    newVariables = []
    for widgetAlert in widgetAlerts:
        already_exist = 0
        for v in currentVariables:
            value = json.loads(v['value'])
            if (is_same_alert(value, widgetAlert)):
                already_exist = 1
                
        if (already_exist == 0):
            widgetAlert['widget_id'] = config['widget_id']
            custom_data = config['custom_data']
            custom_keys = custom_data.keys()
            for key in custom_keys:
                widgetAlert[key]=custom_data[key]
            variablename = "Alert__%d%d" % ((int(time.time()*1000)), random.randint(0, 1000))
            newVariables.append({'name':variablename, 'value': json.dumps(widgetAlert)})

    if len(newVariables) > 0:     
        r = IPM.ws_create_update_variables(config, newVariables)
        print("create variables result: %d" % r.status_code)
      
    variableSets['new_alerts'] = newVariables
      
    return variableSets

def update_variables_from_widget(config):
    # Get the current values from the widget
    widgetAlerts = IPM.ws_get_widget_values(config)
    print("%d widget alerts" % len(widgetAlerts))    
    
    # Classify the variables (current or obsolete) 
    variablesSets = classify_alerts_from_widget(config, widgetAlerts)
    
    # Create new variables if not yet in current_alerts
    create_variables_from_widget(config, variablesSets, widgetAlerts)
        
    return variablesSets

def main(argv):

    # Example of a configuration object that could be stored as a config file passed as
    # a parameter of the program
    # custom_data are added to the alert fetched from the widget. They can be used to manage
    # some business logic with the alerts received
    configtemplate = {
        "url":"ProcessMining.com",
        "user_id": "john.smith",
        "api_key":"1345TYUI",
        "project_key": "procure-to-pay",
        "org_key": "",
        "dashboard_name": "Alerts Dashboard",
        "widget_id": "alerts-widget-1",
        "custom_data": {"Status":"False", "Custom2":"default"}
    }

    if (len(argv) == 1) :
        print("configuration file required.")
        print("Alternatively, you can ill-out the configtemplate object")
        myconfig = configtemplate
    elif (len(argv) == 2) :
        # Open the configuration file that contains myconfig json
        with open(argv[1], 'r') as file:
            myconfig = json.load(file) # keep the original
            file.close()
  
    
    print(myconfig)
    
    IPM.ws_post_sign(myconfig)
    # Read the widget, create new variables if needed, retrieve existing variables, retrieve obsolete variables
    variable_sets = update_variables_from_widget(myconfig)

    # Variables that were already created, the alerts are still in the widget (current)
    current_alerts = variable_sets['current_alerts']
    # Variables that were already created, the alerts are not anymore in the widget (obsolete)
    obsolete_alerts = variable_sets['obsolete_alerts']
    # Alerts that appear for the first time in the widget (new)
    new_alerts = variable_sets['new_alerts']

    print("%d obsolete alerts for %s" % (len(obsolete_alerts), myconfig['widget_id'])) 
    print("%d current alerts for %s" % (len(current_alerts), myconfig['widget_id'])) 
    print("%d new alerts from %s" % (len(new_alerts), myconfig['widget_id']))
    print('Alert processing rate since last update is %s' % (len(obsolete_alerts)/(len(current_alerts)+len(obsolete_alerts))))

    # Do something with obsolete variables
    # Delete the obsolete variables that came from this widget, but that are not anymore in the widget
    for v in obsolete_alerts:
        IPM.ws_delete_variable(myconfig, v['name'])
    print("%d deleted variables" % (len(obsolete_alerts)))
    

if __name__ == "__main__":
    main(sys.argv)
