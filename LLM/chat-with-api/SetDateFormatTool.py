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

class SetDateFormatToolInput(BaseModel):
    project_name: str = Field(..., description="Name of a process mining project")
    dateformat: str = Field(..., description="java date time format for the project")
 
 
date_formats = {}  

class SetDateFormatTool(BasePMTool):
    return_direct: bool = True
    name = "set_date_format"
    args_schema = SetDateFormatToolInput

    description = """Use this tool when you need to set the date format that should be used for a project"""

    def _run(self, project_name: str, 
              date_format: str  ,
             ) -> str:
        """Use the tool."""
        date_formats[project_name] = date_format;
            
        return f"""The format for dates will be {date_format}"""
       
    
    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("API does not support async")
    
    