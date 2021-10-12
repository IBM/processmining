# IBM Process Mining
API client samples

## CSV data trimming

The sample application will trim a process' data chunks, based of the case and entity filters specified in the input JSON.

Usage example:

java -DserverUrl=<process_mining_url> -DuserId=<user_id> -DapiKey=<api_key> -jar csv-trimming-job-1.0-SNAPSHOT.jar <process_id> <organisation_id> <path_to_filters_json>
