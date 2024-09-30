#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import hashlib, hmac, base64
import requests, json, urllib3

requests.packages.urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import sys

SPINNING_RATE = 0.1
TIME_ADJUST = 0
PRINT_TRACE = 0

# config is passed to most function, this is a json object that includes all the required parameters

def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor

def init_params_headers(config, headers, params):
    params.update({'org' : config['org_key']})     
    headers.update({"content-type": "application/json", "Authorization": "Bearer %s" % config['sign'] })


def getTimestamp():
    return str(int(time.time() * 1000) + TIME_ADJUST) ;

def hmacSHA256(api_key, values):
    message = bytes("".join(values),encoding='utf8')
    return base64.b64encode(hmac.new( bytes(api_key, encoding='utf8'), message, digestmod=hashlib.sha256).digest()).decode("utf-8")

def ws_post_sign(config):

    url = "%s/integration/sign" % config['url']
    headers = {"content-type": "application/json"}
    data = { 'uid' : config['user_id'], 'apiKey' : config['api_key']}
    if( PRINT_TRACE) : print("REST CALL: "+url+" "+str(data))
    r = requests.post(url, verify=False, data=json.dumps(data), headers=headers)
    if (r.status_code != 200):
        print("Error: get signature: %s" % r.json()['data'])
        config['sign'] = 0
        return 0
    else:
        config['sign'] = r.json()['sign']
    return r.json()['sign']


def ws_delete_process(config):
    headers={}
    params={}
    init_params_headers(config, headers, params)

    url = "%s/integration/processes/%s" % (config['url'], config['project_key'])

    if( PRINT_TRACE) : print("REST CALL: "+ url+" "+str(params))
    r = requests.delete(url, verify=False, params=params, headers=headers)
    if (r.status_code != 200):
        print("Error: delete process: %s" % r.json()['data'])        
    return r

def ws_proc_post(config):
    headers={}
    params={}
    init_params_headers(config, headers, params)

    url = "%s/integration/processes" % (config['url'])
    data = { 'title' : config['project_name'], 'org' : config['org_key']}
    if( PRINT_TRACE) : print("REST CALL: "+ url+" "+str(data))
    r = requests.post(url, verify=False, data=json.dumps(data), headers=headers, params=params)
    if (r.status_code != 200):
        print("Error: Process %s creation: %s" % (config['project_name'], r.json()['data']))        
    return r

def ws_csv_upload(config):
    headers={}
    params={}
    init_params_headers(config, headers, params)
    # no content-type 
    headers.pop("content-type")

    url = "%s/integration/csv/%s/upload" % (config['url'], config['project_key'])
    if( PRINT_TRACE) : print("REST CALL: "+ url+" "+str(params))
    files = {'file': (config['csv_filename'], open(config['csv_filename'], 'rb'),'text/zip')}
    r = requests.post(url, verify=False, files=files, params=params, headers=headers)
    # Async call --- the caller need to loop on get job status that it is completed
    if (r.status_code != 200):
        print("Error: CSV upload: %s" % r.json()['data'])        
    return r


def ws_query_post(config, query):
    headers = {}
    params = {}
    init_params_headers(config, headers, params)
    headers['content-type'] = 'application/x-www-form-urlencoded'
    url = "%s/analytics/integration/%s/query" % (
        config['url'], config['project_key'])
    data = "params={'query': '%s'}" % query
    print(data)
    r = requests.post(url, verify=False, params=params,
                      headers=headers, data=data)
    if (r.status_code != 200):
        print("Error: query post: %s" % r.json()['data'])
    return r


def ws_backup_upload(config):
    headers={}
    params={}
    init_params_headers(config, headers, params)
    # no content-type 
    headers.pop("content-type")

    url = "%s/integration/processes/%s/upload-backup" % (config['url'], config['project_key'])

    if( PRINT_TRACE) : print("REST CALL: "+ url+" "+str(params))
    files = {'file': (config['backup_filename'], open(config['backup_filename'], 'rb'),'text/zip')}
    r = requests.post(url, verify=False, files=files, params=params, headers=headers)
    if (r.status_code != 200):
        print("Error: backup upload: %s" % r.json()['data']) 
    return r

