import requests
from requests.auth import HTTPBasicAuth
import json
import pandas as pd
import datetime as dt
from datetime import datetime

def ws_count_tickets(config):
    auth = HTTPBasicAuth(config['user'],config['token'])

    query = 'project = ' + config['project_key']
    if 'from_date' in my_config:
        query = query + ' AND created >= ' + config['from_date']
    if 'to_date' in my_config:
        query = query + ' AND created <= ' + config['to_date']

    params = {
    'jql': query,
    'fields':'created',
    'maxResults' : 1,
    'startAt': 0
    }

    headers = {
    "Accept": "application/json"
    }
    url = config['url']+'search'
    response = requests.request(
        "GET",
        url,
        headers=headers,
        params=params,
        auth=auth)
    if response.status_code == 200:
        return json.loads(response.text)
    else: 
        print("error count ticket %s " % response.status_code)
        return None

# Standard fields that can be used in all JIRA/environements
# 'created,creator,project,resolution,resolutiondate,updated,duedate,timespent,timeestimate,timeoriginalestimate,status,issuetype,reporter,priority,assignee'
# Feel free to add or remove fields.
# If you need custom fields, first determine which customfield store the data you want (ex customer name), and add it to the list
# You will have to add the key into the create_ticket() function too.
standard_fields = 'created,creator,project,resolution,resolutiondate,updated,duedate,timespent,timeestimate,timeoriginalestimate,status,issuetype,reporter,priority,assignee'


def ws_get_tickets(config):
    auth = HTTPBasicAuth(config['user'],config['token'])

    query = 'project = ' + config['project_key']
    if 'from_date' in my_config:
        query = query + ' AND created >= ' + config['from_date']
    if 'to_date' in my_config:
        query = query + ' AND created <= ' + config['to_date']
    params = {
    'jql': query,
    'fields': standard_fields,
    'expand' : 'changelog',
    'maxResults' : config['maxResults'],
    'startAt': config['startAt']
    }

    headers = {
    "Accept": "application/json"
    }
    url = config['url']+'search'
    response = requests.request(
        "GET",
        url,
        headers=headers,
        params=params,
        auth=auth)
    if response.status_code == 200:
        return json.loads(response.text)
    else: 
        print("error get ticket %s " % response.status_code)
        return None
    
def ws_get_projects(config):

    auth = HTTPBasicAuth(config['user'],config['token'])

    headers = {
    "Accept": "application/json"
    }
    url = config['url']+'project'
    response = requests.request(
        "GET",
        url,
        headers=headers,
        auth=auth)
    if response.status_code == 200:
        return json.loads(response.text)
    else: 
        print("error get project %s " % response.status_code)
        return {'issues':[]}
    
def ws_get_ticket(config):

    auth = HTTPBasicAuth(config['user'],config['token'])

    headers = {
    "Accept": "application/json"
    }
    url = config['url']+'issue/'+config['ticket_id']
    response = requests.request(
        "GET",
        url,
        headers=headers,
        auth=auth)
    if response.status_code == 200:
        return json.loads(response.text)
    else: 
        print("error get ticket %s " % response.status_code)
        return None
    
def create_ticket(issue):
    ticket = { }
    ticket['ticket_id'] = issue['key']
    
    issue_fields = issue['fields']
    ticket['created'] = issue_fields['created']
    # We could anonymize the name (same for the changelog)
    # use creator.displayName for full name or creator.key. creator.key often contains the full name too...
    ticket['creator'] = issue_fields['creator']['displayName']
    ticket['resolutiondate'] = issue_fields['resolutiondate']
    ticket['duedate'] = issue_fields['duedate']  
    ticket['timespent'] = issue_fields['timespent']
    ticket['timeestimate'] = issue_fields['timeestimate']
    ticket['timeoriginalestimate'] = issue_fields['timeoriginalestimate']
    ticket['project_key'] = issue_fields['project']['key']

    #ticket['updated'] = issue_fields['updated']
    #ticket['status_name'] = issue_fields['status']['name']
    #ticket['status_id'] = issue_fields['status']['id']


    # Fields that are dicts. Pick a value in the dict
    if 'issuetype' in issue_fields: 
        ticket['type'] = issue_fields['issuetype']['name']
    else:
        ticket['type'] = None
    if issue_fields['resolution']:
        ticket['resolution'] = issue_fields['resolution']['name']
    else: ticket['resolution'] = None 
    if issue_fields['reporter']:
        ticket['reporter'] = issue_fields['reporter']['displayName']
    else: ticket['reporter'] = None 
    if issue_fields['priority']:
        ticket['priority'] = issue_fields['priority']['name']
    else: ticket['priority'] = None 
    if issue_fields['assignee']:
        ticket['assignee'] = issue_fields['assignee']['displayName']
    else: ticket['assignee'] = None 

    return(ticket)

