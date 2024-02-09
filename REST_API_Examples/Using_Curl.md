# EXAMPLES OF REST API CALLS USING CURL

Replace the elements like <THIS> with your values

You fist need to get a signature:
```
curl -X POST -k '<URL>/integration/sign' -H "Content-Type: application/json"  --data '{"uid" : "<USER>", "apiKey" : "<APIKEY>"}'
``` 
returns a key = <KEY> that you use in the other calls

## Uploading an event log
Upload CSV into a project
```
curl -k -X POST '<URL>/integration/csv/<PROJECT>/upload?org=<ORG>' -F file=@<FILE>.zip  -H "accept: application/json" -H "Authorization: Bearer <KEY>"
```
returns a job = <JOB>

You need to wait until the <JOB> is complete:
```
curl -k '<URL>/integration/csv/job-status/<JOB>' -H "accept: application/json" -H "Authorization: Bearer <KEY>"
```

Then 'refresh' the event log
```
curl -k -X POST '<URL>/integration/csv/<PROJECT>/create-log?org=<ORG>' -H "accept: application/json" -H "Authorization: Bearer <KEY>"
```
returns a job = <JOB>

loop/wait </JOB> until the job is complete
```
curl -k '<URL>/integration/csv/job-status/<JOB>' -H "accept: application/json" -H "Authorization: Bearer <KEY>"
```

## Querying data from the event log
```
curl -k -X POST '<URL>/analytics/integration/newbawextract/query?org=ca2b2685' -H "Authorization: Bearer <KEY>" --header 'Content-Type: application/x-www-form-urlencoded' --data-urlencode 'params={ "query": "SELECT count(*) FROM EVENTLOG" }' 
```

## Trimming events (using Bank Account Closure)

Replace <URL>, <UID>, <APIKEY>, <ORG>
And <KEY> returned by the command below:
curl -X POST -k '<URL>/integration/sign' -H "Content-Type: application/json"  --data '{"uid" : "<UID>", "apiKey" : "<APIKEY>"}'
 
 
curl -k -X POST ‘<URL>/integration/csv/bank-account-closure/trimming?org=<ORG>' -H "Authorization: Bearer <KEY>" --header 'Content-Type: application/json' --data '{"caseFilters": [{"filterType": "attribute","attributeKey": "attr-CLOSURE_TYPE","attributeValue": "Client Recess"}]}'