def ws_get_backup_list(config):
    headers={}
    params={}
    init_params_headers(config, headers, params)

    url  = "%s/integration/processes/%s/backups" % (config['url'], config['project_key'])
    if( PRINT_TRACE) : print("REST CALL: "+ url+" "+str(params))
    r = requests.get(url, verify=False, headers=headers, params=params)
    if (r.status_code != 200):
        print("Error: backup list get: %s" % r.json()['data'])
    return r

def getBackupIdByMessage(backuplist, message):
    backuplist = backuplist['backups']
    for backup in backuplist:
        if (backup['message'] == message) :
            return backup['id']
    return 0

def ws_apply_backup(config):
    headers={}
    params={}
    init_params_headers(config, headers, params)

    url = "%s/integration/processes/%s/backups/%s" % (config['url'], config['project_key'], config['backup_id'])
    if( PRINT_TRACE) : print("REST CALL: "+ url+" "+str(params))
    r = requests.put(url, verify=False, headers=headers, params=params)
    if (r.status_code != 200):
        print("Error: apply backup: %s : %s" % (r.json()['data'], config['backup_id'])) 
    return r

def ws_create_log(config):
    headers={}
    params={}
    init_params_headers(config, headers, params)

    url = "%s/integration/csv/%s/create-log" % (config['url'], config['project_key'])
    if( PRINT_TRACE) : print("REST CALL: "+ url+" "+str(params))
    r = requests.post(url, verify=False, headers=headers, params=params)
    # Async function, the caller needs to check the job status (returned in r)
    if (r.status_code != 200):
        print("Error: create log: %s" % r.json()['data']) 
    return r

def ws_get_csv_job_status(config):
    headers={}
    params={}
    init_params_headers(config, headers, params)

    url = "%s/integration/csv/job-status/%s" % (config['url'], config['job_key'])
    if( PRINT_TRACE) : print("REST CALL: "+ url+" "+str(params))
    r = requests.get(url, verify=False, headers=headers, params=params)
    if (r.status_code != 200):
        print("Error: get CSV job status: %s" % r.json()['data'])        
    return r

def create_and_load_new_project(config):
    print("Process Mining: creating new project")
    r_proc = ws_proc_post(config)
    if (r_proc.status_code != 200): return r_proc
    config['project_key']= r_proc.json()['projectKey']
    print("Process Mining: loading event log (please wait)")
    r = ws_csv_upload(config)
    if (r.status_code != 200): return r
    else :
        # wait until async call is completed
        config['job_key']= r.json()['data']
        runningCall = 1
        spinner = spinning_cursor()
        while  runningCall :
            r = ws_get_csv_job_status(config)
            if (r.json()['data'] == 'complete') :
                runningCall = 0
            if (r.json()['data'] == 'error') :
                runningCall = 0
                print("Error while loading CSV -- column number mismatch")
                return 0
            sys.stdout.write(next(spinner))
            sys.stdout.flush()
            sys.stdout.write('\b')
            time.sleep(SPINNING_RATE)

    r = ws_backup_upload(config)
    if (r.status_code != 200): return r
    config['backup_id'] = r.json()['backupInfo']['id']
    r = ws_apply_backup(config)
    if (r.status_code != 200): return r
    print("Process Mining: refreshing process (please wait)")
    r = ws_create_log(config)
    if (r.status_code != 200): return r
    else :
        # wait until async call is completed
        config['job_key']= r.json()['data']
        runningCall = 1
        #pbar = tqdm(total=100)
        spinner = spinning_cursor()
        while  runningCall :
            r = ws_get_csv_job_status(config)
            if (r.json()['data'] == 'complete') :
                runningCall = 0
            if (r.json()['data'] == 'error') :
                runningCall = 0
                print("Error while creating the log")
                return 0
            sys.stdout.write(next(spinner))
            sys.stdout.flush()
            sys.stdout.write('\b')
            time.sleep(SPINNING_RATE)
    return r_proc

