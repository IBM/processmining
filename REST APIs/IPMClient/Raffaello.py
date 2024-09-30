import IPMClient as ipm
import json
import sys
import os

def main(argv):

    getConfigFrom = 'FILE'
    configFileName = './IPMConfig_Raffaello.json'

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
    newAcountJSON = {
            "firstName": "prenom",
            "lastName": "nom",
            "country": "FR",
            "email": "prenom.nom@ibm.com",
            "agentEnabled": True,
            "technicalUser": False, # user can't log into the UI if True. Only for REST API
            "active": True,
            "password": "Prenom12345!",
            "username": "prenom.nom@ibm.com"
    }
    organization = client.getOrganizationByName('Demo Kit - myInvenio')
    tenants = client.getTenants()
    client.setCurrentTenant(tenants[0])
    newAccount = client.createAccount(newAcountJSON)
    organization.addAccount(newAccount)

    print('done')


if __name__ == "__main__":
    main(sys.argv)