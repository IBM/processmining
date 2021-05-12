This dataset is very interesting as is inspired from the real CREDEM use case.
It shows clearly how we combine process mining and task mining to refine precisely the time spent on business activities, and how we can recommend BOTs based on automation goals and development complexity.


This example requires creating 1 parent process mining project, and up to 4 process mining projects for task mining.
Steps:
1. Download and unzip 'IBM - Bank Account Closure.zip'
1. Launch IBM Process Mining
1. Create a process mining project 'Bank Account Closure' in a dedicated organization 'myBank' where all the processes will be created.
1. In the Datasource tab, upload banking_account_closure_task_mining_edition.zip
1. From the top-right menu, select account/Manage history, upload the project backup: banking_account_closure_task_mining_edition_2020-10-23_071813.idp, and apply. This action maps the data and adds dashboards and project settings.
1. Visualize the process


The next steps can be repeated for each task mining process. Make sure you respect the naming.
1. Create a process mining project 'Task Mining: BO Service Closure' in 'myBank' organization
1. Upload task_mining_bo_service_closure.zip
1. Upload the project backup: Task Mining_ BO Service Closure_2021-03-15_100754.idp
1. Visualize the process


Do the same with the following datasets/projects
* task_mining_evaluat_request_with_registered_letter.zip / Task Mining_ Evaluating Request (WITH registered letter)_2021-03-15_100925.idp
* task_mining_network_service_closure.zip / Task Mining_ Network Service Closure_2021-03-15_101040.idp
* task_mining_pending_liquidation_request.zip / Task Mining_ Pending Liquidation Request_2021-03-15_101054.idp
* make sure you create the processes with the correct names:
   * Task Mining: Evaluating Request (WITH registered letter)
   * Task Mining: Network Service Closure
   * Task Mining: Pending Liquidation Request

## Bank Account Closure Durations
From the parent process, drill-down to the BO Service Closure activity process that results from task mining.
![](./Images/BankAccountClosure.png?sanitize=true)

## BO Service Closure generated from Task Mining
![](./Images/BOServiceClosure.png?sanitize=true)

## Discover actual working time spent on the BO Service Closure activity
![](./Images/BOServiceClosureTime.png?sanitize=true)

## Plan for RPA from recommendations
![](./Images/RPARecommendations.png?sanitize=true)
