import IPMBase as ipmb   
import IPMWidgets as ipmw

class Dashboard(ipmb.Base):
    def __init__(self, project, jsondata):
        ipmb.Base.__init__(self)
        self.project = project
        self.name = jsondata['name']
        self.id = jsondata['id']
        self.jsondata = jsondata
        self.widgets = None
    
    def getHeaders(self):
        return self.project.getHeaders() 
    
    def getURL(self):
        return self.project.client.url
    
    def retrieveWidgets(self):
        params = {'org' : self.project.organization.key}      
        headers = self.getHeaders()
        url = "%s/analytics/integration/dashboard/%s/%s/list" % (self.getURL(), self.project.key, self.id)
        if self.sendGetRequest(
            url=url,
            verify=self.verify,
            params=params,
            headers=headers,
            functionName='retrieve widgets'
        ):
            self.widgets = []
            for jsonWidget in self.getResponseData()['widgets']:
                widget = ipmw.Widget(self, jsonWidget)
                self.widgets.append(widget)
            return self.widgets
        
    def getWidgets(self):
        if self.widgets:
            return self.widgets
        else:
            return self.retrieveWidgets() 

    def getWidgetByName(self, name):
        widgets = self.getWidgets()
        for widget in widgets:
            if widget.name == name:
                return widget
        self.setResponseDataFailed()
