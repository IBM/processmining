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

## Trimming events
```
curl -X POST -k 'https://pharoses1.fyre.ibm.com/integration/sign' -H "Content-Type: application/json"  --data '{"uid" : "task.miner", "apiKey" : "8a5kga87eqvd1180"}'

curl -k -X POST 'https://pharoses1.fyre.ibm.com/integration/csv/bank-account-closure/trimming?org=79f81e76' -H "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0YXNrLm1pbmVyIiwiaWF0IjoxNjk2NDkzMTUwLCJleHAiOjE2OTY0OTQ5NTB9.dkBqkR5h3cV--2hgAwZigklbDHSJmr3D9dSL4ZL_6P8" --header 'Content-Type: application/json' --data '{"caseFilters": [{"filterType": "attribute","attributeKey": "attr-CLOSURE_TYPE","attributeValue": "Client Recess"}]}' 
```

## Trimming events https://pm-sprint-process-miner.fyre.ibm.com

curl -X POST -k 'https://pm-sprint-process-miner.fyre.ibm.com/integration/sign' -H "Content-Type: application/json"  --data '{"uid" : "patrick.megard@fr.ibm.com", "apiKey" : "q2niejpujt1q82as"}'

curl -k -X POST 'https://pm-sprint-process-miner.fyre.ibm.com/integration/csv/bank-account-closure/trimming?org=4dbf178d' -H "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJwYXRyaWNrLm1lZ2FyZEBmci5pYm0uY29tIiwiaWF0IjoxNjk2NTA4OTQxLCJleHAiOjE2OTY1MTA3NDF9.oqoOB96GQScuR0CojHxHMTbbHsDycetKabx7dmji5yo" --header 'Content-Type: application/json' --data '{“caseFilters”: [{“filterType”: “aggregate”,“expression”: “(not 0)“,“filters”: [{“filterType”: “attribute”,“attributeKey”: “attr-CLOSURE_TYPE”,“attributeValue”: “Client Recess”}]}],“entityFilters”: []}'
```

## Trimming events from OCP https://cpd-cp4ba-starter.apps.ocp-663002aumg-8m0f.cloud.techzone.ibm.com/processmining/

curl -X POST -k 'https://pm-pm-cp4ba-starter.apps.ocp-663002aumg-8m0f.cloud.techzone.ibm.com/processmining/sign' -H "Content-Type: application/json"  --data '{"uid" : "cp4admin", "apiKey" : "c45jah8mk40ll395"}'

curl -X POST -k 'https://useast.techzone-services.com:25403/integration/sign' -H "Content-Type: application/json"  --data '{"uid" : "maintenance.admin", "apiKey" : "k0rea0pg4c6ro2nq"}'


## Filenet graphql

curl -k -X -POST  'https://fncm-dev-demo-emea-10.automationcloud.ibm.com.com/oidc/endpoint/ums/token' -u "customApp:passw0rd" -d "grant_type=password&scope=openid&username=patrick.megard@fr.ibm.com&password=PatUrxing#me23!"


curl -k -X POST 'https://pharoses1.fyre.ibm.com/analytics/integration/bank-account-closure/query?org=79f81e76' -H "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0YXNrLm1pbmVyIiwiaWF0IjoxNzE1Nzc0NDcyLCJleHAiOjE3MTU3NzYyNzJ9.OtnGiFZ3cOpQZV3O8Db74mUJuceOcYRU1s0Akirf6wI" --header 'Content-Type: application/x-www-form-urlencoded' --data-urlencode 'params={ "query": "SELECT count(*) FROM EVENTLOG" }' 

curl -X POST -k 'https://pharoses1.fyre.ibm.com/integration/sign' -H "Content-Type: application/json"  --data '{"uid" : "task.miner", "apiKey" : "8a5kga87eqvd1180"}'

curl -k -X GET 'https://pharoses1.fyre.ibm.com/integration/processes/bank-account-closure/project-settings/activities-cost?org=79f81e76' -H "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0YXNrLm1pbmVyIiwiaWF0IjoxNzE1ODQ5MjUzLCJleHAiOjE3MTU4NTEwNTN9.4dv3eyv2Tj88IGKw7zNEWp-gFkEtFd4EqSK58fRNfSw" --header 'Content-Type: application/json'

curl -k -X GET 'https://pharoses1.fyre.ibm.com/integration/processes/bank-account-closure/project-settings/activities-cost/Request+created?org=79f81e76' -H "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0YXNrLm1pbmVyIiwiaWF0IjoxNzE1ODQ5MjUzLCJleHAiOjE3MTU4NTEwNTN9.4dv3eyv2Tj88IGKw7zNEWp-gFkEtFd4EqSK58fRNfSw" --header 'Content-Type: application/json'

curl -k -X GET 'https://useast.services.cloud.techzone.ibm.com:27464/integration/user-management/integration/organizations' -H "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJtYWludGVuYW5jZS5hZG1pbiIsImlhdCI6MTcxNjM5Mjc4MCwiZXhwIjoxNzE2Mzk0NTgwfQ.vkr0AexzgdUhvPhSQPKsiRtGdSdkmQil3NJOndC4abQ" --header 'Content-Type: application/json'

curl -X POST -k 'https://useast.services.cloud.techzone.ibm.com:27464/integration/sign' -H "Content-Type: application/json"  --data '{"uid" : "maintenance.admin", "apiKey" : "k0rea0pg4c6ro2nq"}'
