# IBM Process Mining
IBM Process Mining assets available to clients, partners, and IBMers.

## Process Apps
Process Apps can be developed by IBM, consultants, partners, clients. They provide connectors, filters, kpis, dashboards that address a specific use case.
If you want to contribute a process app that would be useful to other process mining practitionners, don't hesitate to use pull requests.

This repository contains process apps that you can upload in your process mining environment.

Check the [list of available process apps](./Process%20Apps/README.md)

## Use cases - Examples
Feel free to create process mining projects from these [examples](./Datasets_usecases/README.md)

## Custom Accelerators (public)
Accelerators are programs used to create the event-log from external data sources. They include the connection to the datasource, the data transformation, and optionally the upload of the final CSV into a process mining project. Accelerators can be multi-threaded, and can provide recovery mechanisms. They are useful when huge data requiring several hours of connection are collected.
- BAW Accelerator for BPM (no code) : https://github.com/IBM/ibm-process-mining-BAW-accelerator
- BAW Accelerator for Case (no code) : https://github.com/MalekJabri/BAWAccelerator

## Custom Accelerators (IBM consultants only)
These accelerators are available to IBMers only. 
- SAP AP, SAP P2P, SAP O2C with Talend: https://github.ibm.com/automation-base-pak/ibm-process-mining-etl/
- Maximo (contact laurence_may@uk.ibm.com)


## Installation scripts
Traditional installation of process mining and task mining on premises  [Installation scripts](./Installation_on_prem/README.md).
Following this script might accelerate the installation process for POCs. 

# IBM Process Mining Technical Assets
These assets illustrate how IBM Process Mining components can be customized by javascript developers.

## Custom Metrics (javascript)
Custom metrics are developed in Javascript to create case-level metrics from the events data in each case.
Examples of custom metrics: [Custom Metrics](./Custom%20Metrics/)
## Custom Filters (javascript)
Custom filters are developed in Javascript to create sophisticated filters from the events data in each case.
Examples of custom filters:  [Custom Filters](./Custom%20Filters/)
## Custom Widgets (javascript)
Custom widgets are developed in Javascript to add new widgets in dashboards.
Examples of custom widgets:  [Custom Widgets](./Custom%20Widgets/)

Read this [tutorial](./Custom%20Widgets/dimension_linechart/README.md) to learn how to create advanced custom widgets with charts, that could be useful in any project.