def upload_csv_and_createlog(config) :
    r = ws_csv_upload(config)
    if (r.status_code != 200): return r
    else :
        # wait until async call is completed
        config['job_key']= r.json()['data']
        runningCall = 1
        print("Process Mining: loading event log (please wait)")
        spinner = spinning_cursor()
        while  runningCall :
            r = ws_get_csv_job_status(config)
            if (r.json()['data'] == 'complete') :
                runningCall = 0
            if (r.json()['data'] == 'error') :
                runningCall = 0
                print("Error while loading CSV -- column number mismatch")
                return 0
            sys.stdout.write(next(spinner))
            sys.stdout.flush()
            sys.stdout.write('\b')
            time.sleep(SPINNING_RATE)

    r = ws_create_log(config)
    if (r.status_code != 200): return r
    else :
        # wait until async call is completed
        config['job_key']= r.json()['data']
        runningCall = 1
        print("Process Mining: refreshing model (please wait)")
        spinner = spinning_cursor()
        while  runningCall :
            r = ws_get_csv_job_status(config)
            if (r.json()['data'] == 'complete') :
                runningCall = 0
            if (r.json()['data'] == 'error') :
                runningCall = 0
                print("Error while creating the log")
                return 0
            sys.stdout.write(next(spinner))
            sys.stdout.flush()
            sys.stdout.write('\b')
            time.sleep(SPINNING_RATE)
    return r

# List all the dashboards of a given process mining project
def ws_get_dashboards(config):
    headers={}
    params={}
    init_params_headers(config, headers, params)

    url = "%s/analytics/integration/dashboard/%s/list" % (config['url'], config['project_key'])
    r = requests.get(url, verify=False, params=params, headers=headers)
    if (r.status_code == 200):
        values = r.json()
        return {'status_code': r.status_code, 'data' : values['data']['dashboards']}
    else:
        return {'status_code': r.status_code, 'data' : None}

# Returns only the table widgets in the dashboard_name
def ws_get_widgets(config):
    res = ws_get_dashboards(config)

    if (res['status_code'] == 200): dashboards = res['data']
    else:
        return {'status_code': res['status_code'], 'data': None}

    for aDashboard in dashboards:
        if (aDashboard['name'] == config['dashboard_name']):
            dashboard = aDashboard

    if dashboard == 0 :
        print("ERROR: dashboard does not exist")
        return 0
    dashboard_id = dashboard['id']

    headers={}
    params={}
    init_params_headers(config, headers, params)

    url = "%s/analytics/integration/dashboard/%s/%s/list" % (config['url'], config['project_key'], dashboard_id)
    r = requests.get(url, verify=False, params=params, headers=headers )
    if (res['status_code'] == 200):
        widgets = r.json() 
        return {'status_code': res['status_code'], 'data': widgets['data']['widgets']}
    else:
        return {'status_code': res['status_code'], 'data': None}

