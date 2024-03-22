# IBM Process Mining Python Client Library

This Python library greatly facilitates the use of IBM Process Mining REST API to retrieve data and to perform actions.

## IPMClient
IPMClient is the principal class that communicates with IBM Process Mining through REST APIs.

client = Client(url, userid, apikey)
client.getToken() called in the constructor. Could be renewed on demand

### Tenants - manage IPMTenant objects
tenants = client.retrieveTenants() # retrieves the list of tenants by REST API

tenants = client.getTenants() # returns the list of tenants, or all client.retrieveTenants() if empty

tenant = client.getTenantByName(name) # returns a tenant object IPMTenant
tenant = client.getTenantByKey(key) # returns a tenant object IPMTenant
tenant = client.getCurrentTenant() # returns a tenant object IPMTenant. By default id=-1
tenant = client.setCurrentTenant(tenant) # all tenant operations are through this one

### Accounts -- manage IPMAccount objects
accounts = client.retrieveAccounts(tenant=None) # retrieves the list of accounts of tenant or of the current tenant via the REST API
accounts = client.getAccounts(tenant=None) # return the list of accounts or retrieves it if empty
account = client.getAccountBysUserName(username, tenant=None) 
account = client.createAccount(accountData, tenant=None) # create an account (JSON) in the tenant or currentTenant
account = client.deleteAccount(account, tenant=None)

### Organizations -- manage IPMOrganization objects
organizations = client.retrieveOrganizations()
organizations = client.getOrganizations()
organization = client.getLocalOrganization()
organization = client.createOrganization(name, description)
organization = client.deleteOrganization(organization)
organization = client.getOrganizationByName(name)
organization = client.getOrganizationByKey(key)

### Projects -- manage IPMProject objets
projects = client.retrieveProjects()
projects = client.getProjects()
project = client.getProjectByName(name)
project = client.getProjectByKey(key)
project = client.createProject(organization, name)
project = client.deleteProject(project)

## IPMTenant Class

IPMTenant instances are create by client.retrieveTenants(), that is called during the instantiation of IPMClient instance

accounts = tenant.getAccounts() # call client.retrieveAccounts() if empty
account = tenant.getAccountByUserName(username)

## IPMOrganization Class

IPMOrganization instances are created by client.retrieveOrganizations() or by client.createOrganization()

accounts = organization.retrieveAccounts()
accounts = organization.getAccounts()
account = organization.addAccount(account)
accounts = organization.removeAccount(account)
account = organization.getAccountByUserName(username)

projects = organization.getProjects()
project = organization.getProjectByName(name)

## IPMProject Class

IPMProject instances are created by client.createProject(name) or by client.retrieveProjects()

project.uploadCSVApplyBackupRunMining(csvfile, idpfile)

project.uploadCSV(csvfilename)
project.uploadApplyBackup(idpfilename)
project.uploadBackup(ipdfilename)
project.applyBackup(backupId) 
project.retrieveBackupList()
project.getBackupList()
project.runMining()

project.retrieveMetaInfo()
project.retrieveInformation()
project.getInfo()
project.getPerformance()
project.getNavigation()
project.retrieveWorkflow()
project.retrieveBPMN()

project.dashboards = project.retrieveDashboards()
project.getDashboards()
dashboard = project.getDashboardByName()

## IPMDashboard Class

IPMDashboard instances are created by project.retrieveDashboards()

dashboard.widgets = dashboard.retrieveWidgets()
dashboard.getWidgets()
widget = dashboard.getWidgetByName(name)

## IPMWidget Class
IPMWidget instances are created by dashboard.retrieveWidgets()

widget.values = widget.retrieveValues()
widget.getValues() -> widget.values
widget.dataframe = widget.toDataFrame() # create a dataframe from the values
widget.toCSV(csvfilename, replace=True) # add timestamp to filename if replace==False

## IPMAccount Class
IPMAccount instances are created by client.createAccount() and by client.retrieveAccounts() # using the currentTenant (the default one by default)

account.patch(json)







