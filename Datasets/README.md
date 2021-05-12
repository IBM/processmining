# Use Cases and Datasets
The following use cases are provided with a sample dataset, and with a project backup (.IDP) that includes dashboards, KPIs, costs, and other process settings.

* [Procure to Pay](https://github.com/IBM/processmining/tree/main/Datasets/ProcureToPay-SAP). This sample shows the exclusive multi-level process capability of IBM Process Mining. It leverages events from 4 distinct SAP processes merged into a single end-to-end P2P case.
* [Order to Cash](https://github.com/IBM/processmining/tree/main/Datasets/OrderToCash-SAP). Shows the end-to-end order to cash process from SAP data
* [Banking Account Closure](https://github.com/IBM/processmining/tree/main/Datasets/BankingAccountClosure). Demonstrate the combination of process mining and task mining to get finer details on business activities, and to recommend best RPA investments to simulate.

## Loading project backup files (.IDP)
Each dataset is provided with a process mining project backup file (.IDP).
1. Upload the event log file (CSV). Do not do the mapping
1. From the top-right menu, select 'Manage History', load the IDP file and apply. This step will automatically map the fields, update the project settings, load the dashboards and the reference model.

![](./images/ManageHistory.png?sanitize=true)