def ws_get_widget_values(config):
    dashboard_id = config.get('dashboard_id')
    if dashboard_id is None:
        # add the dashboard_id to the widget data
        print("....searching dashboard_id")
        res = ws_get_dashboards(config)
        if (res['status_code'] == 200): dashboards = res['data']
        else:
            return {'status_code': res['status_code'], 'data': None}
        dashboard = 0
        for aDashboard in dashboards:
            if (aDashboard['name'] == config['dashboard_name']):
                dashboard = aDashboard
        if (dashboard == 0) :
            print("ERROR: dashboard %s does not exist" % config['dashboard_name'])
            return {'status_code': 200, 'data': None}
        else:
            # Store the dashboard id in the widget to avoid calling again the rest API to retrieve the dashboard by name
            config['dashboard_id'] = dashboard['id']

    headers={}
    params={}
    init_params_headers(config, headers, params)

    url = "%s/analytics/integration/dashboard/%s/%s/%s/retrieve" % (config['url'],
                                                                        config['project_key'],
                                                                        config['dashboard_id'],
                                                                        config['widget_id'])

    r = requests.get(url, verify=False, params=params, headers=headers )
    if (r.status_code == 200):
        values = r.json()
        return {'status_code': r.status_code, 'data': values['data']}
    else:
        return {'status_code': r.status_code, 'data': None}

def ws_create_update_variables(config, variablesArray):
    headers={}
    params={}
    init_params_headers(config, headers, params)

    url = "%s/integration/processes/%s/variables" % (config['url'], config['project_key'])
    r = requests.post(url, verify=False, data=json.dumps(variablesArray), params=params, headers=headers )
    return r

def ws_get_variable(config, variablename):
    headers={}
    params={}
    init_params_headers(config, headers, params)
    
    url = "%s/integration/processes/%s/variables/%s" % (config['url'], config['project_key'], variablename)
    r = requests.get(url, verify=False, params=params, headers=headers )
    if (r.status_code == 200):
        values = r.json()
        return values['data']
    else:
        return 0

def ws_get_variables(config):
    headers={}
    params={}
    init_params_headers(config, headers, params)

    url = "%s/integration/processes/%s/variables" % (config['url'], config['project_key'])
    r = requests.get(url, verify=False, params=params, headers=headers )
    if (r.status_code == 200):
        values = r.json()
        return values['data']
    else:
        print("Error: ws_get_variables %s" % r.json()['data'])
        return []

def ws_delete_variable(config, variablename):
    headers={}
    params={}
    init_params_headers(config, headers, params)

    url = "%s/integration/processes/%s/variables/%s" % (config['url'], config['project_key'], variablename)
    r = requests.delete(url, verify=False, params=params, headers=headers )
    return r.status_code

def ws_delete_variables(config):
    variables = ws_get_variables(config)
    for variable in variables:
        ws_delete_variable(config, variable['name'])

def ws_get_processes(config):
    headers={}
    params={}
    init_params_headers(config, headers, params)

    url = "%s/integration/processes" % (config['url'])
    r = requests.get(url, verify=False, params=params, headers=headers )
    if (r.status_code == 200):
        values = r.json()
        return values['data']
    else:
        return r

def ws_get_project_info(config):
    headers={}
    params={}
    init_params_headers(config, headers, params)

    url = "%s/integration/processes/%s" % (config['url'], config['project_key'])

    return(requests.get(url, verify=False, params=params, headers=headers ))


def ws_get_project_meta_info(config):
    headers={}
    params={}
    init_params_headers(config, headers, params)

    url = "%s/integration/csv/%s/meta" % (config['url'], config['project_key'])

    r = requests.get(url, verify=False, params=params, headers=headers )
    if (r.status_code == 200):
        values = r.json()
        return values['data']
    else:
        return r



def main(argv):

    if len(argv) == 1:
        # update the configuration with your environment
        config = {
            "url": '',
            "user_id": '',
            "api_key": '',
            "org_key": '',
            "project_key": '',
        }
    else:
        # load the configuration from a json file provided as a parameter of this python program
        with open(argv[1], 'r') as file:
            config = json.load(file)

    config['sign'] = ws_post_sign(config)
    # Example to get the activities and their service time
    r = ws_query_post(config, "SELECT \"ACTIVITY\", count(*), AVG(SERVICETIME) FROM EVENTLOG GROUP BY \"ACTIVITY\"")
    if r.status_code == 200:
        print ('SQL returns: %s' % r.json())

if __name__ == "__main__":
    main(sys.argv)
