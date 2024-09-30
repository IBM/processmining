import IPMClient as ipm
import json
import sys
import os

def main(argv):

    getConfigFrom = 'FILE'
    configFileName = 'IPMClient/IPMConfig.json'

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
    project = client.getProjectByKey('bank-account-closure')
    svg = project.retrieveSVG()
    with open('mySVG.svg', 'w') as file:
        file.write(svg)
        file.close()

    project._dumpToFile = True
    #result = project.retrieveKPISettings()
    #result = project.retrieveModelStatistics()
    #result = project.retrieveDeviations()
    #result = project.retrieveFilters()
    #project.dumpJsonToFile(result, 'filters')

    #result = project.retrieveTemplates()
    #project.retrieveStatus()
    #result = project.retrieveVariants()
    #result = project.retrieveSettings()
    #r = project.retrieveSettingsActivityCost()
    #r = project.retrieveSettingsActivityWorkingTime()
    #project.dumpJsonToFile(r, 'project-settings activities-working-time')
    with open('json_result_examples/filters.json', 'r') as file:
        filters = json.load(file)
    #stat2 = project.retrieveModelStatistics(filters)
    # To apply a transient filter, create an ARRAY of JSON (filters) see examples
    #stats1 = project.retrieveModelStatistics()
    #ActStats = project.getActivityStatistics(stats1)
    #BOStats = project.getActivityStatistics(stats1,'BO Service Closure')
    #TransStats = project.getTransitionStatistics(stats1)
    #StartStats = project.getTransitionStatistics(stats1, 'START', 'Request created')
    #processStats = project.getProcessStatistics(stats1)
    #stats2 = project.retrieveModelStatistics([filter])
    #diff  = stats1['processAnalysis']['filteredCases'] - stats2['processAnalysis']['filteredCases']
    #deviations =  project.retrieveDeviations()
    #deviations =  project.retrieveDeviations(filters)
    #kpis = project.retrieveKpiStatus()
    #kpis = project.retrieveKpiStatus(filters)
    #customMetrics = project.retrieveCustomMetrics()
    # ERROR project.setActivityCost returns 400
    #result = project.setActivityCost('BO Service Closure', 100, 'Manual', '2019-11-14T00:00:00.000Z')
    '''
    groups = client.retrieveGroups()
    owners = client.getGroupByName(groups, 'Owners')

    accountData = {
        "firstName": "John",
        "lastName": "Sam",
        "country": "IN",
        "email": "john.sam@ibm.com",
        "agentEnabled": True,
        "technicalUser": False,
        "active": True,
        "password": "John12345!",
        "username": "john.sam"
    }

    account = client.createAccount(accountData)
    client.addAccountToGroup(account, owners['groupId'])
    org1 = client.getOrganizationByName('myBank')
    org2 = client.getOrganizationByName('MAPFRE')
    org1.addAccount(account)
    org2.addAccount(account)
    client.deleteAccount(account)
'''
    print('done')


if __name__ == "__main__":
    main(sys.argv)