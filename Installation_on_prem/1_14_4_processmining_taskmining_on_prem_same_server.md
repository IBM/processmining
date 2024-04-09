# Installation of IBM Process Mining 1.14.3 - Traditional Installation on RedHat 8 - Process and Task Mining on the Same Server

In this document, we install Process Mining and Task Mining on the same server. 

This installation process is for a POC, everything is installed as root, with no password in the database. You can follow the installation documentation to add more security.

Official installation process from the documentations: https://www.ibm.com/docs/en/process-mining/1.14.4?topic=installing-traditional-environments

Get the installation package using the part numbers mentionned in:
https://www.ibm.com/docs/en/process-mining/1.14.4?topic=installation-process-mining-packages

- M0GXPML for Process Mining
- M0GXQML for Task Mining

# Install Process Mining
## Install MongoDB 6.0 Community Edition
Instructions from https://www.mongodb.com/docs/v6.0/tutorial/install-mongodb-on-red-hat/#install-mongodb-community-edition


```
vi /etc/yum.repos.d/mongodb-org-6.0.repo
```
Copy this text into /etc/yum.repos.d/mongodb-org-6.0.repo
```
[mongodb-org-6.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/$releasever/mongodb-org/6.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-6.0.asc
```

Run the install
```
yum install -y mongodb-org
```

Start Mongo and check the status
```
systemctl start mongod
```

## Install IBM Process Mining
Get the package from Passport Advantage, with this part number : M0GXPML
Extract ibmprocessmining-setup-1.14.4_473401fb.tar.gz and upload it onto the VM.

```
cd /opt
tar xvf ibmprocessmining-setup-1.14.4_473401fb.tar.gz
export PM_HOME=/opt/processmining
```

In .bashrc, insert export PM_HOME=/opt/processmining

Update $PM_HOME/etc/processmining.conf to update Task Mining URL such that it is the URL of process mining.

```
vi $PM_HOME/etc/processmining.conf
```

## Install python 9
```
yum install python3.9
```


## Create Self Signed Certificates
If you have official certificates from your company, you should using them.

https://www.ibm.com/docs/docs/en/process-mining/1.14.4?topic=installation-self-certificates

```
    mkdir /opt/cert
    cd /opt/cert
    openssl genrsa -des3 -out rootCA.key 2048
    openssl req -x509 -new -nodes -key rootCA.key -sha256 -days 1024 -out rootCA.pem
```

Create a new file v3.ext
```
vi v3.ext
```
Add the following text to the file. Note that the DNS hostname wildcard should match your server hostname
```
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names
[alt_names]
DNS.1 = *.fyre.ibm.com
```

Create the certificates
```
openssl req -new -nodes -out server.csr -newkey rsa:2048 -keyout server.key
openssl x509 -req -in server.csr -CA rootCA.pem -CAkey rootCA.key -CAcreateserial -out server.crt -days 500 -sha256 -extfile v3.ext
cat server.crt server.key > server.pem
```
Install the rootCA in the keystore
```
$PM_HOME/jdk/linux/ibm-openjdk-semeru/bin/keytool -import -trustcacerts -alias "Process Mining CA" -file /opt/cert/rootCA.pem -keystore $PM_HOME/jdk/linux/ibm-openjdk-semeru/lib/security/cacerts -storepass changeit
```

Create keys for process apps
```
cd $PM_HOME/etc
openssl genrsa -out keypair-callsToAcf.pem 2048
openssl rsa -in keypair-callsToAcf.pem -outform DER -pubout -out acf-ext-publicKey.der
openssl pkcs8 -topk8 -nocrypt -in keypair-callsToAcf.pem -outform DER -out acf-core-privateKey.der
```

## Install NGINX

```
sudo yum update
sudo yum install nginx
```

Copy the virtual host file from the process mining installation into the nginx folder
```
cp $PM_HOME/nginx/processmining.conf /etc/nginx/conf.d/default.conf
```


