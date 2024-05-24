import IPMBase as ipmb
import IPMProject as ipmp
import IPMOrganization as ipmo
import IPMTenant as ipmt
import IPMAccount as ipma
import json

class Client(ipmb.Base):
    def __init__(self, url, userid, apikey):
        ipmb.Base.__init__(self)
        self.url = url
        self.user_id = userid
        self.api_key = apikey
        self.getToken()
        self.tenants = None
        self.currentTenant = None
        self.projects = []
        self.organizations = []

    def getToken(self):
        if self.sendPostRequest(url=f"{self.url}/integration/sign",
                                verify=self.verify,
                                headers={"content-type": "application/json"},
                                params={},
                                data=json.dumps({ 'uid' : self.user_id, 'apiKey' : self.api_key}),
                                functionName='get token',
                                files=None):
            self.token = self.getResponseData()
        else:
            self.token = None

    # TENANT MANAGEMENT

    def retrieveTenants(self):
        if self.sendGetRequest(url=f"{self.url}/user-management/integration/tenants",
                                verify=self.verify,
                                headers=self.getHeaders(),
                                params={},
                                functionName='retrieve tenants'):
            jsontenants = self.getResponseData()
            self.tenants = []
            for jsontenant in jsontenants:
                self.tenants.append(ipmt.Tenant(self, jsontenant))
            return self.tenants   

    def getTenants(self):
        if self.tenants: return self.tenants
        return self.retrieveTenants()
    
    def getTenantByName(self, name):
        tenants = self.getTenants()
        for tenant in tenants:
            if tenant.name == name: return tenant
        self._setResponseKO()

    def getTenantByKey(self, key):
        tenants = self.getTenants()
        for tenant in tenants:
            if tenant.key == key: return tenant     
        self._setResponseKO()

    def setCurrentTenant(self, tenant):
        self.currentTenant = tenant

    def getCurrentTenant(self): 
        if self.currentTenant is None:
            self.tenants = self.retrieveTenants()
            self.currentTenant = self.getTenantByKey('-1')
        return self.currentTenant

    # ACCOUNT MANAGEMENT
    def retrieveAccounts(self, tenant=None)->list:
        if tenant==None:
            tenant = self.getCurrentTenant()
        
        if self.sendGetRequest(url=f"{self.url}/user-management/integration/tenants/{tenant.key}/accounts",
                    verify=self.verify,
                    headers=self.getHeaders(),
                    params={},
                    functionName='retrieve accounts'):
            # returned data does not include information about the organizations to which the account belongs
            jsonaccounts = self.getResponseData()
            tenant.accounts = []
            for item in jsonaccounts:
                account = ipma.Account(self, item)
                tenant.accounts.append(account)
            return tenant.accounts

    def getAccounts(self, tenant=None):
        if tenant==None:
            tenant = self.getCurrentTenant()
        return tenant.getAccounts()
    
    def getAccountByUserName(self, username, tenant=None):
        if tenant==None:
            tenant = self.getCurrentTenant()
        return tenant.getAccountByUserName(username)         
    
    
    def createAccount(self, accountData, tenant=None):
        dataExample = {
            "firstName": "John",
            "lastName": "Sam",
            "country": "IN",
            "email": "john.sam@ibm.com",
            "agentEnabled": True,
            "technicalUser": False,
            "active": True,
            "password": "string",
            "username": "john.sam"
        }
        if tenant==None:
            tenant = self.getCurrentTenant()
        existingAccount = tenant.getAccountByUserName(accountData['username'])
        if existingAccount :
            print(f'--Process Minin: WARNING: create account: {existingAccount.username} already exists, use client.getAccountByUserName()')
            self._setResponseOK(existingAccount.key)
            return existingAccount
        
        # Create the account using the REST API
        if self.sendPostRequest(
                url=f'{self.url}/user-management/integration/tenants/{tenant.key}/accounts', 
                verify=self.verify,
                headers=self.getHeaders(), 
                params={},
                data=json.dumps(accountData),
                functionName='create account'):

                account = ipma.Account(self, self.getResponseData())
                tenant.accounts.append(account)
                return account
        else: return
    
    def deleteAccount(self, account, tenant=None):
        if tenant==None:
            tenant = self.getCurrentTenant()
        if self.sendDeleteRequest(
            url=f'{self.url}/user-management/integration/tenants/{tenant.key}/accounts/{account.key}', 
            verify=self.verify,
            headers=self.getHeaders(), 
            params={},
            functionName='delete account'):

            account.data = self.getResponseData()
            # Remove account from tenant list
            tenant._removeAccount(account)
            # Remove account from each organization
            organizations = self.getOrganizations()
            for organization in organizations:
                if organization.accounts:
                    for index, item in enumerate(organization.accounts):
                        organization.accounts.pop(index)
            return account
        else:
            return False   
        
    # GROUPS
        
    def retrieveGroups(self):
        url = f'{self.url}/user-management/integration/groups'
        return self.sendGetRequest(
            url=url, verify=self.verify, params={}, headers=self.getHeaders(), functionName='retrieve groups')
    
    def getGroupByName(self, groups, groupName):
        for group in groups:
            if group['groupName'] == groupName:
                return group
            
    def addAccountToGroup(self, account, groupId):
        url = f'{self.url}/user-management/integration/groups/{groupId}/accounts'
        data = json.dumps({'username': account.username})
        return self.sendPostRequest(
            url=url, verify=self.verify, params={}, headers=self.getHeaders(), data=data, functionName='add account to group')        

 
    # ORGANIZATION MANAGEMENT
    
    def getOrganizations(self):
        if self.organizations: return self.organizations
        return self.retrieveOrganizations()

    def retrieveOrganizations(self)->list:
        # Organizations are only used to add/remove accounts
        # Local organizations are not always returned. But we don't need them as we don't need to add accounts to private orgs
        self.organizations = []
        if self.sendGetRequest(url=f"{self.url}/user-management/integration/organizations",
                        verify=self.verify,
                        headers=self.getHeaders(),
                        params={},
                        functionName='retrieve organizations'):
            organizations = self.getResponseData()
            for org_data in organizations:
                organization = ipmo.Organization(self, org_data)
                self.organizations.append(organization)
        return self.organizations 
        
    def createOrganization(self, name, description):
        existingOrg = self.getOrganizationByName(name)
        if existingOrg:
            print(f"--Process Mining: WARNING organization {name} exists already, use client.getOrganizationByName()")
            self._setResponseOK(existingOrg.key)
            return existingOrg
        
        if self.sendPostRequest(
                url=f'{self.url}/user-management/integration/organizations', 
                verify=self.verify,
                headers=self.getHeaders(), 
                params={},
                data=json.dumps({ "name": name, "description": description}),
                functionName='create organization'):
                organization = ipmo.Organization(self, self.getResponseData())
                # add to the client if direct creation (instead as from the client)
                
                self.organizations.append(organization)
                return organization
        
    def deleteOrganization(self, organization):
        if self.sendDeleteRequest(
            url=f'{self.url}/user-management/integration/organizations/{organization.key}',
            verify=self.verify,
            headers=self.getHeaders(),
            params={'org' : organization.key},
            functionName='delete organization'
        ):
            self._removeOrganization(organization)
            return organization
        return 

    def getOrganizationByKey(self, key):
        organizations = self.getOrganizations()
        for org in organizations:
            if org.key == key:
                return org
        self._setResponseKO()

            
    def getOrganizationByName(self, name):
        organizations = self.getOrganizations()
        for org in organizations:
            if org.name == name:
                return org
        self._setResponseKO()
   
    def _removeOrganization(self, organization:ipmo.Organization):
        for index, item in enumerate(self.organizations):
            if item.key == organization.key:
                self.organizations.pop(index)
                return organization
        

