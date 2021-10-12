# IBM Process Mining - Export dashboard data

The sample application will execute the Analytics dashboards marked as "exportable" and outputs their results to server-side configured S3 bucket.

Usage example:
java -DserverUrl=<process_mining_url> -DuserId=<user_id> -DapiKey=<api_key> -jar dashboard-export-job-1.0-SNAPSHOT.jar <process_id> <organisation_id> <path_to_filters_json>
