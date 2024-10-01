# IBM Process Mining
IBM Process Mining assets are available to clients, partners, and IBMers.

## Process Apps
Process Apps can be developed by IBM, consultants, partners, and clients. They provide connectors, filters, KPIs, and dashboards that address a specific use case.
Don't hesitate to use pull requests if you want to contribute a process app useful to other process mining practitioners.

This repository contains process apps you can upload to your process mining environment.

Check the [list of available process apps](./Process%20Apps/README.md)

[BAW-IBM-Process-Mining-Assets](./Process%20Apps/BAW-IBM-Process-Mining-Assets/) contains the process app documented and supported in the product. I found several issues with clients using this connector/process app, I recommend using [BAW_connector](./BAW_connector/) instead.

## Use cases - Examples
Feel free to create process mining projects from these [examples](./Datasets_usecases/README.md), and to contribute new ones.

## Custom Accelerators (public)
Accelerators are programs used to create the event log from external data sources. They include the connection to the data source, the data transformation, and, optionally, the upload of the final CSV into a process mining project. Accelerators can be multi-threaded and can provide recovery mechanisms. They are helpful when large amounts of data requiring several hours of connection are collected.
- BAW Accelerator for BPM: [python](./BAW_connector/README.md)
- BAW Accelerator for Case (no code) : https://github.com/MalekJabri/BAWAccelerator

## Custom Accelerators (IBM consultants only)
These accelerators are available to IBMers only. 
- SAP AP, SAP P2P, SAP O2C with Talend: https://github.ibm.com/automation-base-pak/ibm-process-mining-etl/
- Maximo (contact laurence_may@uk.ibm.com)


## Installation scripts
Traditional installation of process mining and task mining on premises  [Installation scripts](./Installation_on_prem/README.md).
Following this script might accelerate the installation process for POCs. Note: this script is for version 1.14. Version 1.15 adds MonetDB for nextgen.

## REST APIs
[REST APIs](./REST%20APIs/) contains [IPMClient](./REST%20APIs/IPMClient/), a powerful python library that simplifies drastically the use of Process Mining REST API in a python program. Most REST APIs are implemented and you can easily request analytics results, create projects, upload data, create users, and many more, through a few python line of code.

## LLM
[LLM](./LLM/chat-with-api/) is an experiment from Emmanuel Tissandier, to interact with a bot that interprets your request using LLM, and call the appropriate action to provide you with the answer. This is an interesting example of using Process Mining REST API and LangChain.

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
