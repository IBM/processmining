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
    client.setTrace(True, 0)
    
    testOrg2 = client.createOrganization('anOrg2', 'this is anOrg2')
    if client.isResponseKO(): return
 
    testOrg3 = client.getOrganizationByName('anOrg3')
    if testOrg3:
        client.deleteOrganization(testOrg3)
    
    testOrg3 = client.createOrganization('anOrg3', 'this is anOrg3')
    COProject3 = client.createProject('CO3',testOrg3.key)
    COProject3.uploadCSVApplyBackupRunMining('IPMClient/data/Client Onboarding.zip', 'IPMClient/data/Client Onboarding.idp')

    newaccountdata = {
        "firstName": "John",
        "lastName": "Sam",
        "country": "FR",
        "email": "john.sam@ibm.com",
        "agentEnabled": True,
        "technicalUser": False,
        "active": True,
        "password": "John12345!",
        "username": "john.sam"
    }
    account = client.createAccount(newaccountdata)
    testOrg2.addAccount(account)
    testOrg3.addAccount(account)
    #testOrg2.removeAccount(account)
    client.deleteAccount(account)


    print('done')


if __name__ == "__main__":
    main(sys.argv)