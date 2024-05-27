import IPMBase as ipmb
import pandas as pd
from datetime import datetime

class Widget(ipmb.Base):
    def __init__(self, dashboard, jsonWidget):
        ipmb.Base.__init__(self)
        self.dashboard = dashboard
        self.name = jsonWidget['title']
        self.jsondata = jsonWidget
        self.values = None
        self.jsondata = None
        self.dataframe = None

    def getHeaders(self):
        return self.dashboard.getHeaders()
    
    def getURL(self):
        return self.dashboard.project.client.url
    
    def getValues(self):
        if self.values: return self.values
        else: return self.retrieveValues()

    def retrieveValues(self):
        params = {'org' : self.dashboard.project.orgkey}      
        headers = self.getHeaders()
        url = "%s/analytics/integration/dashboard/%s/%s/%s/retrieve" % (self.getURL(), self.dashboard.project.key, self.dashboard.id, self.name)
        if self.sendGetRequest(url=url, verify=self.verify, params=params, headers=headers, functionName='retrieve widget values'):
            self.values = self.getResponseData() 
            return self.values

    def toDataFrame(self):
        if self.values:
            self.dataframe = pd.DataFrame(self.values) 
            return self.dataframe
    
    def toCSV(self, filename, replace=True):
        if replace:
            filename = filename+'.csv'
        else:
            filename = filename+'_'+datetime.now().strftime("%d_%m_%Y_%H_%M_%S")+'.csv'
        self.dataframe.to_csv(filename, index=None)

    def getURL(self):
        return self.dashboard.project.client.url