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
    if (config['version']!="1.13.1+"):
        params.update({'uid':config['user_id'] , 'ts': config['ts'] , 'sign' : config['sign'], 'org' : config['org_key']})
        headers.update({"content-type": "application/json"})
    else:   
        params.update({'org' : config['org_key']})     
        headers.update({"content-type": "application/json", "Authorization": "Bearer %s" % config['sign'] })


def getTimestamp():
    return str(int(time.time() * 1000) + TIME_ADJUST) ;

def hmacSHA256(api_key, values):
    message = bytes("".join(values),encoding='utf8')
    return base64.b64encode(hmac.new( bytes(api_key, encoding='utf8'), message, digestmod=hashlib.sha256).digest()).decode("utf-8")

def ws_post_sign(config):
    if (config['version']!="1.13.1+"):
        # for version prior to 1.13.1
        ts = getTimestamp()
        signature = hmacSHA256(config['api_key'], [config['user_id'], ts])
        #we need to keep a ts compliant with the signature. So let's put that directly in config
        config['ts']=ts
        return signature
    else:
        url = "%s/integration/sign" % config['url']
        headers = {"content-type": "application/json"}
        data = { 'uid' : config['user_id'], 'apiKey' : config['api_key']}
        if( PRINT_TRACE) : print("REST CALL: "+url+" "+str(data))
        r = requests.post(url, verify=False, data=json.dumps(data), headers=headers)
        if (r.status_code != 200):
            print("Error: get signature: %s" % r.json()['data'])
            return 0      
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
        return values['data']['dashboards']
    else:
        return r

# Return the dashboard Id provided by name
def ws_get_dashboard(config, dashboard_name) :
    dashboards = ws_get_dashboards(config)
    for dashboard in dashboards:
        if (dashboard['name'] == dashboard_name):
            return dashboard
    return 0

# Returns only the table widgets in the dashboard_name
def ws_get_widgets(config, dashboard_name):
    dashboard = ws_get_dashboard(config, dashboard_name)
    if dashboard == 0 :
        print("ERROR: dashboard does not exist")
        return 0
    dashboard_id = dashboard['id']

    headers={}
    params={}
    init_params_headers(config, headers, params)

    url = "%s/analytics/integration/dashboard/%s/%s/list" % (config['url'], config['project_key'], dashboard_id)

    r = requests.get(url, verify=False, params=params, headers=headers )
    widgets = r.json()
    return widgets['data']['widgets']

def ws_get_widget_values(config, mywidget):
    dashboard_id = mywidget.get('dashboard_id')
    if dashboard_id is None:
        # add the dashboard_id to the widget data
        print("....searching dashboard_id")
        dashboard = ws_get_dashboard(config, mywidget['dashboard_name'])
        if (dashboard == 0) :
            print("ERROR: dashboard does not exist")
            return 0
        else:
            # Store the dashboard id in the widget to avoid calling again the rest API to retrieve the dashboard by name
            mywidget['dashboard_id'] = dashboard['id']

    headers={}
    params={}
    init_params_headers(config, headers, params)

    url = "%s/analytics/integration/dashboard/%s/%s/%s/retrieve" % (config['url'],
                                                                        config['project_key'],
                                                                        mywidget['dashboard_id'],
                                                                        mywidget['widget_id'])

    r = requests.get(url, verify=False, params=params, headers=headers )
    values = r.json()
    return values['data']

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


