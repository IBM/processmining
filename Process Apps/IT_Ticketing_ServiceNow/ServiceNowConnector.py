import requests, json
import pandas as pd
import datetime


def ws_get_incidents(config):
    headers={"content-type": "application/json"}
    params={}

    # Restrict the returned data to the fields we need
    DESCRIPTION_COLS = 'number,sys_id,short_description,priority,severity,urgency,impact,category,subcategory,close_code,contact_type,active'
    STATE_COLS = 'sys_created_on,sys_created_by,opened_at,opened_by,resolved_at,resolved_by,closed_by,closed_at,reopened_time,reopened_by,sys_updated_on,sys_updated_by,incident_state,hold_reason'
    ASSIGNMENT_COLS = 'assignment_group,reassignment_count'
    RELATION_COLS = 'parent_incident,child_incidents'
    TASKS_COLS = 'activity_due,due_date'
    PERFORMANCE_COLS = 'sla_due,made_sla,business_stc,calendar_stc,reopen_count,sys_mod_count'
    params['sysparm_fields'] = DESCRIPTION_COLS +','+STATE_COLS+','+ASSIGNMENT_COLS+','+RELATION_COLS+'+'+TASKS_COLS+'+'+PERFORMANCE_COLS
    
    # sysparm_no_count get the number of records false: Execute a select count(*). DOES NOT WORK?
    params['sysparm_exclude_reference_link'] = True

    # All parameters are case-sensitive. Queries can contain more than one entry, such as sysparm_query=<col_name><operator><value>[<operator><col_name><operator><value>].
    # For example: (sysparm_query=caller_id=javascript:gs.getUserID()^active=true)
    # sysparm_query=sys_updated_on>2018-01-01^sys_updated_on<2019-01-01)
    params['sysparm_query']=''
    if 'from_date' in config:
        params['sysparm_query']='sys_updated_on>=' + config['from_date']
    if 'to_date' in config:
        if params['sysparm_query'] != '':
            params['sysparm_query'] = params['sysparm_query'] + '^sys_updated_on<=' + config['to_date']
        else:
            params['sysparm_query'] = 'sys_updated_on<=' + config['to_date']

    if 'incident_limit' in config:
        if config['incident_limit'].isnumeric():
            if int(config['incident_limit']) > 0:
                params['sysparm_limit'] = config['incident_limit']
            # should we check if the limit is bigger than 1000? (that is the default)
    if 'incident_offset' in config:
        if config['incident_offset'].isnumeric():
            if int(config['incident_offset']) > 0:
                params['sysparm_offset'] = config['incident_offset']

    url  = config['url'] + "/table/incident"

    r = requests.get(url, auth=(config['user'], config['pwd']), headers=headers, params=params)
    if (r.status_code == 200):
        return json.loads(r.content)['result']
    else:
        print('ServiceNow REST API: %s' % json.loads(r.content))
        return []
    
def ws_get_users(config):
    headers={"content-type": "application/json"}
    params={}
    # Restrict the returned data to the fields we need
    params['sysparm_fields'] = 'sys_id,user_name'

    url  = config['url'] + "/table/sys_user"
    r = requests.get(url, auth=(config['user'], config['pwd']), headers=headers, params=params)
    if (r.status_code == 200):
        return json.loads(r.content)['result']
    else:
        print('ServiceNow REST API: %s' % json.loads(r.content))
        return []
    
def ws_get_user_groups(config):
    headers={"content-type": "application/json"}
    params={}
    # Restrict the returned data to the fields we need
    params['sysparm_fields'] = 'sys_id,name'

    url  = config['url'] + "/table/sys_user_group"
    r = requests.get(url, auth=(config['user'], config['pwd']), headers=headers, params=params)
    if (r.status_code == 200):
        return json.loads(r.content)['result']
    else:
        print('ServiceNow REST API: %s' % json.loads(r.content))
        return []

def ws_get_incident_audit(config, documentkey):
    headers={"content-type": "application/json"}
    params = {"tablename": 'incident'}
    if (documentkey != 0): # documentkey refers to the sys_id of the INCIDENT.
        params['documentkey'] = documentkey
    url  = config['url'] + "/table/sys_audit"
    r = requests.get(url, auth=(config['user'], config['pwd']), headers=headers, params=params)
    if (r.status_code == 200):
        return json.loads(r.content)['result']
    else:
        print('ServiceNow REST API: %s' % json.loads(r.content))
        return []

    
