# Upgrading IBM Process Mining fomr 1.14.2 to 1.14.3 - Traditional Installation on RedHat 8 - Process and Task Mining on the Same Server

In this document, we install Process Mining and Task Mining on the same server. 

This installation process is for a POC, everything is installed as root, with no password in the database. You can follow the installation documentation to add more security.

Official installation process from the documentations: https://www.ibm.com/docs/en/process-mining/1.14.3?topic=installing-traditional-environments

Get the installation package using the part numbers mentionned in:
https://www.ibm.com/docs/en/process-mining/1.14.3?topic=installation-process-mining-packages

- M0GXPML for Process Mining
- M0GXQML for Task Mining

# Update Process Mining

Get the upgrade package from Passport Advantage, with this part number : M0GXPML
Extract ibmprocessmining-update-1.14.3_2e2b3127.tar.gz and upload it onto the VM.

Stop IBM Process Mining and nginx
```
export PM_HOME=/opt/processmining
$PM_HOME/bin/stop.sh
service nginx stop
```

```
cd /opt
tar xvf ibmprocessmining-update-1.14.3_2e2b3127.tar.gz
```

Backup configuration files (process mining and nginx)
```
cp $PM_HOME/etc/processmining.conf $PM_HOME/etc/processmining.conf.1.14.2
cp $PM_HOME/etc/accelerator-core.properties $PM_HOME/etc/accelerator-core.properties.1.14.2
cp /etc/nginx/conf.d/default.conf $PM_HOME/nginx/processmining.conf
cp /etc/nginx/conf.d/default.conf $PM_HOME/nginx/processmining.conf.1.14.2
```

Execute the upgrade script
```
cd /opt/processmining-update
./update.sh
```

The files that you edited for 1.14.2 are unchanged, and the update created new files flagged 1.14.3

Check these files:

- $PM_HOME/etc/accelerator-core-properties
- $PM_HOME/etc/processmining.conf
- $PM_HOME/nginx/processmining.conf


## $PM_HOME/etc/accelerator-core-properties

Check the differences between the 1.14.2 and the 1.14.3 versions

By default 1.14.3 should be usable as is 

Set accelerator-core.properties.1.14.3 as the current file
```
cp $PM_HOME/etc/accelerator-core.properties.1.14.3 $PM_HOME/etc/accelerator-core-properties
```

## $PM_HOME/etc/processmining.conf

Check the differences between $PM_HOME/etc/processmining.conf and $PM_HOME/etc/processmining.conf.1.14.3
```
diff $PM_HOME/etc/processmining.conf $PM_HOME/etc/processmining.conf.1.14.3
```

Any custom configuration you made (ex number of widgets, size of upload files, etc) should be changed in processmining.1.14.3.conf.

