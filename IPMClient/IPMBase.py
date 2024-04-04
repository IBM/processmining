#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests, json, urllib3
import json

requests.packages.urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# connector is passed to most function, this is a json object that includes all the required parameters


class Base():
    def __init__(self):
        self.response_data = None
        self.verify = False
        self.traceChoice = False
        self.traceDetails = 0 # 0=No details, 1=Print the URL, 2=print the response data
        self.jsondata = None
    
    def getJSONData(self):return self.jsondata    
    def getHeaders(self): return {"content-type": "application/json", "Authorization": "Bearer %s" % self.token } 
    def getResponseData(self): return self.response_data['data']
    def getResponseStatusCode(self): return self.response_data['status_code']
    def isResponseKO(self): return not self.response_data['success']
    def isResponseOK(self): return self.response_data['success']
    def _setResponseKO(self):
        self.response_data = {'success': False, 'data': None, 'status_code':-1}
    def _setResponseOK(self, data):
        self.response_data = {'success': True, 'data': data, 'status_code':-1}


    def setVerify(self, choice=False): 
        self.verify = choice
        return self.verify

    def setTrace(self, choice, traceDetails=0):
        self.traceChoice = choice
        if traceDetails: self.traceDetails = traceDetails
        return choice
    
    def getTrace(self): return self.traceChoice

    def trace(self, response, function_name):
        msg = f"--Process Mining: REST API called for: {function_name} : status code : {response.status_code}"
        if self.traceDetails:
            msg = f"{msg}: url: {response.url}"
            print(msg)
            if self.traceDetails == 2:
                msg =f"--- Returned data:{response.json()}"
                print(msg)
        else: print(msg)

    def handleResponse(self, response, function_name):
        if self.trace: self.trace(response, function_name)

        jresponse = response.json()
        if (response.status_code == 200 or response.status_code == 202) and jresponse['success']:
            match function_name:
                case 'get token': self.response_data = {'data': jresponse['sign'], 'success': True, 'status_code': 200}
                case 'create project': self.response_data = {'data': jresponse['projectKey'], 'success': True, 'status_code': 200}
                case 'upload backup': self.response_data = {'data': jresponse['backupInfo'], 'success': True, 'status_code': 200}
                case 'delete project': self.response_data = {'data': jresponse['projectKey'], 'success': True, 'status_code': 200}
                case 'delete backup': self.response_data = {'data': None, 'success': True, 'status_code': 200}
                case 'get deviations job status': self.response_data = {'data': jresponse, 'success': True, 'status_code': 200}
                case 'get kpi-status job status': self.response_data = {'data': jresponse, 'success': True, 'status_code': 200}
                case default: self.response_data = {'data':jresponse['data'], 'success':True, 'status_code': 200}
            return
        elif 'data' in jresponse:
                self.response_data = {'data':jresponse['data'], 'success':False, 'status_code': response.status_code}
                if 'error' in jresponse:
                    msg = f"--Process Mining: ERROR: {function_name} : error code {response.status_code} : error {jresponse['error']} : {jresponse['data']}";
                else:
                    msg = f"--Process Mining: ERROR: {function_name} : error code {response.status_code} : {jresponse['data']}";
                print(msg)
                return
        msg = f"--Process Mining: ERROR: {function_name} : error code : {response.status_code}";
        print(msg)
        self.response_data = {'data':'', 'success':False, 'status_code': response.status_code}
        return 
    
    def sendGetRequest(self, url, verify, headers, params, functionName):
        self.handleResponse(requests.get(url, verify=verify, headers=headers, params=params), functionName)
        if self.isResponseOK():
            return self.getResponseData()
    
    def sendPostRequest(self, url=str, verify=False, headers=json, params=json, data=None, files=None, functionName=str):
        self.handleResponse(requests.post(url, verify=verify, headers=headers, params=params, data=data, files=files), functionName)
        if self.isResponseOK():
            return self.getResponseData()   

    def sendDeleteRequest(self, url, verify, headers, params, functionName):
        self.handleResponse(requests.delete(url, verify=verify, headers=headers, params=params), functionName)
        if self.isResponseOK():
            return self.getResponseData()   
        
    def sendPatchRequest(self, url, verify, headers, params, data, functionName):
        self.handleResponse(requests.patch(url, verify=verify, headers=headers, params=params, data=data), functionName)
        if self.isResponseOK():
            return self.getResponseData()   
        
    def sendPutRequest(self, url, verify, headers, params, functionName):
        self.handleResponse(requests.put(url, verify=verify, headers=headers, params=params), functionName)
        if self.isResponseOK():
            return self.getResponseData()
    
    