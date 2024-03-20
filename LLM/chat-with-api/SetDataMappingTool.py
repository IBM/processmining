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

class SetDataMappingToolInput(BaseModel):
    project_name: str = Field(..., description="Name of a process mining project")
    activity_column_name: str = Field(..., description="Name of a column in the CSV representing activity name")
    activity_column_index: int = Field(..., description="Index of a column in the CSV representing activity name")
    case_id_name: str = Field(..., description="Name of a column in the CSV representing the case id")
    case_id_index: int = Field(..., description="Index of a column in the CSV representing the case id")
    start_time_name: str = Field(..., description="Name of a column in the CSV representing the start time")
    start_time_index: int = Field(..., description="Index of a column in the CSV representing the end time")

 
column_mappings = {}  

class SetDataMappingTool(BasePMTool):
    return_direct: bool = True
    name = "set_data_mapping"
    args_schema = SetDataMappingToolInput

    description = """Use this tool when you need to specify the data mapping for the CSV columns"""

    def _run(self, project_name: str, 
              activity_column_name: str = '' ,
              activity_column_index: int = -1,
              case_id_name: str  = '',
              case_id_index: int =-1,
              start_time_name: str  = '',
              start_time_index: int =-1
             ) -> str:
        """Use the tool."""
        mapping = {} 
        if (project_name in column_mappings):
            mapping = column_mappings[project_name];
        
        if  activity_column_name != '' :
            mapping.update({'activity_column_name' : activity_column_name})
        if  case_id_name != '' :
            mapping.update({'case_id_name' : case_id_name})
        if  start_time_name != '' :
            mapping.update({'start_time_name' : start_time_name})
        if  start_time_index >=0 :
            mapping.update({'start_time_index' : start_time_index})
        if  activity_column_index >= 0 :
            mapping.update({'activity_column_index' : activity_column_index})
        if  case_id_index >= 0 :
            mapping.update({'case_id_index' : case_id_index})

        column_mappings[project_name] = mapping;
        
        if 'activity_column_name' in mapping:
            activity_column_name = mapping['activity_column_name']
        else:
            activity_column_name = 'Unknown'
            
        if 'case_id_name' in mapping:
            case_id_name = mapping['case_id_name']
        else:
            case_id_name = 'Unknown'
            
        if 'start_time_name' in mapping:
            start_time_name = mapping['start_time_name']
        else:
            start_time_name = 'Unknown'
            
        if 'activity_column_index' in mapping:
            activity_column_index = mapping['activity_column_index']
        else:
            activity_column_index = 'Unknown'
        if 'case_id_index' in mapping:
            case_id_index = mapping['case_id_index']
        else:
            case_id_index = 'Unknown'
        if 'start_time_index' in mapping:
            start_time_index = mapping['start_time_index']
        else:
            start_time_index = 'Unknown'
            
        return f"""The current binding is :
Activity name: '{activity_column_name}' (column index: {activity_column_index})
Start time: '{start_time_name}' (column index: {start_time_index})
Case ID: '{case_id_name}' (column index: {case_id_index}) """
       
    
    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("API does not support async")
    
    