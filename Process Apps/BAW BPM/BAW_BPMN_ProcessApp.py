import pandas as pd
import os
import requests, urllib3
requests.packages.urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from requests.auth import HTTPBasicAuth
from jsonpath_ng import jsonpath, parse
import json



baw_fields = {
    "process_mining_mapping": {
        "process_ID": "piid",
        "task_name": "name",
        "start_date": "startTime",
        "end_date": "completionTime",
        "owner": "owner",
        "team": "teamDisplayName"
    },
    "included_task_data": [
        "activationTime",
        "atRiskTime",
        "completionTime",
        "description",
        "isAtRisk",
        "originator",
        "priority",
        "startTime",
        "state",
        "piid",
        "priorityName",
        "teamDisplayName",
        "managerTeamDisplayName",
        "tkiid",
        "name",
        "status",
        "owner",
        "assignedToDisplayName",
        "assignedToType",
        "dueTime",
        "closeByUser"
    ],
    "excluded_task_data": [
        "description",
        "clientTypes",
        "containmentContextID",
        "kind",
        "externalActivitySnapshotID",
        "serviceID",
        "serviceSnapshotID",
        "serviceType",
        "flowObjectID",
        "nextTaskId",
        "actions",
        "teamName",
        "teamID",
        "managerTeamName",
        "managerTeamID",
        "displayName",
        "processInstanceName",
        "assignedTo",
        "assignedToID",
        "collaboration",
        "activationTime",
        "lastModificationTime",
        "assignedToDisplayName",
        "closeByUserFullName"
    ]
}


PROCESS_SEARCH_URL = "rest/bpm/wle/v1/processes/search?"
PROCESS_SEARCH_BPD_FILTER = "searchFilter="
PROCESS_SEARCH_PROJECT_FILTER = "&projectFilter="
TASK_SUMMARY_URL = "rest/bpm/wle/v1/process/"
TASK_SUMMARY_URL_SUFFIX = "/taskSummary/"
TASK_DETAIL_URL = "rest/bpm/wle/v1/task/"
TASK_DETAIL_URL_SUFFIX = "?parts=data"


def build_instance_search_url(config):
    url = config['root_url'] + PROCESS_SEARCH_URL

    # from_date and from_date_criteria
    from_date_str = config['from_date_criteria']+"="+config['from_date']

    # to_date and to_date_criteria
    to_date_str = config['to_date_criteria']+"="+config['to_date']

    url = url + from_date_str + "&" + to_date_str

    # Add the process name and project to the URL
    url = url + "&" + config['process_name'] + PROCESS_SEARCH_PROJECT_FILTER + config['project']

  
    if config['instance_limit'] > 0 :
        url = url + f"&limit={str(config['instance_limit'])}"

    return url

def get_instance_list(instance_list, config):
    try:
        url = build_instance_search_url(config)
        message = f"Search URL : {url}"
        print(message)
        response = requests.get(url, auth=config['auth_data'], verify=False)
        status = response.status_code

        if status == 200:
            instance_data_json = response.json()
            for bpd_instance in instance_data_json['data']['processes']:
                instance_list.append({'piid' : bpd_instance['piid']})
        else :
            error = json.loads(response.text)
            message = f"BAW REST API response code: {response.status_code}, reason: {response.reason}, {error['Data']['errorMessage']}"
            raise ProcessAppException(message)
            print(message)
    except Exception as e:
        message = f"Unexpected error processing BPD : {config['process_name']} " + str(e)
        print(message)

    

# Function to fetch task details info for a specific instance
def create_event(task_id, event_data, config):
    try:
        url = config['root_url'] + TASK_DETAIL_URL + task_id + TASK_DETAIL_URL_SUFFIX
        task_detail_response = requests.get(url, auth=config['auth_data'], verify=False)
        if task_detail_response.status_code == 200:
            task_detail_data = task_detail_response.json()
            task_data = task_detail_data['data']
            task_data_keys = task_data.keys()

            # Create the process mining event
            event = {}
             # find and rename the keys that are mapped into process mining keys
            ipm_mapping = config['BAW_fields']['process_mining_mapping']
            ipm_fields = ipm_mapping.keys()
            for field in ipm_fields:
                if (ipm_mapping[field] in task_data_keys):
                    event[field] = task_data.pop(ipm_mapping[field])
                else:
                    print("Error: task data: %s mapped to: %s not found" % (ipm_mapping[field], field))

            # include the keys that in config['BAW_fields']['included_task_data']
            keepkeys = config['BAW_fields']['included_task_data']
            for key in keepkeys:
                if (key in task_data_keys):
                    event[key] = task_data.pop(key)

            # Append the data.variables that are listed
            data_variables = config['task_data_variables']

            # Search from 'data.variables' keep 'data.' before each variable name
            #
            for searched_var in data_variables:
                # Default value to use if no match is found in the task data
                variable_value = ""
                jsonpath_expression = parse("variables"+"."+searched_var)
                for match in jsonpath_expression.find(task_data['data']):
                    # Update the default variable
                    variable_value = match.value
                    break
                # Add the value to the event dictionary (could be "")
                event["tsk."+searched_var] = variable_value

            # append event to the event_data array
            event_data.append(event)
    except Exception as e:
        message = f"Unexpected error while creating event for task : {task_id} "+str(e)
        print(message)
        raise ProcessAppException(message)



