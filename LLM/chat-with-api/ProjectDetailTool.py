from langchain_core.tools import BaseTool
from langchain_core.pydantic_v1 import (
    BaseModel,
    Field  
)
import requests
from typing import Optional
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
import json
from BasePMTool import BasePMTool


class ProjectDetailInput(BaseModel):
    project_name: str = Field(..., description="Name of a process mining project")
 
class ProjectDetailTool(BasePMTool):

    name = "get_project_detail"
    description = """ The tool can provide  the owner of the project, the number of cases,     
    the number of events and the organization of the project.  Please note the returned 
    durations are expressed in milliseconds.
    """

    args_schema = ProjectDetailInput

    def _run(self, project_name: str,
             run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""
        return self.getProjectFromNameWithAPI(project_name)
    
    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("API does not support async")
    
    def getProjectFromNameWithAPI(self, name):
        response = requests.get(self.url+f'/integration/processes',               
                                headers = self.getRequestHeader(self.getToken()),
                                verify = False)

        if response.status_code == 200:
            #might be that the process is incomplete and the API return 400. invoke the API with all projects to check.abs
            for p in response.json()['data'] :
                if p['projectName'] == name or p['projectTitle'] == name:
                    return str(p)
            return "The project does not exist."     

        else:
         return "The tool has some issue, try later."     