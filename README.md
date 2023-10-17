# IBM Process Mining
IBM Process Mining assets are available to clients, partners, and IBMers.

## Process Apps
Process Apps can be developed by IBM, consultants, partners, and clients. They provide connectors, filters, KPIs, and dashboards that address a specific use case.
Don't hesitate to use pull requests if you want to contribute a process app useful to other process mining practitioners.

This repository contains process apps you can upload to your process mining environment.

Check the [list of available process apps](./Process%20Apps/README.md)

## Use cases - Examples
Feel free to create process mining projects from these [examples](./Datasets_usecases/README.md)

## Custom Accelerators (public)
Accelerators are programs used to create the event log from external data sources. They include the connection to the data source, the data transformation, and, optionally, the upload of the final CSV into a process mining project. Accelerators can be multi-threaded and can provide recovery mechanisms. They are helpful when large amounts of data requiring several hours of connection are collected.
- BAW Accelerator for BPM (no code) : https://github.com/IBM/ibm-process-mining-BAW-accelerator
- BAW Accelerator for Case (no code) : https://github.com/MalekJabri/BAWAccelerator

## Custom Accelerators (IBM consultants only)
These accelerators are available to IBMers only. 
- SAP AP, SAP P2P, SAP O2C with Talend: https://github.ibm.com/automation-base-pak/ibm-process-mining-etl/
- Maximo (contact laurence_may@uk.ibm.com)


## Installation scripts
Traditional installation of process mining and task mining on premises  [Installation scripts](./Installation_on_prem/README.md).
Following this script might accelerate the installation process for POCs. 

## Hands-on Labs

IBM Processes Mining and Task Mining hands-on labs are updated to work with every major release. Click [here](https://ibm.box.com/v/PROC-TASK-MINING-LABS-1-14) to download the labs. The labs were designed to run as-is on the IBM Tech Zone Environment (current version 1.14.1), which includes Process Mining, Task Mining, and Task Mining Client VMs, and it is available to IBMers and IBM Business Partners. Click [here](https://techzone.ibm.com/collection/process-mining-with-task-mining-demo-and-etl) to access the Tech Zone Environment.

For questions regarding the labs or the Tech Zone Environment, contact pacholsk@calibm.com

# IBM Process Mining Technical Assets
These assets illustrate how JavaScript developers can customize IBM Process Mining components.

## Custom Metrics (JavaScript)
Custom metrics are developed in JavaScript to create case-level metrics from the events data in each case.
Examples of custom metrics: [Custom Metrics](./Custom%20Metrics/)

## Custom Filters (JavaScript)
Custom filters are developed in JavaScript to create sophisticated filters from the event data in each case.
Examples of custom filters:  [Custom Filters](./Custom%20Filters/)

## Custom Widgets (JavaScript)
Custom widgets are developed in JavaScript to add new widgets in dashboards.
Examples of custom widgets:  [Custom Widgets](./Custom%20Widgets/)

Read this [tutorial](./Custom%20Widgets/dimension_linechart/README.md) to learn how to create advanced custom widgets with charts, that could be useful in any project.
