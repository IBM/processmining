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


class MiningToolInput(BaseModel):
    project_name: str = Field(..., description="Name of a process mining project")

class MiningTool(BasePMTool):
    return_direct: bool = True
    name = "mine_data"
    args_schema = MiningToolInput

    description = """Use this tool when you need perform the mining on a project. Ue the following format:
    {{ "project_name": "the project name"}}""" 

    def _run(self, project_name) -> str:
        """Use the tool."""
        return self.mine(project_name)
    
    async def _arun(self, **params) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("API does not support async")
    
    def mine(self, project_name):      
      """Loads the object in cloud ot processmining"""
      try:
            # check there is a 
            if project_name not in SetDataMappingTool.column_mappings:
                return "you should first specify a column mapping for the project"
            mapping = SetDataMappingTool.column_mappings[project_name];
            
            formattedMapping = {}
            dateformat = 'yyyy-MM-dd HH:mm:ss.SSS'
            if project_name in SetDateFormatTool.date_formats:
                dateformat = SetDateFormatTool.date_formats[project_name];
            formattedMapping[str(mapping['case_id_index'])] ={"id":"attr-process","mask":"","name":mapping['case_id_name']};
            formattedMapping[str(mapping['activity_column_index'])] ={"id":"attr-activity","mask":"","name":mapping['activity_column_name']};
            formattedMapping[str(mapping['start_time_index'])] ={"id":"attr-start-time","mask":dateformat,"name":mapping['start_time_name']};

            token = self.getToken()
            response = requests.post(self.url+f'/integration/csv/{project_name}/create-log',                 
                headers = self.getRequestHeader(token),
                params = {'mapping' : json.dumps(formattedMapping), 'org' : ''},
                verify=False)
            jsonresponse = response.json()
            if response.status_code == 200:
              # downloading in progress
              jobid =  jsonresponse['data'];
              done= False;
              while not done:
                 time.sleep(2);
                 response = requests.get(self.url+f'/integration/csv/job-status/{jobid}',
                                         headers = self.getRequestHeader(token),
                                         verify=False)
                 data = response.json()
                 if response.status_code == 200 :
                    done = data['data'] == 'complete'
                    if data['data'] == 'error':
                        if 'errors.providedFieldMappingNotValid' == data['message'] :
                          return 'The project does not have a mapping defined'
                        return f"There was a problem mining the project : {data['message']}" ;
                 else:
                   return "There was a problem mining the data.";
              return "The mining was done";
            else:
             if 'data' in jsonresponse:
               return jsonresponse['data'];
             return 'Error running the tool'
      except Exception as e:
          return 'Cannot do mining on the project. ' + str(e)