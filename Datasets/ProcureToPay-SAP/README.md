This Procure To Pay dataset shows end-to-end P2P process built from four common SAP processes: Purchase Requisition, Purchase Order, Invoice, Good Receipt.
It demonstrates nicely how powerful the multi-level process capability of IBM Process Mining is. You will see that we are possibly using four process_id columns in the dataset, each column correspond to the ID of one of the four SAP processes involved in this end-to-end business process.
For example, when 3 goods are purchased in a single order, we keep seeing a single process.

Steps:
1. Download this ZIP and unzip:
1. Create a Process Mining project
1. Upload the data set from the Datasource tab: "p2p_automotive_As_Is.zip"
1. Upload the project backup "P2P - Automotive_2020-10-23_071252.idp" (see below how). The project backup does the mapping automatically, and load the P2P dashboards, KPIs, costs...
1. Visualize the process


Note: IBM can provide a Talend-based ETL project to produce this dataset from your own SAP system upon request, as an accelerator (contribution). Contact patrick.megard@fr.ibm.com

P2P Generated Model
![](./Images/P2PModel.png?sanitize=true)

P2P Conformance Checking
![](./Images/P2PConformanceChecking.png?sanitize=true)

Order Maverick (orders without requisition)
![](./Images/OrderMaverick.png?sanitize=true)

Spent Under Management
![](./Images/SpentUnderManagement.png?sanitize=true)
