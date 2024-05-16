# IBM Process Mining Python Client Library

This Python class library greatly facilitates the use of IBM Process Mining REST API to retrieve data and to perform actions.

`IPMClient` is the principal class that communicates with IBM Process Mining through REST APIs.

An IPMClient object stores information that was retrieved from IBM Process Mining. This reduced the amount of REST API requests.

## Integrating IBM Process Mining with Cognos Analytics and S3

[CognosAnalyticsClient.py](./CognosAnalyticsClient.py) is a utility library to ease the connection to Cognos Analytics and to upload files.
[IPM_CognosAnalytics.ipynb](./IPM_CognosAnalytics.ipynb.py) is a jupyter notebook that is using both IPMClient and CognosAnalyticsClient to upload Process Mining data to Cognos Analytics

[COS.ipynb](COS.ipynb) is a jupyter notebook that shows how to upload data to S3


## Getting and retrieving objects
Method names starting with retrieve (ex client.retrieveProjects) explicitly call the REST API. They are used initially, or to refresh some data.
Method names starting with get (ex client.getProjects) return the local client.projects list. If this list is empy, the function call its retrieve equivalent (ex client.retrieveProjects()).

The objects are typically returned by their name or their key. For example myProject = client.getProjectByName('My Project'). The client takes care of searching in local lists or calling the REST API to retrieve the list of projects.

Since the client first search in its local lists, it might happen that the list is not up to date with the data on the IBM Process Mining server. This should not really happen, but to avoid this, you could first call the retrieve method to refresh the local data. For example, you could call client.retrieveProjects(), and then call client.getProjectByName('My Project'). But it is unlikely that changes occur while you are executing your python program, unless it is a long-lasting program.

## Creating and deleting artifacts in IBM Process Mining
The IPMClient object is also responsible for creating and deleting artifacts in IBM Process Mining: 

Example:
```
import IPMClient as ipm
client = ipm.IPMClient('https://processmining.com', 'john.smith', '12345RTY')
organization = client.getOrganizationByName('myFinance')
client.createProject(organization, 'new project')
```


Therefore you never need to create an instance of the classes, except for IPMClient. The instances are automatically created from the client when you retrieve the objects, or when you create a new artifact from the client.

## Managing objects and retrieving detailed data
The objects of the classes can be queried to obtain information, or to modify some relationships. Some methods query or modify aritifacts in IBM Process Mining. For example organization.getAccounts() query the accounts in an organization. organization.addAccount(account) add an account to an organization, and organization.removeAccount(account) removes the account from the organization.

We limit the instance fields to those that are essential to retrieve and manipulate the artifacts. Often the data returned from the IBM Process Mining information contains detailed information returned as JSON. Each object stores this additional information that can be used as needed.

For example, `project.getJSONdata()` returns a JSON dict that contains all the details retrieved from existing projects. You can refer to the IBM Process Mining REST API documentation for details.

If you created an artifact, the data returned by the creation might not be as complete as the data returned from already existing objects. For example, the data returned by `client.createProject(organization, 'My Project')` is the project key 'my-project'. On the other hand, the data returned from existing projects include information like owner, last used, and other statistics. When you call `project.runMining()`, the project's detailed data is retrieved.

## Managing request status and data
The IBMClient class library homogeneizes the IBM Process Mining REST API calls, their status code and returned data. If needed you can access the request returned information.

```
instance.getResponseStatusCode()
instance.getResponseData()
instance.isResponseOK()
instance.isResponseKO()
```


## IPMClient
This is the only constructor that you need to call in your python program.

```
import IPMClient as ipm
client = ipm.Client(url, userid, apikey)
```

`client.getToken()` is called in the constructor. It could ne renewed on demand as the token expires.

### Manage IPMTenant objects
You can ignore the tenant. By default, the client is using the default client named '-1'
If you need to explicitly manage a client, get the Tenants, and call `client.setCurrentTenant(tenant)`.

```
tenants = client.retrieveTenants() # retrieves the list of tenants by REST API
tenants = client.getTenants() # returns the list of tenants, or all client.retrieveTenants() if empty
tenant = client.getTenantByName(name) # returns a tenant object IPMTenant
tenant = client.getTenantByKey(key) # returns a tenant object IPMTenant
tenant = client.getCurrentTenant() # returns a tenant object IPMTenant. By default id=-1
tenant = client.setCurrentTenant(tenant) # all tenant operations are through this one
```

### Manage IPMAccount objects
```
accounts = client.retrieveAccounts(tenant=None) # retrieves the list of accounts of tenant or of the current tenant via the REST API
accounts = client.getAccounts(tenant=None) # return the list of accounts or retrieves it if empty
account = client.getAccountBysUserName(username, tenant=None) 
account = client.createAccount(accountData, tenant=None) # create an account (JSON) in the tenant or currentTenant
account = client.deleteAccount(account, tenant=None)
```
### Organizations -- manage IPMOrganization objects
```
organizations = client.retrieveOrganizations() # Calls the REST API to refresh the organization list
organizations = client.getOrganizations() # returns the organization list, or call retrieveOrganization() if empty
organization = client.getLocalOrganization()
organization = client.getOrganizationByName(name) # find by name in the local list or retrieve the list if empty
organization = client.getOrganizationByKey(key)  # find by key in the local list or retrieve the list if empty
organization = client.createOrganization(name, description)
organization = client.deleteOrganization(organization)
```

