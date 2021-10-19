# IBM Process Mining
API client samples

## CSV data trimming

Data trimming is the capability introduced in the 1.12.0 release, that would truncate a process' data source by retaining only the cases that satisfy the filter conditions specified in the input JSON.

Usage example:

java -DserverUrl=<process_mining_url> -DuserId=<user_id> -DapiKey=<api_key> -jar csv-trimming-job-1.0-SNAPSHOT.jar <process_id> <organisation_id> <path_to_filters_json>