# PROJECT MANAGEMENT
    
    def retrieveProjects(self):
        self.projects = []
        if self.sendGetRequest(url=f"{self.url}/integration/processes",
                        verify=self.verify,
                        headers=self.getHeaders(),
                        params={},
                        functionName='retrieve projects'):
                        
            projects = self.getResponseData()

            for project_data in projects:        
                project = ipmp.Project(self, project_data['projectTitle'], project_data['projectName'], project_data['organization'], project_data)
                self.projects.append(project)
        return self.projects
    
    
    def retrieveLastAccessedProcesses(self):
        if self.sendGetRequest(url=f"{self.url}/integration/access/processes",
                        verify=self.verify,
                        headers=self.getHeaders(),
                        params={},
                        functionName='retrieve last accessed projects'):
            self.lastAccessedProjects = []
        
    def createProject(self, name, orgkey=''): #orgkey='' for local org
        existingProject = self.getProjectByName(name)
        if existingProject:
            print(f"--Process Mining: WARNING project {name} exists already")
            self._setResponseOK(existingProject.key)
            # status_code = -1 used to test that the project was returned without calling the API
            return existingProject

            # create the project in IPM
        if self.sendPostRequest(
            f'{self.url}/integration/processes',
            verify=self.verify,
            params={'org' : orgkey},
            headers=self.getHeaders(),
            data=json.dumps({ 'title' : name, 'org' : orgkey}),
            files=None,
            functionName='create project'):

            key = self.getResponseData()
            project = ipmp.Project(self, name, key, orgkey)
            self.projects.append(project)
            return project
    
    def deleteProject(self, project):

        if self.sendDeleteRequest(
            url=f"{self.url}/integration/processes/{project.key}",
            verify=self.verify,
            params={'org' : project.orgkey},
            headers=self.getHeaders(),
            functionName='delete project'):

            # remove from client project list
            self._removeProject(project)
        return project

    def getProjects(self):
        if self.projects: return self.projects
        return self.retrieveProjects()
    
    def getProjectByKey(self, key):
        projects = self.getProjects()
        for project in projects:
            if project.key == key:
                return project
        self._setResponseKO()


    def getProjectByName(self, name):
        projects = self.getProjects()
        for project in projects:
            if project.name == name:
                return project
        self._setResponseKO()
        
    def _removeProject(self, project):
        projects = self.getProjects()
        for index, item in enumerate(projects):
            if item == project:
                projects.pop(index)
                return project
            
    