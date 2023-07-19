# Simple Process App that uses a ZIP file loaded by the user
In this example, the user will upload a ZIP file that contains one or several files to process in order to create the event log.

To keep it very simple, here we are uploading a ZIP file that just contains a simple CSV file ready to be ingested. A more sophisticated example will be developed later on.

- Create a process app
- Load the simplecode.py (execution code)

- Create a process with this process app
- Upload the file 'justatest.zip'

The program will retrieve the justatest.zip file that is located in the server's, in the process app directory. We unzip the file: justatest.csv is now located in the same directory.

We can read this file with ```pd.readcsv('./justatest.csv')```
