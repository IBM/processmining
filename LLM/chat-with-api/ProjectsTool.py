from BasePMTool import BasePMTool
from langchain_core.tools import BaseTool
import requests
from typing import Optional
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
import json

class ProjectsTool(BasePMTool):
    return_direct: bool = False
    name = "get_project_list"
    description = "return a list of all process mining projects. "

    def _run(self) -> str:
        """Use the tool."""
        return self.getProjectsFromAPI()
    
    async def _arun(self) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("API does not support async")
    
    def getProjectsFromAPI(self):
      token = self.getToken();
      response = requests.get(self.url+f'/integration/processes', 
                              verify=False,                               
                              headers = self.getRequestHeader(token))
      data = response.json()['data']
     
      return str(data) 