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
    release_requisitions.rename(columns={'Release_DateTime': 'datetime', 'Release_User': 'user',
                        'Release_Role': 'role', 'Release_Type': 'type', 'Release_Source': 'source'}, inplace=True)
    release_requisitions.drop(['Create_Date', 'Create_User', 'Create_Role',
                            'Create_Type', 'Create_Source'], axis=1, inplace=True)
    # If some requisition cases are not complete, we remove rows where the requisition release date is NaN, as in
    # this case, the activity did not yet occur. This is actually never the case.
    release_requisitions = release_requisitions[release_requisitions['datetime'].notna()]

    # procurements
    procurements = pd.read_csv('./procurement.csv', low_memory=False)

    # invoices
    invoices = pd.read_csv('./invoice.csv')

    # Merging invoice.csv information into procurement.csv
    procurements = procurements.merge(invoices, on="Invoice_ID", how="left")

    # Finally we append the requisition and the procurement event logs to create the final event log. Again, we can remove the events with a null `datetime`P2P_events = pd.concat([P2P_events, procurement_events])
    P2P_events = pd.concat([create_requisitions, release_requisitions, procurements])
    # removing rows with no datetime if any
    P2P_events = P2P_events[P2P_events["datetime"].notna()]
    P2P_events = P2P_events.convert_dtypes()  # applying the best known types
    # Reordering columns to simplify mapping
    P2P_events = P2P_events[['activity','datetime', 'user', 'role', 'type',
       'source',  'Req_ID','Req_Header', 'Req_Line', 'PO_Header', 'PO_Line', 'PO_ID', 'MatDoc_Header',
       'MatDoc_Line', 'MatDoc_Year', 'MatDoc_ID', 'gr_h_y', 'Invoice_ID',
       'rses_h', 'rses_l', 'rses_y', 'mandt', 'bukrs', 'xblnr', 'fl_h', 'fl_y',
       'value_old', 'value_new', 'clear_doc', 'qmnum', 'data_gr_effettiva',
       'usertype', 'Order_Type', 'Purchasing_Group', 'Purch_Group_Type',
       'Material_Group_Area', 'Accounting_Type', 'Order_Vendor',
       'Order_Source', 'Department', 'Order_Amount', 'Material',
       'lead_time_material', 'Material_Type', 'Purch_Group_Area',
       'Requisition_Plant', 'Order_Plant', 'Material_Plant', 'data_gr_ordine',
       'data_gr_stat', 'data_gr_ipo', 'Paid_Amount', 'Paid_Vendor',
       'split_ordine', 'split_riga_ordine', 'missmatch_riga_oda',
       'check_riga_gagm', 'consegna_ipotetica', 'consegna_oda_ipotetica',
       '_consegna_statistica_ipotetica_', 'pay_delay', 'pay_type',
       'Req_Required_Vendor', 'Material_Group', 'Invoice_Date',
       'Requisition_Vendor', 'Purchase_Organization', 'insert_date',
       'Invoice_Header', 'Invoice_Year', 'Invoice_Amount', 'Invoice_Vendor',
       'Invoice_Due_Date', 'Invoice_Vendor_City']]

    return(P2P_events)


if __name__ == "__main__":

    context = {'fileUploadName':'P2P.zip'}
    df = execute(context)
    df.to_csv('P2Peventlog.csv', index=None)