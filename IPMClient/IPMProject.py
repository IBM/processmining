import IPMBase as ipmb
import IPMDashboard as ipmd
import sys
import time
import json
import base64

import requests, json, urllib3
requests.packages.urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SPINNING_RATE = 0.1

def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor

class Project(ipmb.Base):
    def __init__(self, client, name, key, orgkey, jsondata=None):
        ipmb.Base.__init__(self)
        self.client = client
        if orgkey == 'User Private' or orgkey == 'local organization':
            orgkey = ''
        self.orgkey = orgkey
        self.key = key
        self.name = name
        self.dashboards = []
        self.data = jsondata

        if jsondata: # project retrieved from retrieveProjects
            self.data = jsondata
            return
        # else project created by the client

    def getHeaders(self):
        return self.client.getHeaders()
    
    def getURL(self):
        return self.client.url

    def uploadCSV(self, csv_filename, datasetOverride=False):

        url=f'{self.getURL()}/integration/csv/{self.key}/upload'
        params={'org' : self.orgkey, 'dataSetOverride' : datasetOverride}
        headers={"Authorization": f"Bearer {self.client.token}"}
        files={'file': (csv_filename, open(csv_filename, 'rb'),'text/zip')}
        if self.sendPostRequest(url=url,params=params,headers=headers,files=files,functionName='upload csv'):
        # Async call --- the caller need to loop on get job status that it is completed
            job_key = self.getResponseData() # that's the job key
        else:
            return False
        # Wait until job key is complete
        runningCall = 1
        print("Process Mining: loading event log (please wait)")
        spinner = spinning_cursor()
        while  runningCall :
            job_status = self.retrieveCSVJobStatus(job_key)
            if job_status == 'complete': 
                runningCall = 0
            if job_status == 'error': 
                runningCall = 0
                print("Error while loading CSV -- column number mismatch")

            sys.stdout.write(next(spinner))
            sys.stdout.flush()
            sys.stdout.write('\b')
            time.sleep(SPINNING_RATE)
        return self
        
    def retrieveCSVJobStatus(self, job_key):
        if self.sendGetRequest(
            f'{self.getURL()}/integration/csv/job-status/{job_key}',
            verify=self.verify,
            params={},   
            headers=self.getHeaders(),
            functionName='get CSV job status'):

            return self.getResponseData()

    def retrieveModelStatisticsJobStatus(self, job_key):
        if self.sendGetRequest(
            f'{self.getURL()}/integration/jobs/model-statistics/{job_key}',
            verify=self.verify,
            params={},   
            headers=self.getHeaders(),
            functionName='get model-statistics job status'):

            return self.getResponseData()      
    
        
    def retrieveBPMN(self, withGateways=True):
        if self.sendGetRequest(
            f'{self.getURL()}/integration/export/{self.key}/BPMN',
            verify=self.verify,
            params={'org' : self.orgkey, 'withGateways':withGateways},   
            headers=self.getHeaders(),
            functionName='get bpmn'):

            encodedbpmn = self.getResponseData()
            return base64.b64decode(encodedbpmn).decode('utf-8')
        
    def retrieveSVG(self, applyKPI=False, viewType=0):
        ''' Use one of these numbers
        0 - Frequency view
        1 - Performance view (Avg)
        2 - Performance view (Max)
        3 - Performance view (Min)
        4 - Performance view (Median)
        5 - Rework view
        6 - Performance view (Weighted)
        7 - Cost view
        8 - Overall cost view
        '''
        if self.sendGetRequest(
            f'{self.getURL()}/integration/csv/{self.key}/workflow',
            verify=self.verify,
            params={'org' : self.orgkey, 'applyKPI' : applyKPI, 'viewType' : viewType},   
            headers=self.getHeaders(),
            functionName='get svg'):

            encodedbpmn = self.getResponseData()
            return base64.b64decode(encodedbpmn).decode('utf-8')
          
    def uploadBackup(self, backupfilename):

        if self.sendPostRequest(
            url=f'{self.getURL()}/integration/processes/{self.key}/upload-backup',
            verify=self.verify,
            params={'org' : self.orgkey},      
            headers={"Authorization": "Bearer %s" % self.client.token},
            files={'file': (backupfilename, open(backupfilename, 'rb'),'text/zip')},
            functionName='upload backup'):

            return self.getResponseData()
    
    def retrieveBackupList(self):
        if self.sendGetRequest(
            url=f'{self.getURL()}/integration/processes/{self.key}/backups',
            verify=self.verify,
            params={'org' : self.orgkey},      
            headers=self.getHeaders(),
            functionName='retrieve backup list'):
            return self.getResponseData()['backups']
    
    def deleteBackup(self, backupId):
        if self.sendDeleteRequest(
            url=f'{self.getURL()}/integration/processes/{self.key}/backups/{backupId}',
            verify=self.verify,
            headers=self.getHeaders(),
            params={'org' : self.orgkey},
            functionName='delete backup'
        ):
            return self.isResponseKO()

    def applyBackup(self, backupId):
        if self.sendPutRequest(
            url=f'{self.getURL()}/integration/processes/{self.key}/backups/{backupId}',
            verify=self.verify,
            headers=self.getHeaders(),
            params={'org' : self.orgkey},
            functionName='apply backup'
        ):
            return self.isResponseOK()
    
    def uploadApplyBackup(self, idpfile):
        backup = self.uploadBackup(idpfile)
        if self.isResponseOK():
            self.applyBackup(backup['id'])

    def uploadCSVApplyBackupRunMining(self, csvfilename, ipdfilename):
        self.uploadCSV(csvfilename)
        self.uploadApplyBackup(ipdfilename)
        self.runMining()
        
    def runMining(self):
        if self.sendPostRequest(
            url=f'{self.getURL()}/integration/csv/{self.key}/create-log',
            params={'org' : self.orgkey},
            headers=self.getHeaders(),
            data=None,
            files=None,
            functionName='process mining'):
            # Async call
            job_key = self.getResponseData()
        else:
            return False
        # wait until async call is completed
        runningCall = 1
        print("Process Mining: refreshing model (please wait)")
        spinner = spinning_cursor()
        while  runningCall :
            job_status = self.retrieveCSVJobStatus(job_key)
            if (job_status == 'complete') :
                runningCall = 0
            if (job_status == 'error') :
                runningCall = 0
                print("Error while creating the log")
                return 0
            sys.stdout.write(next(spinner))
            sys.stdout.flush()
            sys.stdout.write('\b')
            time.sleep(SPINNING_RATE)
        
        # Retrieve the information from the project
        self.retrieveInformation()
    
    def retrieveInformation(self):
        if self.sendGetRequest(
            url=f"{self.getURL()}/integration/processes/{self.key}",
            verify=self.verify,
            params={'org' : self.orgkey},
            headers=self.getHeaders(),
            functionName='retrieve project info'):

            self.info = self.getResponseData()['info']
            self.navigation = self.getResponseData()['navigation']
            self.performance = self.getResponseData()['performance']
            return self.getResponseData()
        return None
    
    def getDashboards(self):
        if (self.dashboards): return self.dashboards
        return self.retrieveDashboards()

    def retrieveDashboards(self):
        if self.sendGetRequest(
            url=f"{self.getURL()}/analytics/integration/dashboard/{self.key}/list",
            verify=self.verify,
            params={'org' : self.orgkey},
            headers=self.getHeaders(),
            functionName='retrieve dashboards'):

            dashboards = self.getResponseData()['dashboards']
            self.dashboards = []
            for dashboard in dashboards:
                self.dashboards.append(ipmd.Dashboard(self, dashboard))
            return self.dashboards
        
    def retrieveFromSQL(self, query):
        exampleData =  {
            "templateId": "62bde8bd2895512725a62ca5",
            "query": "SELECT CASEID FROM EVENTLOG GROUP BY CASEID",
            "targetDate": "2023-12-01T00:00:00.000Z",
            "activitiesConformance": "ONLY_CONFORMANT",
            "keepLast": True
            }
        data = "params={'query': '%s'}" % query
        headers = self.getHeaders()
        headers['content-type'] = 'application/x-www-form-urlencoded'
        if self.sendPostRequest(
            url=f"{self.getURL()}/analytics/integration/{self.key}/query",
            verify=self.verify,
            params={'org' : self.orgkey},
            headers=headers,
            data=data,
            files=None,
            functionName='retrieve from SQL'
        ):
            return self.getResponseData()

    def getDashboardByName(self, name):
        dashboards = self.getDashboards()
        for dashboard in dashboards:
            if dashboard.name == name:
                return dashboard
        print("ERROR: unkwown dashboard %s" % name)
        self._setResponseKO()
        return None
  
        
    def uploadReferenceModel(self, bpmnfilename):
        headers = self.getHeaders()
        url=f'{self.getURL()}/integration/csv/{self.key}/upload-model'
        files={'file': (bpmnfilename, open(bpmnfilename, 'rb'),'text/zip')},
        if self.sendPostRequest(url=url, verify=self.verify, params=self.getParams(), headers=headers, files=files, functionName='upload reference'):
            return self.getResponseData()
        
    # GENERIC METHOD CALLED BY MOST get /integration/processes/
        
    def dumpJsonToFile(self, jsondata, filename='jsonOutput'):
        if self._dumpToFile:
            json_object = json.dumps(jsondata, indent=4)
            # Serializing json
            with open(f'json_result_examples/{filename}.json', "w") as outfile:
                outfile.write(json_object)

    def _retrieveIntegrationProcesses(self, urlTail, params=None):
        if params == None:
            params = {'org' : self.orgkey}    
        url= f'{self.getURL()}/integration/processes/{self.key}/{urlTail}'
        functionName = 'retrieve ' + urlTail
        headers = self.getHeaders()
        if self.sendGetRequest(url=url, verify=self.verify, params=params, headers=headers, functionName=functionName):
            return self.getResponseData()
            

    def retrieveKPISettings(self, fromMaster=False):
        params = {'org' : self.orgkey, 'fromMaster' : fromMaster}
        jsondata = self._retrieveIntegrationProcesses('kpi-settings', params=params)
        if jsondata:
            self._dumpToFile(jsondata, 'kpi-settings')
            return jsondata
                        
    def _retrieveIntegrationProcessesWithFilters(self, urlTail, filters, jobkeyfunction, jsonStopField, jsonStopValue=None):
        url= f'{self.getURL()}/integration/processes/{self.key}/{urlTail}'
        functionName = f'retrieve {urlTail} with filters'
        data = json.dumps(filters)
        headers = self.getHeaders()
        params =  {'org' : self.orgkey}
        if self.sendPostRequest(url=url, verify=self.verify, params=params, headers=headers, data=data, functionName=functionName):
                # Async call --- the caller need to loop on get job status that it is completed
            job_key = self.getResponseData() # that's the job key
        else:
            return None
        runningCall = 1
        print("Process Mining: refreshing with filters (please wait)")
        spinner = spinning_cursor()
        while  runningCall : # The job APIs are not homogeneous. Requires workarounds
            if jobkeyfunction(job_key):
                jsondata = self.getResponseData()
                if jsondata[jsonStopField]:
                    if jsonStopValue and jsondata[jsonStopField]==jsonStopValue:
                        runningCall = 0
                    elif jsonStopValue == None:
                         runningCall = 0                      
            else:
                return
            sys.stdout.write(next(spinner))
            sys.stdout.flush()
            sys.stdout.write('\b')
            time.sleep(SPINNING_RATE)
        return self.getResponseData()  

    def retrieveModelStatistics(self, filters=None):
        # jsondata['processAnalysis'], jsondata['model']['nodes'], jsondata['model']['edges']
        if filters == None:
            return self._retrieveIntegrationProcesses('model-statistics')
        else:
            return self._retrieveIntegrationProcessesWithFilters('model-statistics',filters, self.retrieveModelStatisticsJobStatus, 'model')
              
    def getTransitionStatistics(self, ModelStatistics, sourceActivity=None, targetActivity=None):
        if sourceActivity == None:
            return ModelStatistics['model']['edges']
        for transition in ModelStatistics['model']['edges']:
            if transition['sourceActivity'] == sourceActivity and transition['targetActivity'] == targetActivity:
                return transition
    
    def getActivityStatistics(self, ModelStatistics, activityName=None):
        if activityName==None:
            return ModelStatistics['model']['nodes']
        for activity in ModelStatistics['model']['nodes']:
            if activity['activityName'] == activityName:
                return activity
            
    def getProcessStatistics(self, ModelStatistics):
        return ModelStatistics['processAnalysis']

    def retrieveDeviationsJobStatus(self, job_key):
        if self.sendGetRequest(
            f'{self.getURL()}/integration/jobs/deviations/{job_key}',
            verify=self.verify,
            params={},   
            headers=self.getHeaders(),
            functionName='get deviations job status'):

            return self.getResponseData()
        
    def retrieveDeviations(self, filters=None):
        if filters == None:
            return self._retrieveIntegrationProcesses('deviations') 
        else:
            return self._retrieveIntegrationProcessesWithFilters('deviations',filters, self.retrieveDeviationsJobStatus, 'status','complete')

    def retrieveFilters(self):
        if self._retrieveIntegrationProcesses('filters'):
            jsondata = self.getResponseData()
            return jsondata['filters']  # remove the filters layer

    def retrieveTemplates(self):
        params = {'org' : self.orgkey}    
        url= f'{self.getURL()}/integration/projects/{self.key}/filter-templates'
        functionName = 'retrieve filter-templates'
        headers = self.getHeaders()
        if self.sendGetRequest(url=url, verify=self.verify, params=params, headers=headers, functionName=functionName):
            return self.getResponseData()

    def retrieveKpiJobStatus(self, job_key):
        if self.sendGetRequest(
            f'{self.getURL()}/integration/jobs/kpi-status/{job_key}',
            verify=self.verify,
            params={},   
            headers=self.getHeaders(),
            functionName='get kpi-status job status'):

            return self.getResponseData()
                
    def retrieveKpiStatus(self, filters=None):
        if filters == None:
            return self._retrieveIntegrationProcesses('kpi-status') 
        else:
            return self._retrieveIntegrationProcessesWithFilters('kpi-status',filters, self.retrieveKpiJobStatus, 'status','complete')

    def retrieveVariants(self, size):
        params = {'org' : self.orgkey, 'page' : 0, 'size' : size}    
        jsondata = self._retrieveIntegrationProcesses('variants', params=params)
        if jsondata:
            return jsondata['items']
        
    def retrieveStatus(self):
        return self._retrieveIntegrationProcesses('status')  
        
    def retrieveSettings(self, fromMaster=False):
        params = {'org' : self.orgkey, 'fromMaster' : fromMaster}    
        return self._retrieveIntegrationProcesses('project-settings', params=params)  
        
    def retrieveSettingsActivityCost(self, fromMaster=False):
        params = {'org' : self.orgkey, 'fromMaster' : fromMaster}    
        return self._retrieveIntegrationProcesses('project-settings/activities-cost', params=params)
    
    def retrieveSettingsActivityWorkingTime(self, fromMaster=False):
        params = {'org' : self.orgkey, 'fromMaster' : fromMaster}    
        return self._retrieveIntegrationProcesses('project-settings/activities-working-time', params=params)
     
    def retrieveMetaInfo(self):
        return self._retrieveIntegrationProcesses('meta') 
    
    def retrieveCustomMetrics(self):
        return self._retrieveIntegrationProcesses('custom-metrics') 
    
    def setActivityCost(self, activityName, cost, type='Manual', endDate=None):
        jsondata = {'cost': cost, 'type': type}
        if endDate: jsondata['endDate'] = endDate
        data = json.dumps(jsondata)
        return self.sendPostRequest(
            url=f'{self.getURL()}/integration/processes/{self.key}/project-settings/activities-cost/{activityName}',
            verify=self.verify,
            params={'org' : self.orgkey},
            headers=self.getHeaders(),
            data=data,
            files=None,
            functionName='set activity cost')
    
