## Introduction 
The integration of the Langchain project with ProcessMining allows to invoke a various set of tools to create a proccess mining project with a conversational interface.


## Pre-requisites
  * Python 3.8 or higher
  * A process mining server running
  * An IBM®  Cloud Object Storage account where you place the CSV files you want to use for process mining. The CSV files will be retrieved from a bucket named processmining
  * A IBM® watsonx.ai™ AI studio account to access the fondational model used - here the llama-2-70b-chat


## Setup Pre-Requisites

setup the environement variables.

 GENAI_KEY  : your watsonX.ai key
 GENAI_API  : the watsonX.ai endpoint URL
 

 PM_API_URL  :  The URL of you process mining public API
 PM_API_USER : Your user name in the process mining instace
 PM_API_KEY : the API key for process mining

 COS_ENDPOINT :optional COS endpoint , the default is https://s3.us-south.cloud-object-storage.appdomain.cloud
 COS_API_KEY_ID : Your COS API KEY 
 COS_INSTANCE_CRN : Your COS instance CRN 


### Create a virtual env and install the Python package
```shell
python -m venv ~/pm-llm
source ~/pm-llm/bin/activate
pip install -r requirements.txt
```


### Run the Chat application

Open a new terminal
```
python app.py
```


Then open a browser to this url : http://127.0.0.1:7860

Then you can ask queston to the chat bot such as:
   * can you create a project name XY
   * how many events in project AB
   * can you upload the file AA.csv to the project B
   * can you mine the project Z

