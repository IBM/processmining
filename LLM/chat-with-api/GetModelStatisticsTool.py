from BasePMTool import BasePMTool
import SetDataMappingTool
import SetDateFormatTool
import os
import time
import requests
from typing import Optional
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
import uuid
from langchain_core.pydantic_v1 import (
    BaseModel,
    Field  
)
import json


class GetModelStatisticsInput(BaseModel):
    project_name: str = Field(..., description="Name of a process mining project")

class GetModelStatisticsTool(BasePMTool):
    return_direct: bool = True
    name = "get_statistics"
    args_schema = GetModelStatisticsInput

    description = """The tool provides statistics on activities for a specified project. You will need to use the format :
    {{ "project_name": "the project name"}}""" 

    def _run(self, project_name) -> str:
        """Use the tool."""
        return self.getprocessModelStats(project_name)
    
    async def _arun(self, **params) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("API does not support async")
    
    def getprocessModelStats(self, project_name):      
      """Gets the  process model stats"""
      try:
            token = self.getToken()
            response = requests.get(self.url+f'/integration/processes/{project_name}/model-statistics',                 
                headers = self.getRequestHeader(token),
                params = { 'org' : ''},
                verify=False)
            jsonresponse = response.json()
            if response.status_code == 200:
              # downloading in progress
              data =  jsonresponse['data'];
              print(data)
              res =  "Here are the statistics on activities:\n" 
              for node in data['model']['nodes']:
                if node['activityName'] != 'START' and node['activityName'] != 'STOP':
                  res += f"<b>{node['activityName']} </b>: frequency ({node['statistics']['frequency']}), avg duration ({node['statistics']['avgDuration']}) ,  cost ({node['statistics']['cost']})\n"""
              return res;
            else:
             if 'data' in jsonresponse:
               return jsonresponse['data'];
             return 'Error running the tool'
      except Exception as e:
          return 'Cannot get activity stats on the project. ' + str(e)