Create the nginx ssl directory and copy the certificates from /opt/cert
```
mkdir /etc/nginx/ssl
cp /opt/cert/server.* /etc/nginx/ssl/.
```

Check if SELinux is enabled:
```
getenforce
```
I do not recommend to keep SELinux enforced as it also requires changes on the mongodb side. https://www.mongodb.com/docs/v4.4/tutorial/install-mongodb-on-red-hat/#configure-selinux

If SELinux is enabled:
```
chcon -t httpd_config_t /etc/nginx/ssl/*.*
```
or 
```
chcon -h system_u:object_r:ttpd_config_t /etc/nginx/ssl/server.*
```
And enable the connection from the network (when SELlinux is enforcing)
```
setsebool -P httpd_can_network_connect 1
```




Update the nginx config file to do the following:
- Replace certificate names
    - This vi command replaces mycomapny by server ```:%s/mycompany_com/server/```

```
vi /etc/nginx/conf.d/default.conf
```

Start nginx
```
systemctl enable nginx
systemctl start nginx
```


## Process Mining Startup

Create a start script
```
vi $PM_HOME/bin/start.sh
```
Include these lines:
```
/opt/processmining/bin/pm-web.sh start
/opt/processmining/bin/pm-engine.sh start
/opt/processmining/bin/pm-analytics.sh start
/opt/processmining/bin/pm-monitoring.sh start
/opt/processmining/bin/pm-accelerators.sh start
```
```
vi $PM_HOME/bin/stop.sh
```
Include these lines:
```
/opt/processmining/bin/pm-web.sh stop
/opt/processmining/bin/pm-engine.sh stop
/opt/processmining/bin/pm-analytics.sh stop
/opt/processmining/bin/pm-monitoring.sh stop
/opt/processmining/bin/pm-accelerators.sh stop
```

Make scripts executable
```
chmod +x $PM_HOME/bin/start.sh
chmod +x $PM_HOME/bin/stop.sh
```

Start Process Mining
```
$PM_HOME/bin/start.sh
```

Login to your process mining server
Default credentials:
- User: maintenance.admin
- Pswd: pmAdmin$1

New Password (choose your own) : IBMDem0s!

### Troubles accessing process mining?
If SELinux is enforced, mongodb is also having a problem. https://www.mongodb.com/docs/v4.4/tutorial/install-mongodb-on-red-hat/#configure-selinux

If possible, we recommend to disable SELinux dynamically ```setenforce 0``` or by editing ```/etc/selinux/config``` and rebooting.

```
grep -e "setroubleshoot" /var/log/messages
```

# Install Task Mining in the same server
Upload the taskminer tar.gz file onto the process mining VM
```
cd /opt
tar xvf taskminer_setup_1.14.4_1c78fcb0.tar.gz
export TM_HOME=/opt/taskminer
```

In .bashrc, insert export TM_HOME=/opt/taskminer

Create taskminer user
```
adduser taskminer
chown -R taskminer:taskminer $TM_HOME
chmod +x $TM_HOME/tomcat/bin/*.sh
chmod +x $TM_HOME/bin/*.sh
```


## Self-signed Certificates

Add the CA certificate that you created earlier, into the task mining jdk keystore:
```
$TM_HOME/ibm-openjdk-semeru/bin/keytool -import -keystore $TM_HOME/ibm-openjdk-semeru/lib/security/cacerts -trustcacerts -alias "Process Mining CA" -file /opt/cert/rootCA.pem
```
You can list the CA certificates registered in the keystore:
```
$TM_HOME/ibm-openjdk-semeru/bin/keytool -v -list -keystore $TM_HOME/ibm-openjdk-semeru/lib/security/cacerts | grep Process
```
You can delete a certificate registered in the keystore:
```
$TM_HOME/ibm-openjdk-semeru/bin/keytool -delete -noprompt -alias "Process Mining CA" -keystore $TM_HOME/ibm-openjdk-semeru/lib/security/cacerts
```


## NGINX Configuration

