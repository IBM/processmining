import IPMClient as ipm
import pandas as pd
import json

ipmConfig = {
    "url":"https://pharoses1.fyre.ibm.com",
    "userid":"task.miner",
    "apikey":"8a5kga87eqvd1180"
}


ipmConfig =  {
    "url":"https://useast.services.cloud.techzone.ibm.com:27464",
    "userid":"maintenance.admin",
    "apikey":"k0rea0pg4c6ro2nq"
}

ipmConfig =  {
    "url":"https://useast.services.cloud.techzone.ibm.com:46936",
    "userid":"maintenance.admin",
    "apikey":"k0rea0pg4c6ro2nq"
}

ipmConfig =  {
    "url":"https://useast.services.cloud.techzone.ibm.com:41330",
    "userid":"maintenance.admin",
    "apikey":"k0rea0pg4c6ro2nq"
}

ipmConfig =  {
    "url":"https://useast.services.cloud.techzone.ibm.com:43997",
    "userid":"maintenance.admin",
    "apikey":"k0rea0pg4c6ro2nq"
}



ipmClient = ipm.Client(ipmConfig['url'], ipmConfig['userid'], ipmConfig['apikey'])
co = ipmClient.getProjectByName('CO')
if co:
    ipmClient.deleteProject(co)
org = ipmClient.getOrganizationByName('Finance')
co = ipmClient.createProject(org, 'CO')
co.uploadCSVApplyBackupRunMining('IPMClient/data/Client Onboarding.zip', 'IPMClient/data/Client Onboarding.idp')

## Manage users
groups = ipmClient.retrieveGroups()
owners = ipmClient.getGroupByName(groups, 'Owners')
users = [
    {"firstName": "User1",
    "lastName": "Lab",
    "country": "FR",
    "email": "User1.Lab@ibm.com",
    "agentEnabled": True,
    "technicalUser": False,
    "active": True,
    "password": "Passw0rd!",
    "username": "user1.lab"},
    {"firstName": "User2",
    "lastName": "Lab",
    "country": "FR",
    "email": "User2.Lab@ibm.com",
    "agentEnabled": True,
    "technicalUser": False,
    "active": True,
    "password": "Passw0rd!",
    "username": "user2.lab"},
    {"firstName": "User3",
    "lastName": "Lab",
    "country": "FR",
    "email": "User3.Lab@ibm.com",
    "agentEnabled": True,
    "technicalUser": False,
    "active": True,
    "password": "Passw0rd!",
    "username": "user3.lab"},
    {"firstName": "User4",
    "lastName": "Lab",
    "country": "FR",
    "email": "User4.Lab@ibm.com",
    "agentEnabled": True,
    "technicalUser": False,
    "active": True,
    "password": "Passw0rd!",
    "username": "user4.lab"},
    {"firstName": "User5",
    "lastName": "Lab",
    "country": "FR",
    "email": "User5.Lab@ibm.com",
    "agentEnabled": True,
    "technicalUser": False,
    "active": True,
    "password": "Passw0rd!",
    "username": "user5.lab"},
    {"firstName": "User6",
    "lastName": "Lab",
    "country": "FR",
    "email": "User6.Lab@ibm.com",
    "agentEnabled": True,
    "technicalUser": False,
    "active": True,
    "password": "Passw0rd!",
    "username": "user6.lab"},
    {"firstName": "User7",
    "lastName": "Lab",
    "country": "FR",
    "email": "User7.Lab@ibm.com",
    "agentEnabled": True,
    "technicalUser": False,
    "active": True,
    "password": "Passw0rd!",
    "username": "user7.lab"}
    ]
for user in users:
    account = ipmClient.createAccount(user)
    ipmClient.addAccountToGroup(account, owners['groupId'])
    org.addAccount(account)

print('DONE: set the dashboards to Shared')