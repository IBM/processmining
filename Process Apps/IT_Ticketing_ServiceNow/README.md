# ServiceNow Ticketing Process App

Author: Patrick Megard, patrick.megard@fr.ibm.com

To create a process app, upload ```ServiceNowConnector.py```  in process app builder, and ```serviceNow1_2023-06-05_075444-0700.idp```  as a backup.

Note: So far, the connector has only be tested using the ServiceNow development trial instance that includes a few incidents. We need to access real systems to finalize the development.

## Service Now tables
The connector is fetching data using the ServiceNow REST API. The following tables are used:
- INCIDENT
- SYS_USER
- SYS_USER_GROUP
- SYS_AUDIT

The INCIDENT table returns a snapshot of each incident with the main possible incident statuses and dates (create, open, on hold, resolve, close).

When the AUDIT feature is enabled for the INCIDENT table, changes are logged. We are using these changes to add historical status changes that are not visible in INCIDENT, and to add ticket assignment changes. Additional changes could be added such as priority, category, etc.

## Process mining settings and dashboards
Due to the lack of data, we have not yet created specific filters and dashboards.



