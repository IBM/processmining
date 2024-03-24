import IPMBase as ipmb
import IPMDashboard as ipmd
import sys
import time
import json

import requests, json, urllib3
requests.packages.urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SPINNING_RATE = 0.1

def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor

class Project(ipmb.Base):
    def __init__(self, organization, name, key, jsondata=None):
        ipmb.Base.__init__(self)
        self.client = organization.client
        self.organization = organization
        self.key = key
        self.name = name
        self.dashboards = []
        self.backupList = []
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
        params={'org' : self.organization.key, 'dataSetOverride' : datasetOverride}
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
            job_status = self.getCSVJobStatus(job_key)
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
        
    def getCSVJobStatus(self, job_key):
        if self.sendGetRequest(
            f'{self.getURL()}/integration/csv/job-status/{job_key}',
            verify=self.verify,
            params={},   
            headers=self.getHeaders(),
            functionName='get CSV job status'):

            return self.getResponseData()
        
    def uploadBackup(self, backupfilename):

        if self.sendPostRequest(
            url=f'{self.getURL()}/integration/processes/{self.key}/upload-backup',
            verify=self.verify,
            params={'org' : self.organization.key},      
            headers={"Authorization": "Bearer %s" % self.client.token},
            files={'file': (backupfilename, open(backupfilename, 'rb'),'text/zip')},
            functionName='upload backup'):

            return self.getResponseData()
    
    def retrieveBackupList(self):
        if self.sendGetRequest(
            url=f'{self.getURL()}/integration/processes/{self.key}/backups',
            verify=self.verify,
            params={'org' : self.organization.key},      
            headers=self.getHeaders(),
            functionName='retrieve backup list'):

            self.backupList = self.getResponseData()['backups']
            return self.backupList
    
    def getBackupList(self):
        if self.backupList:
            return self.backupList
        return self.retrieveBackupList()

    def applyBackup(self, backupId):
        if self.sendPutRequest(
            url=f'{self.getURL()}/integration/processes/{self.key}/backups/{backupId}',
            verify=self.verify,
            headers=self.getHeaders(),
            params={'org' : self.organization.key},
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
            params={'org' : self.organization.key},
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
            job_status = self.getCSVJobStatus(job_key)
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

    
    def retrieveMetaInfo(self):
        url=f"{self.getURL()}/integration/csv/{self.key}/meta"
        params={'org' : self.organization.key}
        headers=self.getHeaders()
        if self.sendGetRequest(url=url, verify=self.verify,params=params,headers=headers, functionName='retrieve meta info'):
            self.info = self.getResponseData()
            return self.getResponseData()
    
    def retrieveInformation(self):
        if self.sendGetRequest(
            url=f"{self.getURL()}/integration/processes/{self.key}",
            verify=self.verify,
            params={'org' : self.organization.key},
            headers=self.getHeaders(),
            functionName='retrieve project info'):

            self.info = self.getResponseData()['info']
            self.navigation = self.getResponseData()['navigation']
            self.performance = self.getResponseData()['performance']
            return self.getResponseData()
        return None
    
    def getInfo(self) : return self.info
    def getPerformance(self) : return self.performance
    def getNavigation(self) :  return self.navigation
    
    def getDashboards(self):
        if (self.dashboards): return self.dashboards
        return self.retrieveDashboards()

    def retrieveDashboards(self):
        if self.sendGetRequest(
            url=f"{self.getURL()}/analytics/integration/dashboard/{self.key}/list",
            verify=self.verify,
            params={'org' : self.organization.key},
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
            url=f"{self.getURL()}/analytics/integration/projects/{self.key}/query",
            verify=self.verify,
            params={'org' : self.organization.key},
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
    
    def retrieveWorkflow(self, viewType):
        viewTypes = [
            {'type':'Frequency view', 'value':0},
            {'type':'Performance view (Avg)', 'value':1},
            {'type':'Performance view (Min)', 'value':2},
            {'type':'Performance view (Max)', 'value':3},
            {'type':'Performance view (Median)', 'value':4},
            {'type':'Rework view', 'value':5},
            {'type':'Performance view (Weighted)', 'value':6},
            {'type':'Cost view', 'value':7},
            {'type':'Overall cost view', 'value':8},
            ]

        params = {'org' : self.organization.key, 'viewType': viewType}    
        headers = self.getHeaders()
        url = f"{self.getURL()}/integration/csv/{self.key}/workflow"
        verify=self.verify,
        if self.sendGetRequest(url=url,params=params,headers=headers, verify=verify, functionName='retrieve dashboards'):
            return self.getResponseData()  
        
    def retrieveBPMN(self):

        params = {'org' : self.organization.key}    
        headers = self.getHeaders()
        url = f"{self.getURL()}/integration/export/{self.key}/BPMN"
        if self.sendGetRequest(url=url, verify=self.verify, params=params, headers=headers, functionName='retrieve bpmn'):
            return self.getResponseData()     