def create_user_name(df, users_df, user_field):
    # opened_by is a dict {'link': 'https://dev59014.service-now.com/api/now/table/sys_user/9ee1b13dc6112271007f9d0efdb69cd0', 'value': '9ee1b13dc6112271007f9d0efdb69cd0'}
    # We need its value in user_id, and we need to merge it with users_df
    # When we kept the link: df['resource_id'] = df[user_field].str['value']. Not needed with params['sysparm_exclude_reference_link'] = True

    df['resource_id'] = df[user_field]
    df = df.merge(users_df, left_on='resource_id', right_on='user_id', how='left')
    # Sometimes: {'link': 'https://dev59014.service-now.com/api/now/table/sys_user/glide.maint', 'value': 'glide.maint'}. 
    # In this case, the merge does not work.    
    df.loc[df['user_name'].isnull(), 'user_name'] = df['resource_id']  

    return df

def create_activities(df, users_df, incident_state):
    df = df.copy()
    df['activity'] = incident_state
    # match works for python 3.10 we need an alternative
    if incident_state == 'Ticket Created': 
        df = df[df['sys_created_on'] != '']
        df['start_date'] = df['sys_created_on']
        # sys_created_by is directly the user name
        df['user_name'] = df['sys_created_by']
    elif incident_state == 'Ticket Opened':
        df = df[df['opened_at'] != '']
        df['start_date'] = df['opened_at']
        df = create_user_name(df, users_df, 'opened_by')
    elif incident_state == 'Ticket Resolved':
        df= df[df['resolved_at'] != '']
        df['start_date'] = df['resolved_at']
        df = create_user_name(df, users_df, 'resolved_by')           
    elif incident_state == 'Ticket Closed':
        df= df[df['closed_at'] != '']
        df['start_date'] = df['closed_at']
        df = create_user_name(df, users_df, 'closed_by')  
    elif incident_state == 'Ticket Reopened':
        df= df[df['reopened_time'] != '']
        df['start_date'] = df['reopened_time']
        df = create_user_name(df, users_df, 'reopened_by')  # We need to check, no sample data yet
    elif incident_state ==  'Ticket On Hold':
        df=df[df['incident_state'] == '3']
        # date: take the latest modification date. That's probably not correct but closest
        df['start_date'] = df['sys_updated_on']
        # sys_updated_by is directly the user name
        df['user_name'] = df['sys_updated_by'] 
        # add hold reason to the activity
        df['activity'] = df['activity'] + ' ' + df['hold_reason_name'] 
    elif incident_state == 'Ticket Canceled':
        df=df[df['incident_state'] == '8']
        df['start_date'] = df['sys_updated_on']    # The canceled date is not stored. Maybe in the audit
        # sys_updated_by is directly the user name
        df['user_name'] = df['sys_updated_by']
        
    return df


