import IPMBase as ipmb

class Tenant(ipmb.Base):
    def __init__(self, client, jsondata):
        ipmb.Base.__init__(self)
        self.client = client
        self.name = jsondata['name']
        self.key = jsondata['tenantId']
        self.accounts = None

    def getHeaders(self): return {"content-type": "application/json", "Authorization": "Bearer %s" % self.client.token } 
    def getURL(self): return self.client.url

# ACCOUNT MANAGEMENT
        
    def getAccounts(self)->list:
        if self.accounts: return self.accounts
        return self.client.retrieveAccounts(self)
    
    def getAccountByUserName(self, username):
        accounts = self.getAccounts()
        for account in accounts:
            if account.username == username: 
                return account
        self._setResponseKO()

    def _removeAccount(self, account):
        accounts = self.getAccounts()
        for index, item in enumerate(accounts):
            if item == account:
                self.accounts.pop(index)
                return account   