def create_ticket_changelog(ticket_id, author, datestr, item):
    ticket_change = {}
    ticket_change['ticket_id'] = ticket_id
    ticket_change['author'] = author
    ticket_change['created'] = datestr
    ticket_change['field'] =  item['field']
    ticket_change['from'] = item['from']
    ticket_change['fromString'] = item['fromString']
    ticket_change['to'] = item['to']
    ticket_change['toString'] = item['toString']
    return ticket_change

# Useful function to only see the issue fields that are not None
def explore_issue_fields(issue):
    fields = issue['fields']
    print("Issue: %s" % issue['key'])
    for field in fields:
        if fields[field]:
            print("%s : %s" %(field, fields[field]))


def XformToIso(d):
    if d == '':
        return ''
    else:
        aDate = datetime.strptime(d,'%Y-%m-%dT%H:%M:%S.%f%z')
    return  aDate.isoformat(sep = 'T', timespec = 'milliseconds')



# When loaded into Process Mining, the import works.
# To run/debug this program as a standalone code, we redefine the ProcessAppException class below
try:
    STANDALONE = 0
    from process_app import ProcessAppException
except: 
    class ProcessAppException(Exception):
        def __init__(self, message):
            self.message=message
            super().__init__(self.message)
        def getMessage(self):
            return self.message

