# IBM Process Mining
API client samples

## Export dashboard data

The exporting of Analytics' dashboard results as CSV to an external S3 storage is a new capability introduced with the 1.12.0 release.

The pre-requisites of using this capability are:
- the S3 storage tier to be set up in the Process Mining server configuration
- dashboards to be marked as "exportable" in their "Dashboard info" panel in the Analytics platform.

Usage example:

java -DserverUrl=<process_mining_analytics_url> -DuserId=<user_id> -DapiKey=<api_key> -jar dashboard-export-job-1.0-SNAPSHOT.jar <process_id> <organisation_id> <path_to_filters_json>
