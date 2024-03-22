import IPMBase as ipmb
import IPMClient as ipmc
import IPMProject as ipmp
import json

class Organization(ipmb.Base):
    def __init__(self, client, data):
        ipmb.Base.__init__(self)
        self.client = client
        self.accounts = []
        self.projects = []
        self.name = data['name']
        self.key = data['key']
        self.realKey = data['realKey']
        self.description = data['description']
        self.owner = data['owner']
        self.status = True
        self.data = data
        
    
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
          
            self.data = self.getResponseData()
            return self

    # MANAGE ACCOUNTS

    def retrieveAccounts(self):
        if self.key == 0: # API can't be called with key == 0 
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

    
    def _setProjects(self, projects):
        self.projects = []
        for project in projects:
            if project.organization == self:
                self.projects.append(project)
    
    def _removeProject(self, project):
        projects = self.getProjects()
        for index, item in enumerate(projects):
            if item == project:
                projects.pop(index)
                return project