def execute(context):
    my_config = context['config']

    # if any, check the minimal number of issue per project, unless we discard the project. Default is 50
    if 'minimalIssueNumber' not in my_config:
        my_config['minimalIssueNumber'] =  50


    # config['projects'] can be empty, or contain a list of projects separated by a comma
    # get the list of projects
    if 'projects' not in my_config:
        projects = ''
    else:
        projects = my_config['projects']
    if projects == '':
        # get all the projects
        projects = ws_get_projects(my_config)
        print("JIRA Projects : %s projects retrieved" % len(projects))
        # discard projects with less than 50 issues (should that be a parameter?)
        kept_projects = []
        for project in projects:
            my_config['project_key']=project['key']
            result = ws_count_tickets(my_config)
            # Let's remove automatically the projects with less than my_config['minimalIssueNumber'] issues
            if result['total'] >= my_config['minimalIssueNumber']:
                print('Project key = %s , name = %s : contains %s issues' % (project['key'],project['name'],result['total']) )
                kept_projects.append(project)
            else:
                print('Project key = %s , name = %s : contains %s issues <*** DISCARDED ***>' % (project['key'],project['name'],result['total']) )
        projects = kept_projects

    else:
        my_config['projects'] = my_config['projects'].replace(' ','')
        project_keys = my_config['projects'].split(',')
        projects = []
        for project in project_keys:
            projects.append({'key': project})

           

    # from_date and to_date field to limit the scope whenever needed
    # check that the input dates have the expected date format
    date_format = '%Y-%m-%d'
    if 'from_date'in my_config:
        try:
        # formatting the date using strptime() function to raise an error if date format problem
            dt.datetime.strptime(my_config['from_date'], date_format)
        # If the date validation goes wrong
        except Exception as e:   # printing the appropriate text if ValueError occurs
            raise ProcessAppException("Incorrect from date format, should be like this 2022-10-08" + str(e))
    if 'to_date' in my_config:
        try:
        # formatting the date using strptime() function to raise an error if date format problem
            dt.datetime.strptime(my_config['to_date'], date_format)
        # If the date validation goes wrong
        except Exception as e:   # printing the appropriate text if ValueError occurs
            raise ProcessAppException("Incorrect to date format, should be like this 2022-10-08" + str(e))

    all_tickets = []
    changelog_list = []
    # get the list of issues for each project. 
    for project in projects:
        my_config['project_key']=project['key']
        # We are paging to retrieve the issues
        i = 0
        retrieved = 0
        total = 1
        while retrieved < total:
            my_config['startAt'] = i * my_config['maxResults']
            i += 1
            result = ws_get_tickets(my_config)
            total = result['total']
            issues = result['issues']
            retrieved += len(issues)
            print('Project %s: Retrieved %s issues out of %s' % (my_config['project_key'],retrieved, total))
            for issue in issues:
                # Create a list of tickets
                ticket = create_ticket(issue)
                all_tickets.append(ticket)
                # Create a list of changelogs, add the ticket_id
                changelog = issue['changelog']
                changelog['ticket_id'] =  issue['key']
                # We could add other case-level data
                changelog_list.append(issue['changelog'])

    print("Total of %s tickets created from %s projects" % (len(all_tickets), len(projects)))
    all_tickets_df = pd.DataFrame(all_tickets,dtype=str)

    # CHANGELOG
    # Each change log can include several changes.
    # Create the list of change logs units
    ticket_changes_list =  []
    for changelog in changelog_list:
        # there could be several histories in each change log (histories==values when calling the {ticketid}/changelog API)
        for history in changelog['histories']:
            # there could be several item changes in each history
            for item in history['items']:
                ticket_changelog = create_ticket_changelog(changelog['ticket_id'], history['author']['key'], history['created'], item)
                ticket_changes_list.append(ticket_changelog)

    print("Total number of changelogs: %s" % len(ticket_changes_list))
    all_ticket_changes_df = pd.DataFrame(ticket_changes_list)


    # CREATE THE EVENT LOG
    # Create an event log from the ticket list
    # We only have the creation date and the resolution date. We will get the other steps from the changelog
    # The creation date is used to create the first activity: Ticket Created
    # The resolution date could be used to create an activity. We would need to use the 'resolution' field to determine the activity (Done, Resolved, Cancelled, etc)
    # That could be useful if we don't have the changelog.
    # With the changelog, we will get all the activities related to status changes, therefore we can cope with that.
    # The advantage of only using the changelog is that we don't have to deal with duplicates and to compare dates.


    # Ticket creation events
    ticket_created_df = all_tickets_df.copy()
    ticket_created_df['activity'] = 'Ticket Created'
    ticket_created_df.rename(columns={'creator':'user'}, inplace=True)
    ticket_created_df['start_date'] = ticket_created_df['created']
    ticket_created_df = ticket_created_df[['ticket_id','activity','start_date','user', 'project_key','type', 'priority', 'resolutiondate', 'duedate',
        'timespent', 'timeestimate', 'timeoriginalestimate', 'resolution', 'reporter', 'assignee']]
    print("Total number of tickets created: %s" % len(ticket_created_df))

    # Create an event log from the ticket status changes
    status_changes_df = all_ticket_changes_df[all_ticket_changes_df['field']=='status'].copy()
    status_changes_df['activity'] = 'Ticket ' + status_changes_df['toString']
    status_changes_df.rename(columns={'author':'user'}, inplace=True)
    status_changes_df['start_date'] = status_changes_df['created']
    status_changes_df = status_changes_df[['ticket_id', 'activity', 'start_date','user']]
    print("Total number of status changes in changelog: %s" % len(status_changes_df))

    # Create event log from ticket assignee changes
    assignee_changes_df = all_ticket_changes_df[all_ticket_changes_df['field']=='assignee'].copy()
    assignee_changes_df['activity'] = 'Ticket Assigned'
    assignee_changes_df['start_date'] = assignee_changes_df['created']
    assignee_changes_df.rename(columns={'author':'user', 'toString':'assignee'}, inplace=True)
    assignee_changes_df = assignee_changes_df[['ticket_id', 'activity', 'start_date','user','assignee']]
    print("Total number of assignee changes in changelog: %s" % len( assignee_changes_df))

    # CREATE THE FINAL EVENT LOG
    eventlog_df = pd.concat([ticket_created_df, assignee_changes_df, status_changes_df])
    # Replace NaN by blank ''
    eventlog_df.fillna('', inplace=True)
    # Change the date format such that it is automatically understood in Process Mining
    eventlog_df['start_date'] = eventlog_df['start_date'].apply(XformToIso)
    eventlog_df['resolutiondate'] = eventlog_df['resolutiondate'].apply(XformToIso)
    eventlog_df.fillna('', inplace=True)
    # force the type to strings
    eventlog_df.astype(str)
    # duedate is just a date, no need to transform, although it is not recognized by process mining 2022-01-01
    return  eventlog_df


if __name__ == "__main__":

    # Create a json file 'my_config.json' that includes your configuration
    try: 
        f = open('my_config.json')
        my_config = json.load(f)
    except Exception as e:
        # For testing, you can use this json configuration
        print("*** WARNING: %s. Create one, or update my_config object in the code" % e)
        my_config = {
            "url":"https://<JIRA>/rest/api/3/", # Works with https://<JIRA>/rest/api/2/
            "user":"johnsmith@acme.com",
            "token":"hdGvEUCd0hp1209U32093U0gv53jx3IWNUA2xYkd",
            "maxResults":50, # Paging size. Max = 1000
            "startAt":0, # Paging offset
            "projects":"", # list of project keys separated by comma, or empty for all projects
            "minimalIssueNumber":50,
            "from_date":"", # empty or YYYY-MM-DD as from creation date
            "to_date":"" # empty or YYYY-MM-DD as to creation date
            }
    # STANDALONE variable used to print and generate CSV files (1 or 0)
    STANDALONE = 1
    context = {'config': my_config}
    eventlog_df = execute(context)
    print("End of local execution")
    if STANDALONE:
        print("Number of events in eventlog : %s" % len(eventlog_df))
        print(eventlog_df)
        eventlog_df.to_csv('jiraevents.csv', index=None)

