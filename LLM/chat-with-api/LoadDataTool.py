from BasePMTool import BasePMTool
import os
import requests
import threading
import time
import pandas as pd
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
import ibm_boto3
from ibm_botocore.client import Config, ClientError
from SuggestMapping import suggestMapping
from SuggestDateFormat import suggestDateFormat

# Constants for IBM COS values
COS_ENDPOINT = os.getenv('COS_ENDPOINT', 'https://s3.us-south.cloud-object-storage.appdomain.cloud')
COS_API_KEY_ID = os.getenv('COS_API_KEY_ID')
COS_INSTANCE_CRN = os.getenv('COS_INSTANCE_CRN')

class LoadDataToolInput(BaseModel):
    project_name: str = Field(..., description="Name of a process mining project")
    filename: str = Field(..., description="path of a csv file")

class ProgressPercentage(object):
    def __init__(self, filesize):
        self._size = filesize
        self._seen_so_far = 0

    def __call__(self, bytes_amount):
        self._seen_so_far += bytes_amount
        self.done = self._seen_so_far == self._size

class LoadDataTool(BasePMTool):
    return_direct: bool = True
    name = "upload_data"
    args_schema = LoadDataToolInput

    description = """Use this tool when you need to load csv data in a project.  Make sure you use as input a format similar to the JSON below:
    {{ "project_name": "the project name" , "filename": "the csv file name"}}""" 

    def _run(self, project_name, filename) -> str:
        """Use the tool."""
        return self.loadCSV(project_name, filename)
    
    async def _arun(self, **params) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("API does not support async")
    
    def loadCSV(self, project_name, filename):      
      """Loads the object in cloud object storage with the name 'filename' in bucket processmining"""
      filecreated = False
      localfile = None
      try:

            s3 = ibm_boto3.client("s3", ibm_api_key_id=COS_API_KEY_ID,
                                  ibm_service_instance_id=COS_INSTANCE_CRN,
                                  config=Config(signature_version="oauth"),
                                  endpoint_url=COS_ENDPOINT)
 
            myuuid = uuid.uuid4()
            sizeResponse = s3.head_object(Bucket='processmining', Key=filename)
            filesize = sizeResponse['ContentLength']
            localfile = f'/tmp/{myuuid}'
            callback = ProgressPercentage(filesize);
            s3.download_file('processmining', filename, localfile ,Callback = callback)
            while not callback.done:
                """wait"""
            print(f'File was downloaded from COS in {localfile}')
            filecreated = True
            token = self.getToken();
            response = requests.post(self.url+f'/integration/csv/{project_name}/upload?org=&sign={token}',
                                     #headers = self.getRequestHeader(token),
                                     files={'file' : (filename, open(localfile, 'rb'), 'text/zip')}, 
                                     verify=False)
            print('Response from Process Mining posting file', response)

            jsonresponse = response.json()
            if response.status_code == 200:
              # downloading in progress
              jobid =  jsonresponse['data'];
              uploaded= False;
              while not uploaded:
                 time.sleep(2);
                 response = requests.get(self.url+f'/integration/csv/job-status/{jobid}' ,
                                         verify=False,                                
                                         headers = self.getRequestHeader(token))
                 print(response)
                 if response.status_code == 200 :
                    uploaded = response.json()['data'] == 'complete'
                    if response.json()['data'] == 'error':
                          return "Error downloading data";

                 else:
                   return "Error downloading data";
              try: 
                 if '.zip' in filename :
                   df = pd.read_csv(localfile, compression='zip', nrows=3)
                 else:
                   df = pd.read_csv(localfile,  header=0, nrows=4)
                
                 # try to suggest data mapping
                 suggestion = suggestMapping(str(df.columns.values.tolist()))
                 dateformat = suggestDateFormat(df.to_string())
                 return f"The file was downloaded\n\nHere are the first 3 rows.\n{df.to_string()} \n\n{suggestion}\n\n{dateformat}"
              except Exception as e:
                print(e)
                return "The file was downloaded";

            else:
             if 'data' in jsonresponse:
               return jsonresponse['data'];
             return 'Error running the tool'
         # TODO delete the local file on all cases.
      except ClientError as a:
          if '404' in str(a):
              return 'Cannot load data to the project. The file was not found';
          return 'Cannot load data to the project. ' + str(a)
      except Exception as e:
          return 'Cannot load data to the project. ' + str(e)
      finally:
          if filecreated:
              os.remove(localfile)
          