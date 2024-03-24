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

class DeleteProjectInput(BaseModel):
    project_name: str = Field(..., description="Name of a process mining project")
 
class DeleteProjectTool(BasePMTool):
    return_direct: bool = True
    name = "delete_project"
    args_schema = DeleteProjectInput

    description = """Use this tool when you need to delete a process mining project providing its name."""

    def _run(self, project_name: str) -> str:
        """Use the tool."""

        return self.deleteProject(project_name)
    
    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("API does not support async")
    
    def deleteProject(self, project_name):      
      token = self.getToken();
      project_name = str(project_name).strip()
      response = requests.delete(self.url+f'/integration/processes/{project_name}?org=', 
                                 headers = self.getRequestHeader(token),
                                 verify=False)
      responsedata = response.json()
      if response.status_code == 200:
         return f'The project {project_name} was removed' 
      else:
        if 'data' in responsedata:
             return f"Error trying to delete the project {project_name} : {responsedata['data']}";
        return f'Error trying to delete the project {project_name}'
  
   