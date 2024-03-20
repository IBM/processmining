from BasePMTool import BasePMTool
import requests
from typing import Optional
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.pydantic_v1 import (
    BaseModel,
    Field  
)
import json


class CreateProjectInput(BaseModel):
    project_name: str = Field(..., description="Name of a process mining project")
 

class CreateProjectTool(BasePMTool):
    return_direct: bool = True
    name = "create_project"
    args_schema = CreateProjectInput

    description = """Use this tool when you need to create a new process mining project.Make sure you use a input format similar to the JSON below:
    {{ "project_name": "the project name"}}"""

    def _run(self, project_name: str) -> str:
        """Use the tool."""

        return self.createProject(project_name)
    
    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("API does not support async")
    
    def createProject(self, project_name):      
      token = self.getToken();
      project_name = str(project_name).strip()
      response = requests.post(self.url+f'/integration/processes',
                               headers = self.getRequestHeader(token),
                               verify=False,
                               data=json.dumps({"title" : project_name, 
                                                "org" : "" }))
      jsonresponse = response.json();
      if response.status_code == 200:
         return f"The project was created with name {jsonresponse['projectKey']} " ;
      else:
         if 'data' in jsonresponse:
             return f"There was en error creating the project : {jsonresponse['data']}";
         return 'There was en error creating the project'
  
   