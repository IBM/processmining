import IPMClient as ipm
import json
import sys
import os

def main(argv):

    getConfigFrom = 'FILE'
    configFileName = './IPMConfig_nextgen.json'

    # update the clienturation with your environment
    # retrieve from OS variables
    if getConfigFrom == 'OS':
        url :str= os.getenv('PM_API_URL')
        userid :str  = os.getenv('PM_API_USER')
        apikey :str =os.getenv('PM_API_KEY')
    elif getConfigFrom == 'VARS':
    # or update these variables
        url = 'PROCESSMININGURL'
        userid = 'PROCESSMINGUSERID'
        apikey= 'USER_APIKEY'
    elif getConfigFrom == 'FILE':
    # or load a file that contains JSON config
        with open(configFileName, 'r') as file:
            config = json.load(file)
            url = config['url']
            userid = config['userid']
            apikey = config['apikey']
    
    client = ipm.Client(url, userid, apikey)
    client.setTrace(True, 1)
    project = client.getProjectByName('BAC')
    dashboards = project.getDashboards()
    dashboard = project.getDashboardByName('test')
    widget = dashboard.getWidgetByName('alerts')
    values = widget.retrieveValues()
    stats1 = project.retrieveModelStatistics()

    with open('json_result_examples/filters.json', 'r') as file:
        jsonfilter = json.load(file)
        filters = jsonfilter['filters']
    stat2 = project.retrieveModelStatistics(filters)
    #filter = project.createFilterAttribute('activity', 'Authorization Requested', True, 'ANY')
    #stats2 = project.retrieveModelStatistics([filter])
    print('done')


if __name__ == "__main__":
    main(sys.argv)