import pandas as pd
from zipfile import ZipFile
import time

def execute(context):

    # Unzip the file that includes the 3 files that we need to transform and merge
    myFileUploadName = context["fileUploadName"]
    with ZipFile(myFileUploadName, 'r') as f:
        f.extractall()

    # The 3 files are now stored in the Process Mining Server, in a directory dedicated to the process app, where the python code is stored and executed
    # as well as where the ZIP file loaded by the user is stored.
    # Therefore, all the unzipped files are accessible in the current directory
    # sleep a while until all files are extracted
    time.sleep(5)
    requisitions = pd.read_csv('./requisition.csv')
    create_requisitions = requisitions.copy()
    create_requisitions['activity'] = 'Requisition Created'
    create_requisitions.rename(columns={'Create_Date': 'datetime', 'Create_User': 'user',
                            'Create_Role': 'role', 'Create_Type': 'type', 'Create_Source': 'source'}, inplace=True)
    create_requisitions.drop(['Release_DateTime', 'Release_User', 'Release_Role',
                            'Release_Type', 'Release_Source'], axis=1, inplace=True)

    release_requisitions = requisitions.copy()
    release_requisitions['activity'] = 'Requisition Released'
    release_requisitions.drop(['Create_Date', 'Create_User', 'Create_Role',
                            'Create_Type', 'Create_Source'], axis=1, inplace=True)


    requisition_events = pd.concat([create_requisitions, release_requisitions])
    # just in case there are null dates
    requisition_events[requisition_events['datetime'].notna()]
    # Convert columns to best possible dtypes using dtypes supporting
    requisition_events.convert_dtypes()

    # procurements
    procurements = pd.read_csv('./procurement.csv', low_memory=False)

    # invoices
    invoices = pd.read_csv('./invoice.csv')

    # Merging invoice.csv information into procurement.csv
    procurement_events = procurements.merge(invoices, on="Invoice_ID", how="left")
    # Convert columns to best possible dtypes using dtypes supporting
    procurement_events.convert_dtypes()

    # Finally we append the requisition and the procurement event logs to create the final event log. Again, we can remove the events with a null `datetime`P2P_events = pd.concat([P2P_events, procurement_events])
    P2P_events = pd.concat([requisition_events, procurement_events])
    # removing rows with no datetime if any
    P2P_events = P2P_events[P2P_events["datetime"].notna()]
    P2P_events = P2P_events.convert_dtypes()  # applying the best known types

    return(P2P_events)


if __name__ == "__main__":

    context = {'fileUploadName':'P2P.zip'}
    df = execute(context)
    df.to_csv('P2Peventlog.csv', index=None)