### Projects -- manage IPMProject objets
```
projects = client.retrieveProjects() # Call the REST API to refresh to project list
projects = client.getProjects() # return the local list or call retrieveProjects() if empty
project = client.getProjectByName(name) # find by name in the local list or retrieve the list if empty
project = client.getProjectByKey(key) # find by key in the local list or retrieve the list if empty
project = client.createProject(organization, name)
project = client.deleteProject(project)
```

The following classes handle artefacts retrieved from IBM Process Mining, or artefacts created in IBM Process Mining by the client.

## IPMTenant Class
Operations on Accounts can be done through the client. Using the Tenant class is optional.

IPMTenant instances are create by client.retrieveTenants(), that is called during the instantiation of IPMClient instance
```
accounts = tenant.getAccounts() # call client.retrieveAccounts() if empty
account = tenant.getAccountByUserName(username)
```

## IPMOrganization Class

IPMOrganization instances are created by client.retrieveOrganizations() or by client.createOrganization()
```
accounts = organization.retrieveAccounts()
accounts = organization.getAccounts()
account = organization.addAccount(account)
accounts = organization.removeAccount(account)
account = organization.getAccountByUserName(username)

projects = organization.getProjects()
project = organization.getProjectByName(name)
```

## IPMProject Class

IPMProject instances are created by client.createProject(name) or by client.retrieveProjects()

Methods for managing the project model
```
project.uploadCSVApplyBackupRunMining(csvfile, idpfile)

project.uploadCSV(csvfilename)

project.uploadApplyBackup(idpfilename)
project.uploadBackup(ipdfilename)
project.applyBackup(backupId) 
project.retrieveBackupList()
project.deleteBackup(backupId)
 
project.uploadReferenceModel(bpmnfilename)

project.runMining()
```


The following methods retrieve project status, statistics, variants, filters, ... as JSON objects.
Examples of JSON returned by these methods are available in the directory [json_result_examples](./json_result_examples).

```
filters = project.retrieveFilters()
templates = project.retrieveTemplates()
settings = project.retrieveKPISettings()
settings = project.retrieveSettings(fromMaster=False) # if using a snapshot, can be retrieved from parent
activityCosts = project.retrieveSettingsActivityCost(fromMaster=False) # if using a snapshot, can be retrieved from parent
activityWorkingTime = project.retrieveSettingsActivityWorkingTime(fromMaster=False) # if using a snapshot, can be retrieved from parent
status = project.retrieveStatus()
information = project.retrieveMetaInfo()
information = project.retrieveInformation()
```

This method is useful to save a JSON object into a filename
```
project.dumpJsonToFile(result, filename) 
```

Methods returning process deviations and variants
```
deviations = project.retrieveDeviations(filters=None) # transient filters can be applied
variants = project.retrieveVariants() # top 30 variants
kpiStatus = project.retrieveKpiStatus(filters=None) # transient filters can be applied
```

Methods returning statistical data
```
modelStats = project.retrieveModelStatistics(filters=None)
```
The following methods facilitate the parsing of ModelStatistics JSON. You need first to call
```project.retrieveModelStatistics()```.
```
allActivityStats = project.getActivityStatistics(modelStats) 
BOStats = project.getActivityStatistics(modelStats,'BO Service Closure')
AllTransitionStats = project.getTransitionStatistics(modelStats)
startRequestCreatedStats = project.getTransitionStatistics(modelStats, 'START', 'Request created')
processStats = project.getProcessStatistics(modelStats)
customMetrics = project.retrieveCustomMetrics()
```

Methods related to dashboards
```
project.dashboards = project.retrieveDashboards()
project.getDashboards()
dashboard = project.getDashboardByName()
```

## IPMDashboard Class

IPMDashboard instances are created by project.retrieveDashboards()

```
dashboard.widgets = dashboard.retrieveWidgets()
dashboard.getWidgets()
widget = dashboard.getWidgetByName(name)
```

## IPMWidget Class
IPMWidget instances are created by dashboard.retrieveWidgets()

```
widget.values = widget.retrieveValues()
widget.getValues() -> widget.values
widget.dataframe = widget.toDataFrame() # create a dataframe from the values
widget.toCSV(csvfilename, replace=True) # add timestamp to filename if replace==False
```

## IPMAccount Class
IPMAccount instances are created by client.createAccount() and by client.retrieveAccounts() # using the currentTenant (the default one by default)

```
account.patch(json)
```