```
cp $TM_HOME/conf/taskminer.conf /etc/nginx/conf.d/taskminer.conf
vi /etc/nginx/conf.d/taskminer.conf
```
Edit taskminer.conf to set the correct values (replace <TM_HOST> with the server name (ex: process-miner.ibm.com) and <MY_CERTIFICATE>)
    - :%s/<MY_CERTIFICATE>/server/


## Task Mining Configuration
```
vi $TM_HOME/bin/environment.conf
```
Replace with correct values (see doc: https://www.ibm.com/docs/en/process-mining/1.14.4?topic=optional-basic-setup)

Example:
```
TM_HOME=/opt/taskminer

application_path=/opt/taskminer/data

#possible values are db2 | pgsql
TM_DB_TYPE=pgsql
TM_DB_HOST=localhost
#50000 for db2 | 5432 for pgsql
TM_DB_PORT=5432
TM_DB_NAME=pmdb
TM_DB_USERNAME=taskminer
TM_DB_PWD=Tmppwd_1
#only for db2 or pgsql
TM_DB_SCHEMA=taskminer
#only for db2 
TM_DB_USE_SSL=false


jwt_secret=0EC83CBA5CF1FE59A354E571BE539070AA9C7AB4E427112051CB2752ACD054CE
jwe_secret=30575D0353CF07AE2BB2D2449FFCED2DFD604FE1BB48213247292D737136BC86

# leave empty if you are doing a default installation with PM and TM on the same server
# otherwise, if PM is installed on a different server, fill this field with a complete url. 
# I.e. https://my-pm-server.domain.com
processmining_host=
```

Start nginx
```
service nginx start
```

## Install PostgreSQL
```
sudo dnf install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-8-x86_64/pgdg-redhat-repo-latest.noarch.rpm
sudo dnf -qy module disable postgresql
sudo dnf install -y postgresql15-server
sudo /usr/pgsql-15/bin/postgresql-15-setup initdb
sudo systemctl enable postgresql-15
sudo systemctl start postgresql-15
```

Create the taskminer user and the database pmdb
```
sudo -u postgres createuser taskminer
sudo -u postgres createdb pmdb
```
Open postgres psql (commands)
```
sudo -u postgres psql
```
Execute the following commands in psql:
```
alter user taskminer with encrypted password 'Tmppwd_1';
grant all privileges on database pmdb to taskminer;
```

## Update Process Mining configuration file
```
cd $PM_HOME/etc
vi processmining.conf
```
Search the instruction that starts with taskmining, and replace "" with the URL of process mining
```
taskmining : {
  url : "https://YOURPROCESSMINING.com" #Complete task mining url starting with https:// 
}
```

## Task Mining Startup
```
$TM_HOME/bin/tm-web.sh start
```

## Start process mining
Stop and restart nginx and process mining
```
$PM_HOME/bin/stop.sh
$PM_HOME/bin/start.sh
```

## login Task Mining web page
Since version 1.14.1, task mining web is only accessed via processmining web page.

https://PM_HOST/taskmining


# Tricks
## maintenance.admin password forgotten

When no email is in place, we can simulate that we received an email with a token.

Pre-requisite: Query the mongo database to get the accounts.

In mongo:
```
> use processmining
> db.accounts.find()
{ "_id" : ObjectId("64c1247d184bab5851f4df39"), "username" : "maintenance.admin", "email" : "maintenance.admin@mycompanydomain.com", "home" : "__maintenanceadmin", "groupId" : "-1", "firstName" : "Account", "lastName" : "Maintenance", "organization" : "processmining", "country" : "IT", "lastIP" : "127.0.0.1", "lastLogin" : ISODate("2023-09-14T12:26:55.004Z"), "created" : ISODate("2023-07-26T13:49:49.548Z"), "agentEnabled" : false, "active" : true, "tutorial" : true, "password" : "8888a8ebedd0ee4f810302708d609831de32dd3772e031b97f4c0e66b623ba8b57468c1d2de4d41e580687573efb6385", "passwordState" : "LOST_PASSWORD", "role" : "USER", "authToken" : "ng2spps94b6qhse13qqcdf8uho", "authTokenValidity" : ISODate("2023-09-14T12:35:46.500Z"), "projectLimit" : 1, "sessionLimit" : 2, "apiKey" : "k5siu71a93c61asf", "apiKeyEnabled" : true, "roles" : [ "ROLE_FREE_USER", "ROLE_USER", "ROLE_ADMIN" ], "permissions" : [ "PERM_EXPORT_BPMN", "PERM_ACTIVITY_MAP", "PERM_DASHBOARD", "PERM_USER_MANAGEMENT", "PERM_BPA", "PERM_ANALYTICS", "PERM_CONFORMANCE", "PERM_SOCIAL_NET" ], "permissionOverride" : [ ], "totpAuthEnabled" : false, "blocked" : false, "lockedSNA" : false, "passwordHistory" : [ "8888a8ebedd0ee4f810302708d609831de32dd3772e031b97f4c0e66b623ba8b57468c1d2de4d41e580687573efb6385" ], "lastPasswordUpdate" : ISODate("2023-09-14T12:26:37.863Z"), "applicationUser" : false, "lastModDate" : ISODate("2023-09-14T12:30:46.502Z"), "isProjected" : false, "_class" : "account" }
```

- Login as maintenance.admin
- Click 'Forgot your password?'
- Login as maintenance.admin, (enter), click reset

At this point you see the UI that requests the previous password, and that invite to create a new one.
Do nothing with that UI.

Call this URL
https:://<PM_HOST>/signin?emailResetPasswordSent=true&emailToken=true&resetPassword=LOST_PASSWORD&usr=maintenance.admin

The new UI requires you to enter a Token, and invite to create a new one.
You have 5 minutes...

```
> db.accounts.find()
{ "_id" : ObjectId("64c1247d184bab5851f4df39"), "username" : "maintenance.admin", "email" : "maintenance.admin@mycompanydomain.com", "home" : "__maintenanceadmin", "groupId" : "-1", "firstName" : "Account", "lastName" : "Maintenance", "organization" : "processmining", "country" : "IT", "lastIP" : "127.0.0.1", "lastLogin" : ISODate("2023-09-14T12:26:55.004Z"), "created" : ISODate("2023-07-26T13:49:49.548Z"), "agentEnabled" : false, "active" : true, "tutorial" : true, "password" : "8888a8ebedd0ee4f810302708d609831de32dd3772e031b97f4c0e66b623ba8b57468c1d2de4d41e580687573efb6385", "passwordState" : "LOST_PASSWORD", "role" : "USER", "authToken" : "ng2spps94b6qhse13qqcdf8uho", "authTokenValidity" : ISODate("2023-09-14T12:35:46.500Z"), "projectLimit" : 1, "sessionLimit" : 2, "apiKey" : "k5siu71a93c61asf", "apiKeyEnabled" : true, "roles" : [ "ROLE_FREE_USER", "ROLE_USER", "ROLE_ADMIN" ], "permissions" : [ "PERM_EXPORT_BPMN", "PERM_ACTIVITY_MAP", "PERM_DASHBOARD", "PERM_USER_MANAGEMENT", "PERM_BPA", "PERM_ANALYTICS", "PERM_CONFORMANCE", "PERM_SOCIAL_NET" ], "permissionOverride" : [ ], "totpAuthEnabled" : false, "blocked" : false, "lockedSNA" : false, "passwordHistory" : [ "8888a8ebedd0ee4f810302708d609831de32dd3772e031b97f4c0e66b623ba8b57468c1d2de4d41e580687573efb6385" ], "lastPasswordUpdate" : ISODate("2023-09-14T12:26:37.863Z"), "applicationUser" : false, "lastModDate" : ISODate("2023-09-14T12:30:46.502Z"), "isProjected" : false, "_class" : "account" }
```

Copy the authToken and enter the token in the UI, then create the new password.
You are done.

