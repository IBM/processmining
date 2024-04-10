# BAW BPM Process App

WARNING: Since version 1.14.4 (March 2024), a new version of the BAW process app has been released by the Process Mining development team. For more information, read the official documentation: [BAW App](https://www.ibm.com/docs/en/process-mining/1.14.4?topic=SSWR2IP_1.14.4/process-mining-documentation/user-manuals/accelerator/Using_the_custom_Process_App_for_BAW.htm)

You can download the asset from this link: [Download](https://github.com/nikhil-ps-ibm/processmining_externalFilesbyDocs/blob/BAWAssets/Process%20Apps/BAW-IBM-Process-Mining-Assets.zip)

## OBSOLETE
This process app relies on BAW BPM REST API to fetch instances and tasks from the BAW database, and to create an event for each BPD instance task.

This is a simplified and limited version of the BAW Accelerator https://github.com/IBM/ibm-process-mining-BAW-accelerator. This standalone version should be used whenever you need to fetch several thousands of tasks. You can leverage multi threading increase the speed by 10 times, you can recover from errors, and so forth.


## BAW BPM Process App Overview
A Process App is created in IBM Process Mining through a simple UI wizard
- Name the process app, provide a short description, etc
- Upload the python file that is executed
- Upload a process mining backup file (IDP) that defines the mapping, and optionnally KPIs, filters, custom metrics, costs, dashboards, etc.
- Define the process app input parameters that the user will set to connect and extract the data

## Python file
The python program defines entirely what the process app does to connect to the data source and to create the event-log. IBM Process Mining will call the function ```execute(context)``` that you must declare and define.

```python
def execute(context):
    # Get the input parameters
    config = context['config']

    # Get the data from the source (ex: call BAW REST API to fetch instances and tasks for each instance)
    event_list = everything_you_need_to_do_to_get_the_events(config)

    # Create and return a Pandas dataframe that contains all the events 
    return(pd.dataframe(event_list))
``` 

## Tips
You need to test your python code as a standalone program, before loading it into the process app.
- Create a ```default_config``` object for testing your app
- Add a ```__main__```

The process app can display exceptions from the process app UI, but you need to raise ```ProcessAppException``` to see these messages. We import ProcessAppException from process_app, but this package is not yet available externally. For convenience, we redefine this class when running as standalone, such that our code can run unchanged as standalone or when loaded in IBM Process Mining.

```python
# When loaded into Process Mining, the import works.
# To run/debug this program as a standalone code, we redefine the ProcessAppException class below
try:
    from process_app import ProcessAppException
except: 
    class ProcessAppException(Exception):
        def __init__(self, message):
            self.message=message
            super().__init__(self.message)
        def getMessage(self):
            return self.message

def execute(context):
    # Get the input parameters
    config = context['config']

    # Example testing that a input parameter from_date is matching the expected date format
    try:
        dateObject = datetime.datetime.strptime(config['from_date'], date_format)
        config['from_date'] = dateObject.strftime(baw_date_format)
    # If the date validation goes wrong
    except Exception as e:   # printing the appropriate text if ValueError occurs
        raise ProcessAppException("Incorrect date format, should be like this 2022-10-08" + str(e))

    # Get the data from the source (ex: call BAW REST API to fetch instances and tasks for each instance)
    event_list = everything_you_need_to_do_to_get_the_events(config)

    # Create and return a Pandas dataframe that contains all the events 
    return(pd.dataframe(event_list))

if __name__ == "__main__":
    context = {'config': default_config}
    df = execute(context) 
    print (df)
``` 