If you installed Task Mining, set the URL of task mining to be the URL of process mining (starting with https://)

```
vi $PM_HOME/etc/processmining.conf.1.14.3
```

Set the 1.14.3 version current
```
cp $PM_HOME/etc/processmining.conf.1.14.3 $PM_HOME/etc/processmining.conf
```

## $PM_HOME/nginx/processmining.conf

The nginx configuration file is typically copied as /etc/nginx/conf.d/default.conf

Check the differences between $PM_HOME/nginx/processmining.1.14.3 and /etc/nginx/conf.d/default.d 

There are a few changes. Best is to use 1.14.3 version and update the certificate names that you created. In this installation, we used server.pem and server.key

Edit $PM_HOME/nginx/processmining.1.14.3.conf and update the certificate names:
```
vi $PM_HOME/nginx/processmining.conf.1.14.3
```
Backup the 1.14.2 file and update nginx with the new 1.14.3 file
```
cp /etc/nginx/conf.d/default.conf $PM_HOME/nginx/processmining.conf.1.14.2
cp $PM_HOME/nginx/processmining.conf.1.14.3 /etc/nginx/conf.d/default.conf
cp $PM_HOME/nginx/processmining.conf.1.14.3 $PM_HOME/nginx/processmining.conf
```

## Process Mining Startup

Restart nginx
```
service nginx start
```

Start Process Mining
```
$PM_HOME/bin/start.sh
```

Note: if you still run version 1.14.2 (old UI), check in $PM_HOME/jetty*/webapps/ that you do not have any 1.14.2 files.

# Update Task Mining in the same server


Stop Process Mining (1.14.3), Task Mining (1.14.2), and nginx
```
export TM_HOME=/opt/taskminer
$PM_HOME/bin/stop.sh
$TM_HOME/bin/stop.sh
service nginx stop
```

Backup the task mining files that you customized in 1.14.2
```
cp /etc/nginx/conf.d/taskminer.conf $TM_HOME/conf/taskminer.conf.1.14.2
cp $TM_HOME/conf/taskminer.conf.1.14.2 $TM_HOME/conf/taskminer.conf
cp $TM_HOME/bin/environment.conf $TM_HOME/bin/environment.conf.1.14.2
```

Upload the taskminer update tar.gz file onto the process mining VM
```
cd /opt
tar xvf taskminer_update_1.14.3_719cc6d3.tar.gz
```

Run the installer script

```
cd /opt/taskmining-update
./update.sh
```

## Install PostgreSQL
With 1.14.3, we changed from mysql to postgres.

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
exit;
```

## Update $TM_HOME/bin/environment.conf
This file holds the database configuration for task mining.

```
vi $TM_HOME/bin/environment.conf
```
Replace with correct values (see doc: https://www.ibm.com/docs/en/process-mining/1.14.3?topic=optional-basic-setup)

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

Update permissions:
```
chmod +x ${TM_HOME}/tomcat/bin/*.sh
chmod +x ${TM_HOME}/bin/*.sh
chown -R taskminer:taskminer ${TM_HOME}/
```


## NGINX Configuration
nginx configuration file is unchanged between 1.14.2 and 1.14.3

Start nginx
```
service nginx start
```

Start process mining
```
$PM_HOME/bin/start.sh
```


## Task Mining Startup
In 1.14.2 we started several applications through a script. This is not needed in 1.14.3, we can remove this script.
```
rm $TM_HOME/bin/start.sh
rm $TM_HOME/bin/stop.sh
```

```
$TM_HOME/bin/tm-web.sh start
```

Note that at this stage all the task mining projects are empty. We need to migrate the data from mysql to postgresql.


## Migration script from MYSQL to PostgreSQL
Now that we have started Taskmining with PostgresQL, we can migrate existing TM data from mysql to posgresql.

The migration tool is available for IBMers at:
https://github.ibm.com/automation-base-pak/tm-utils/tree/main/tm-mysql-2-pgsql


```
sudo dnf install python3.8
yum install python3-devel postgresql-devel --nobest
pip3.8 install mysql-connector-python
pip3.8 install psycopg2-binary
```


Download config.py and tm-mysql-2-pgsql.py from https://github.ibm.com/automation-base-pak/tm-utils/tree/main/tm-mysql-2-pgsql

Update config.py to match your mysql and postgresql database values

If you installed 1.14.2 using these instructions in github, that should be:
```
#Licensed Materials - Property of IBM
#5900-AEO
#Copyright IBM Corp. 2023. All Rights Reserved.
#U.S. Government Users Restricted Rights:
#Use, duplication or disclosure restricted by GSA ADP Schedule
#Contract with IBM Corp.

mysql = dict(
  host="localhost",
  port="3306",
  user="taskminer",
  password="TaskMinerPwd01!",
  database="taskmining",
)
pgsql = dict(
  host="localhost",
  port="5432",
  user="taskminer",
  password="Tmppwd_1",
  database="pmdb",
  schema="taskminer"
)
```

Stop Task Mining
```
$TM_HOME/bin/tm-web.sh stop
```

Start the migration script
```
python3.8 ./tm-mysql-2-pgsql.py
```

Start Task Mining
```
$TM_HOME/bin/tm-web.sh start
```