# Function to fetch task summary info for a specific instance
def get_tasks(instance_list, config):
    
    for instance in instance_list:
        try:
            url = config['root_url'] + TASK_SUMMARY_URL + instance['piid'] + TASK_SUMMARY_URL_SUFFIX

            response = requests.get(url, auth=config['auth_data'], verify=False)
            if response.status_code == 200:
                task_summary_data = response.json()
                task_list = []
                for task_summary in task_summary_data['data']['tasks']:
                    task_id = task_summary['tkiid']
                    task_list.append(task_id)
            instance['task_list'] = task_list
            print("%s task(s) retrieved for BPD instance %s" % (len(instance['task_list']),instance['piid']))

        except Exception as e:
            message = "--- There was an error in the execution: "+str(e)
            print(message)
            raise ProcessAppException(message)



# This is the entry function for the logic file.

default_config = {
        "root_url": "<BAW_URL>",
        "user": "admin",
        "password": "admin",
        "project": "HSS",
        "process_name": "Standard HR Open New Position",
        "from_date": "2022-10-08",
        "from_date_criteria": "createdAfter",
        "to_date": "2022-12-08",
        "to_date_criteria": "modifiedBefore",
        "instance_limit": '10',
        #"task_data_variables": "requisition.gmApproval,requisition.requester",
    }

import datetime

# When loaded into Process Mining, the import works.
# To run/debug this program as a standalone code, we redefine the ProcessAppException class below
try:
    from process_app import ProcessAppException
except: 
    class ProcessAppException(Exception):
        def __init__(self, message):
            self.message=message
            super().__init__(self.message)
        def getMessage(self):
            return self.message


def execute(context):

    # Complement the config fields
    config = context['config']

    # check the URL


    # check that the input dates have the expected date format
    date_format = '%Y-%m-%d'
    baw_date_format = '%Y-%m-%dT%H:%M:%SZ'
    try:
    # formatting the date using strptime() function
        dateObject = datetime.datetime.strptime(config['from_date'], date_format)
        config['from_date'] = dateObject.strftime(baw_date_format)
        dateObject = datetime.datetime.strptime(config['to_date'], date_format)
        config['to_date'] = dateObject.strftime(baw_date_format)

    # If the date validation goes wrong
    except Exception as e:   # printing the appropriate text if ValueError occurs
        raise ProcessAppException("Incorrect date format, should be like this 2022-10-08" + str(e))

    
    # check the optional fields. They key does not exist if the fields are ommitted
    if 'task_data_variables' in config:
    # task_data_variables is entered as a string like this: "requisition.gmApproval,requisition.requester"
    # remove any blank character
    # we have to split it and put each string in an array
        config['task_data_variables'] = config['task_data_variables'].replace(' ','')
        config['task_data_variables'] = config['task_data_variables'].split(',')
    else:
        config['task_data_variables'] = []

    if 'instance_limit' in config:
        if config['instance_limit'].isnumeric():
            config['instance_limit'] = int(config['instance_limit'])
        else:
            config['instance_limit'] = 0
        
    config['BAW_fields'] = baw_fields
        
    event_list = []
    instance_list = []
    config['auth_data'] = HTTPBasicAuth(config['user'], config['password'])

    # Create the instance list
    get_instance_list(instance_list, config)
    print("%s BPD instances retrieved." % len(instance_list))
    get_tasks(instance_list, config)
    event_number = 0
    for instance in instance_list:
        event_number += len(instance['task_list'])
    print("%s events to create" % event_number)
    for instance in instance_list:
        for task in instance['task_list']:
            print("Creating event for task %s" % task)
            create_event(task, event_list, config)
    
    print("Done")

    # Create the dataframe to return to Process Mining
    return pd.DataFrame(event_list)


if __name__ == "__main__":
    context = {'config': default_config}
    df = execute(context) 
    print (df)