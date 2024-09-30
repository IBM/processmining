import IPMClient as ipm
import pandas as pd
import json



ipmConfig = {
    "url":"https://pm-patrick-process-miner.fyre.ibm.com",
    "userid":"task.miner",
    "apikey":"d8org223anqr2kvu"
}

ipmConfig = {
    "url":"https://pm-patrick-process-miner.fyre.ibm.com",
    "userid":"maintenance.admin",
    "apikey":"k5siu71a93c61asf"
}

ipmConfig = {
    "url":"https://pharoses1.fyre.ibm.com",
    "userid":"task.miner",
    "apikey":"8a5kga87eqvd1180"
}



ipmClient = ipm.Client(ipmConfig['url'], ipmConfig['userid'], ipmConfig['apikey'])


CO = ipmClient.createProject('CO', '')
CO.uploadCSVApplyBackupRunMining('IPMClient/data/Client Onboarding.zip', 'IPMClient/data/Client Onboarding.idp')
CO_ADMIN_NO_ORG = ipmClient.getProjectByName('CO_ADMIN_NO_ORG')
dashboards = CO.retrieveDashboards()
stats = CO.retrieveModelStatistics()

tenants = ipmClient.retrieveTenants()
accounts = ipmClient.retrieveAccounts(tenants[1]) # not permitted for Owners only for admin
organizations = ipmClient.retrieveOrganizations()
CO = ipmClient.getProjectByName('CO')
if CO:
    ipmClient.deleteProject(CO)
user = ipmClient.getAccountByUserName('user1.lab')
if not user:
    user = ipmClient.createAccount(
        {"firstName": "User1",
        "lastName": "Lab",
        "country": "FR",
        "email": "User1.Lab@ibm.com",
        "agentEnabled": True,
        "technicalUser": False,
        "active": True,
        "password": "Passw0rd!",
        "username": "user1.lab"})
if user:
    ipmClient.deleteAccount(user)
print('done')
'''
ipmClient = ipm.Client(ipmConfig['url'], ipmConfig['userid'], ipmConfig['apikey'])
ipmClient.retrieveProjects()
groups = ipmClient.retrieveGroups()
MultiTenantAdministrators = ipmClient.getGroupByName(groups, 'MultiTenantAdministrators')
Owners = ipmClient.getGroupByName(groups, 'Owners')

accounts=ipmClient.retrieveAccounts()
'''