# When loaded into Process Mining, the import works.
# To run/debug this program as a standalone code, we redefine the ProcessAppException class below
try:
    DEBUG = 0
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

    # Check parameters
    # check that the input dates have the expected date format
    date_format = '%Y-%m-%d'
    if 'from_date' in config:
        try:
        # formatting the date using strptime() function to raise an error if date format problem
            datetime.datetime.strptime(config['from_date'], date_format)
        # If the date validation goes wrong
        except Exception as e:   # printing the appropriate text if ValueError occurs
            raise ProcessAppException("Incorrect from date format, should be like this 2022-10-08" + str(e))
    if 'to_date' in config:
        try:
        # formatting the date using strptime() function to raise an error if date format problem
            datetime.datetime.strptime(config['to_date'], date_format)
        # If the date validation goes wrong
        except Exception as e:   # printing the appropriate text if ValueError occurs
            raise ProcessAppException("Incorrect to date format, should be like this 2022-10-08" + str(e))

    incidents_list = ws_get_incidents(config)
    if incidents_list == []: # KeyError
        return()

    incidents_df = pd.DataFrame(incidents_list)
    if DEBUG: 
        incidents_df.to_csv('incidents_REST.csv', index=None)
        print(len(incidents_df))
        print(incidents_df.columns)

    incidents_df.rename(columns={'sys_id':'incident_id'}, inplace=True)

    # Get sys_user data
    user_list = ws_get_users(config)
    users_df = pd.DataFrame(user_list)
    users_df.rename(columns={'sys_id':'user_id'}, inplace=True)
    
    incident_states_df = pd.DataFrame({
        'state': ['1', '2', '3', '6', '7', '8'],
        'incident_state_name':['Ticket New', 'Ticket In Progress', 'Ticket On Hold', 'Ticket Resolved','Ticket Closed','Ticket Canceled']
        })
    hold_reasons_df = pd.DataFrame({
        'hold_reason_code': ['1','2','3','4'],
        'hold_reason_name': ['Awaiting Caller','Awaiting Evidence', 'Awaiting Problem Resolution','Awaiting Vendor']})

    # Join to get the hold description in column hold_reason_name
    incidents_df = incidents_df.merge(hold_reasons_df, left_on='hold_reason', right_on='hold_reason_code', how='left')
    # Join to get the incident_status description in column incident_state_name
    incidents_df = incidents_df.merge(incident_states_df, left_on='incident_state', right_on='state', how='left')

    create_df = create_activities(incidents_df, users_df, 'Ticket Created')
    open_df = create_activities(incidents_df, users_df, 'Ticket Opened')
    resolved_df = create_activities(incidents_df, users_df, 'Ticket Resolved')
    closed_df = create_activities(incidents_df, users_df, 'Ticket Closed')
    reopened_df = create_activities(incidents_df, users_df, 'Ticket Reopened')
    canceled_df = create_activities(incidents_df, users_df, 'Ticket Canceled')
    awaiting_df = create_activities(incidents_df, users_df, 'Ticket On Hold')

    # Create the event log
    event_log_df = pd.concat((create_df, open_df, resolved_df, closed_df, reopened_df, canceled_df, awaiting_df))
    event_log_df.drop(columns=['sys_created_on','sys_created_by','opened_at','opened_by','resolved_at','resolved_by','reopened_time','reopened_by','resource_id','user_id'], inplace=True)
    event_log_df['source'] = 'INCIDENT TABLE'
    event_log_df.drop(columns=['state','hold_reason','closed_by', 'closed_at','parent_incident','incident_id','sys_updated_by','hold_reason_code',
                  'hold_reason_name','incident_state'], inplace=True)
    
    
    # Get sys_user_group data
    user_group_list = ws_get_user_groups(config)
    user_groups_df = pd.DataFrame(user_group_list)
    user_groups_df.rename(columns={'sys_id':'group_id', 'name':'group_name'}, inplace=True)
    if DEBUG : 
        user_groups_df.to_csv('user_groups_df.csv', index=None)

    event_log_df = event_log_df.merge(user_groups_df, left_on='assignment_group', right_on='group_id', how='left')

    # Sort the column positions
    event_log_df = event_log_df[['number', 'activity', 'start_date','user_name', 'group_name','incident_state_name', 'active','priority', 'urgency', 'severity','contact_type',
                             'short_description', 'category', 'subcategory', 'close_code', 'made_sla', 'business_stc', 'reassignment_count', 
                             'calendar_stc', 'impact','sys_mod_count',  'reopen_count', 'source','sys_updated_on']]

    # Get sys_audit data related to incident table
    incident_audit = ws_get_incident_audit(config, 0)
    if incident_audit == []:
        if DEBUG : print('No incident audit data') # quit
        return (event_log_df)
    

    incident_audit_df = pd.DataFrame(incident_audit)
    incident_audit_df.rename(columns={'sys_id':'audit_id'}, inplace=True)
    if DEBUG : 
        incident_audit_df.to_csv("incident_audit.csv", index=None)
        print(incident_audit_df['fieldname'].unique())
    
    # join tables to retrieve the incident num from the sys audit table(the documentkey)
    incident_audit_df = incident_audit_df.merge(incidents_df[['incident_id', 'number']], left_on='documentkey', right_on='incident_id', how='left')    

    # Track status changes and compare with status in the INCIDENT table. Add new one (historical)
    # Track hold_reason to complement the Ticket On Hold activity
    # Track assignement changes that can reveal pingpong or be the cause of delays (assignment_group, assigned_to happen at the same time. Keep both)

    # incident state changes
    instance_state_changes_df = incident_audit_df[incident_audit_df['fieldname']=='incident_state']
    # get the state name from incident_states_df
    instance_state_changes_df = instance_state_changes_df.merge(incident_states_df, left_on='newvalue', right_on='state', how='left')
    instance_state_changes_df.rename(columns={'sys_created_on':'start_date', 'incident_state_name':'activity', 'user':'user_name'}, inplace = True)
    if DEBUG :
        instance_state_changes_df.to_csv('instance_state_changes_df.csv', index=None)     
    
    # Complement Ticket On Hold activity with hold_reason if any
    hold_reason_changes_df = incident_audit_df[incident_audit_df['fieldname']=='hold_reason']
    hold_reason_changes_df = hold_reason_changes_df[~hold_reason_changes_df['newvalue'].isna()]
    # get the hold_reason name
    hold_reason_changes_df = hold_reason_changes_df.merge(hold_reasons_df, left_on='newvalue',right_on='hold_reason_code', how='left')
    if DEBUG:
        hold_reason_changes_df.to_csv('hold_reason_changes_df.csv', index=None)

    # merge instance state changes with on hold changes, to complement the activity name
    instance_state_changes_df = instance_state_changes_df.merge(hold_reason_changes_df[['sys_created_on', 'hold_reason_name']], left_on='start_date', right_on='sys_created_on', how='left')
    # replace NaN that result from failed merge
    instance_state_changes_df = instance_state_changes_df.fillna('')
    # concat the Ticket On Hold activity with the reason name if any
    instance_state_changes_df.loc[instance_state_changes_df['hold_reason_name'] != '', 'activity'] = instance_state_changes_df['activity']+' '+instance_state_changes_df['hold_reason_name']
    # Keep interesting columns only
    instance_state_changes_df['source']='SYS_AUDIT TABLE'

    instance_state_changes_df = instance_state_changes_df[['number','activity','start_date','user_name','source']]

    # Optionnally, we could copy the contextual data (case attributes) into the instance_state_changes_df.
    # We are using the create_df to merge left the create_df data with the instance_state_changes_df. We need to have only 1 row per incident 'number' 
    # otherwise the merge left creates more than one row per instance_state_change_df
    # instance_state_changes_df = instance_state_changes_df.merge(create_df.drop(columns=['activity','start_date','user_name','source']),left_on=['number'],right_on=['number'],how='left',right_index=False)
    # but I don't think that we need these contextual data for these activities, as we have them already for the case from INCIDENT table

    if DEBUG:
        print('number of incidents in INCIDENT table : %s' %len(create_df))
        print('number of state changes in AUDIT : %s' % len(instance_state_changes_df))

    if DEBUG:
        instance_state_changes_df.to_csv('state_changes_df.csv', index=None)

    # Concat the event log from INCIDENT TABLE AND from the SYS_AUDIT TABLE and remove duplicates
    # duplicates are matched against 'number','activity','start_date'
    event_log_df = pd.concat([event_log_df, instance_state_changes_df])
    event_log_df = event_log_df[~event_log_df.duplicated(subset=['number','activity','start_date'], keep='first')]
    if DEBUG:
        print(event_log_df[['number','activity','start_date']])
    
    # Now let's add the activities that are assigning the ticket to a group. 
    # We could do this for user too, but the date is the same, so it is the same activity
    group_changes_df = incident_audit_df[incident_audit_df['fieldname']=='assignment_group']
    group_changes_df = group_changes_df[group_changes_df['newvalue']!='']
    group_changes_df = group_changes_df.merge(user_groups_df, left_on='newvalue', right_on='group_id', how='left')
    group_changes_df = group_changes_df[['sys_created_on','number','user','group_name']]
    # Transform into an event log
    group_changes_df.rename(columns={'sys_created_on':'start_date', 'user':'user_name'}, inplace=True)
    if DEBUG:
        print(group_changes_df.columns)
    group_changes_df['activity'] = 'Ticket Assigned'
    group_changes_df['source'] = 'AUDIT'


    if DEBUG :
        event_log_df.to_csv('eventlog.csv', index=None)
        return(event_log_df)
    else:
        return(event_log_df)



if __name__ == "__main__":

    # Create a json file 'my_config.json' that includes your configuration
    try: 
        f = open('my_config.json')
        my_config = json.load(f)
    except Exception as e:
        # For testing, you can use this json configuration
        print("*** WARNING: %s. Create one, or update my_config object in the code" % e)
        my_config = {
            "url": 'https://<SERVICENOW/api/now/',
            "user": 'admin',
            "pwd": 'MY PASSWORD'
            #"incident_limit": '0',
            #"incident_offset": '0'
            #"from_date": '2018-01-01',
            #"to_date": '2019-01-01'
        }
    # DEBUG variable used to print and generate CSV files (1 or 0)
    DEBUG = 0
    context = {'config': my_config}
    eventlog_df = execute(context)
    print("End of local execution")
    if DEBUG:
        print(eventlog_df)
