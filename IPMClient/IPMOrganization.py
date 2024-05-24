import IPMBase as ipmb
import IPMClient as ipmc
import IPMProject as ipmp
import json

# Organizations require Admin permissions. Owners are not enough
# The purpose of Organization is to manage accounts of the organization
# As a facility we store the processes that are connected with the organization
class Organization(ipmb.Base):
    def init__BAK(self, client, jsondata):
        ipmb.Base.__init__(self)
        self.client = client
        self.accounts = []
        self.projects = []
        self.name = jsondata['name']
        self.key = jsondata['key']
        self.realKey = jsondata['realKey']
        self.description = jsondata['description']
        self.owner = jsondata['owner']
        self.status = True
        self.jsondata = jsondata

    def __init__(self, client, jsondata):
        ipmb.Base.__init__(self)
        self.client = client
        self.name = jsondata['name']
        self.key = jsondata['key']
        self.description = jsondata['description']
        self.owner = jsondata['owner']
        self.accounts = []
        self._setProjects()
        self.jsondata = jsondata        
    
    def getHeaders(self):
        return self.client.getHeaders()
    
    def getclient(self)->ipmc:
        return self.client
    
    def getURL(self):
        return self.client.url

        
    def patch(self, name, description):
        self.name = name
        self.description = description
        if self.sendPatchRequest(
            url=f'{self.getURL()}/user-management/integration/organizations{self.key}', 
            verify=self.verify,
            headers=self.getHeaders(), 
            params={},
            data=json.dumps({ "name": name, "description": description}),
            functionName='patch organization'):
          
            self.jsondata = self.getResponseData()
            return self

    # MANAGE ACCOUNTS

    def retrieveAccounts_BAK(self):
        if self.key == 0: # API can't be called with key == 0 BUT THERE A NO OTHER USERS FOR A PRIVATE ORG!!!
            key = self.realKey
        else:
            key = self.key
        self.accounts = []
        if self.sendGetRequest(
            url=f'{self.getURL()}/user-management/integration/organizations/{key}/accounts',
            verify=self.verify,
            headers=self.getHeaders(), 
            params={},
            functionName='retrieve accounts'):

            jsonaccounts = self.getResponseData()
            tenant = self.client.getCurrentTenant()
            tenantAccounts = tenant.getAccounts()
            for item in jsonaccounts:
                # get the accounts from the Tenant
                for account in tenantAccounts:
                    if account.key == item['id']:
                        self.accounts.append(account)
        return self.accounts
        
    def retrieveAccounts(self):
        self.accounts = []
        if self.sendGetRequest(
            url=f'{self.getURL()}/user-management/integration/organizations/{self.key}/accounts',
            verify=self.verify,
            headers=self.getHeaders(), 
            params={},
            functionName='retrieve accounts'):

            jsonaccounts = self.getResponseData()
            tenant = self.client.getCurrentTenant()
            tenantAccounts = tenant.getAccounts()
            for item in jsonaccounts:
                # get the accounts from the Tenant
                for account in tenantAccounts:
                    if account.key == item['id']:
                        self.accounts.append(account)
        return self.accounts

    def getAccounts(self):
        if self.accounts: return self.accounts
        return self.retrieveAccounts()
    
    def getAccountByUserName(self, username):
        accounts = self.getAccounts()
        for account in accounts:
            if account.username == username:
                return account
        self._setResponseKO()

            
    def addAccount(self, account):
        if self.getAccountByUserName(account.username):
            print(f'--Process Mining: ERROR : Account {account.username} already in organization {self.name}, use organization.getAccountByUserName()')
            return False
        if self.sendPostRequest(
            url=f'{self.getURL()}/user-management/integration/organizations/{self.key}/accounts/{account.key}',
            verify=self.verify,
            headers=self.getHeaders(),
            params=None,
            data=None,
            files=None,
            functionName='add account to organization'):

            self.accounts.append(account)
            return account
    
    def removeAccount(self, account):
        existingAccount = self.getAccountByUserName(account.username)
        if existingAccount == None:
            print(f'--Process Mining: ERROR : Account {account.username} not in organization {self.name}, use organization.getAccountByUserName()')
            return False
        if self.sendDeleteRequest(
            url=f'{self.getURL()}/user-management/integration/organizations/{self.key}/accounts/{account.key}',
            verify=self.verify,
            headers=self.getHeaders(),
            params=None,
            functionName='remove account from organization'):    

            self._removeFromAccounts(account)
            return account

    def _removeFromAccounts(self, account):
        accounts = self.getAccounts()
        for index, item in enumerate(accounts):
            if item.key == account.key:
                accounts.pop(index)
                return account
            
    # MANAGE PROJECTS

    def getProjects(self):
        return self.projects
    
    def getProjectByName(self, name):
        projects = self.getProjects()
        for project in projects:
            if project.name == name:
                return project
        self._setResponseKO()

    
    def _setProjects(self):
        if not self.client.projects:
            self.client.retrieveProjects()
        self.projects = []
        for project in self.client.projects:
            if project.orgkey == self.key:
                self.projects.append(project)
    
    def _removeProject(self, project):
        projects = self.getProjects()
        for index, item in enumerate(projects):
            if item == project:
                projects.pop(index)
                return project