from langchain_core.tools import BaseTool
import requests
import json
import os

class BasePMTool(BaseTool):
 
   url :str= os.getenv('PM_API_URL')
   user :str  = os.getenv('PM_API_USER')
   key :str =os.getenv('PM_API_KEY')

   def getToken(self):
      keyResponse =  requests.post(self.url+"/integration/sign", 
                                   headers = {"content-type": "application/json"},
                                   verify=False,
                                   data=json.dumps({"uid": self.user, 
                                                    "apiKey": self.key}))
      return keyResponse.json()["sign"];
  
   def getRequestHeader(self, token):
      return {"content-type": "application/json", "Authorization": f"Bearer {token}" }