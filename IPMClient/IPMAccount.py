import IPMBase as ipmb
import IPMTenant as ipmt
import json

class Account(ipmb.Base):
    def __init__(self, tenant, jsondata):
        ipmb.Base.__init__(self)
        self.tenant = tenant
        self.username = jsondata['username']
        self.email = jsondata['username']
        self.lastname = jsondata['lastName']
        self.firstname = jsondata['firstName']
        self.key = jsondata['accountId']
        self.jsondata = jsondata
        self.status = True
        dataExample = {
            "firstName": "John",
            "lastName": "Sam",
            "country": "IN",
            "email": "john.sam@ibm.com",
            "agentEnabled": True,
            "technicalUser": True,
            "active": True,
            "password": "string",
            "username": "john.sam"
        }
    
    def patch(self, jsondata):
        exampleData = {
            "firstName": "John",
            "lastName": "Sam",
            "country": "IN",
            "email": "admin@ibm.com",
            "agentEnabled": True,
            "technicalUser": True,
            "active": True,
            "password": "string"
            }
        self.username = jsondata['username']
        self.email = jsondata['username']
        self.lastname = jsondata['lastName']
        self.firstname = jsondata['firstname']
        if self.sendPatchRequest(
            url=f'{self.getURL()}/user-management/integration/tenants/{self.tenant.key}/accounts', 
            verify=self.verify,
            headers=self.getHeaders(), 
            params={},
            data=json.dumps(self.data),
            functionName='patch account'):

            self.status = True
            self.jsondata = self.getResponseData()
            return self
            

    def getHeaders(self): return {"content-type": "application/json", "Authorization": "Bearer %s" % self.tenant.client.token } 
    def getURL(self): return self.tenant.client.url