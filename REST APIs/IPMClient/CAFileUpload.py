# CAFileUpload.py
# Copyright 2023 IBM
#
# NOTE: FOR SAMPLE PURPOSES ONLY, NOT FOR PRODUCTION USE.  ENSURE CONTENT 
#       STORE BACKUPS IN PLACE BEFORE USING.
#
# Sample python script to upload a file to IBM Cognos Analytics 11.2+ using the REST API.
# Developed and tested with Python 3 and IBM Cognos Analytics 11.2.4 uploading CSV text 
# files < 100MB in size.  Backwards support for 11.1.7.
# Supports 11.2.4 API key (in addition to standard password credentials).  
#   NOTE: When using API key be sure to first Renew Credentials in Cognos UI > 
#   Personal menu > Profile > Advanced options > Credentials > Renew User 
#   Profile.
# Supports upload new file, update (overwrite) existing upload file or append existing upload file.
# Supports .csv, .xls and .xlsx files per Uploaded Files documentation:
# csv - text/csv
# xls - application/vnd.ms-excel
# xlsx - application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
#
# Limitations of this sample script:
# - only target file storeID (not path) supported for exact match on update/
#   append existing files.  script can also match non-unique filename but
#   not recommended as this method uses an open query of all upload files.
# - calls through a load balancer (also needs X-CA-Affinity in the header)
#
# STEPS:
# 1/5 Create a session and grab the session_key (11.2) or xsrf token (11.1)
# 2/5 Create or get (for update/append) the upload file object and grab the segment id
# 3/5 Upload file data
# 4/5 Upload end of file flag and grab the task id url
# 5/5 Check for file upload completion status using the task id

# python library imports
import argparse, requests, json, time, sys

# set up exit error codes
ERR_FAILED_SESSION = 116
ERR_FAILED_UPLOAD = 117
ERR_UNSUPPORTED_FILETYPE = 118

# set up command-line arguments and help
parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,description="Sample IBM Cognos Analytics REST API file upload script. NOT FOR PRODUCTION USE.  See script comments for full documentation.",epilog="To run, update the default values in the script (displayed here in help) and/or pass values as command-line arguments.\n\nexample calls:\n  python3 CAFileUpload.py myfile.csv  // upload new upload file to default location using url and credential default values in script\n  python3 CAFileUpload.py -url \"http://myserver:myport/api/v1\" -n \"mynamespaceid\" -u \"myuser\" -p \"mypassword\" -d \"i6EB9D205C24A480D95CDEB77D4928465\" myfile.csv  // upload new upload file using command-line arguments for destination folder, url and credentials\n  python3 CAFileUpload.py -a \"i6EB9D205C24A480D95CDEB77D4928465\" myfile.csv  // append rows to existing upload file using default url and credentials from script\n  python3 CAFileUpload.py -up \"i6EB9D205C24A480D95CDEB77D4928465\" myfile.csv  // update (ie overwrite) existing upload file using default url and credentials from script")
parser.add_argument('-url', '--url', help=': ibm cognos rest api url - eg http://server:port/api/v1', default='http://myserver:myport/api/v1')
parser.add_argument('-n', '--namespace_id', help=': namespace id as it appears in cognos configuration - NOTE: NOT the namespace name', default='mynamespaceid')
parser.add_argument('-u', '--username', help=': user name', default='myuser')
parser.add_argument('-p', '--password', help=': user password', default='mypassword')
parser.add_argument('-apikey', '--apikey', help=': user api key (11.2.4+). NOTE: remember to Renew Credentials before using new api keys.', default='myapikey')
parser.add_argument('filename', help=': filename of the upload file - supports .csv, .xls and .xlsx - eg myfile.csv')
group = parser.add_mutually_exclusive_group()
group.add_argument('-d', '--destination', help=': destination folder storeID or path for new upload files. optional as product default location is user My Content folder. note: include quotes around the value like: -d "i6EB9D205C24A480D95CDEB77D4928465" or -d "/content/folder[@name=\'Upload Files\']"')
group.add_argument('-up', '--update', help=': update (ie overwrite) existing upload file. specify target update file Content Store storeID for exact unique match or use keyword "match" for non-unique filename match against query of all upload files (not recommended).  eg -up "i6EB9D205C24A480D95CDEB77D4928465" or -up "match".')
group.add_argument('-a', '--append', help=': append rows to existing upload file. specify target append file Content Store storeID for exact unique match or use keyword "match" for non-unique filename match against query of all files (not recommended). eg -a "i6EB9D205C24A480D95CDEB77D4928465" or -a "match".')
parser.add_argument('-s', '--silent', help=': silent mode - do not display progress messages', action="store_true")
args = parser.parse_args()

# set up the credentials object
if args.apikey != "myapikey":
    credentials = {
        "parameters": [
        {
            "name": "CAMAPILoginKey",
            "value": args.apikey
        }
        ]
    }
else:
    credentials = {
        "parameters": [
        {
            "name": "CAMNamespace",
            "value": args.namespace_id
        },
        {
            "name": "CAMUsername",
            "value": args.username
        },
        {
            "name": "CAMPassword",
            "value":args.password
        }
        ]
    }

# set up the upload file type and file open mode
fileType = args.filename.split(".")[-1] 
if fileType == 'csv': 
    fileTypeContentType = 'text/csv'
    fileOpenMode = 'r'
elif fileType == 'xls':
    fileTypeContentType = 'application/vnd.ms-excel' 
    fileOpenMode = 'rb'   
elif fileType == 'xlsx':
    fileTypeContentType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    fileOpenMode = 'rb'
else:
    print('error unsupported upload file type...')
    print('supported upload file types include: csv, xls and xlsx')
    print('quitting...')
    sys.exit(ERR_UNSUPPORTED_FILETYPE)


# step 1/5 create a session and grab the session_key (11.2) or xsrf token (11.1)
if (not args.silent):
        print('1/5 Creating a session and grabbing session_key or XSRF token...')
session = requests.Session()
response = session.put(args.url + '/session', json=credentials)
if (not response):
    print('error creating session...')
    print('response status code = {}'.format(response.status_code))
    print('displaying response and quitting...')
    print(response.text)
    sys.exit(ERR_FAILED_SESSION)
else:
    if (not args.silent):
        print('Session creation successful...')

# test whether we're hitting Cognos 11.2 (session_key) or 11.1 (XSRF-Token cookie)
json_response = response.json()
if "session_key" in json_response:
    # Cognos 11.2 so we want to use session_key in all headers
    session_key = json_response["session_key"]
    authkey = "IBM-BA-Authorization"
    authvalue = session_key
    if (not args.silent):
        print('Cognos 11.2 so using session_key in headers...')
else:
    # Cognos 11.1.7 so we want to use XSRF-Token in all headers
    cog_version = 111
    XSRFValue = session.cookies.get_dict()["XSRF-TOKEN"]
    authkey = "X-XSRF-Token"
    authvalue = XSRFValue
    if (not args.silent):
        print('Cognos 11.1 so using XSRF-Token in headers...')


# 2/5 Create new or get existing (for update/append) upload file object and grab the segment id
if (args.update is None and args.append is None): 
    # creating new upload file (neither update nor append arguments used)
    if (not args.silent):
            print('2/5 Create the upload file object for the new upload file and grab the segment id...')

    if (args.destination is not None):
        myData = '{"filename":"' + args.filename + '", "destination":"' + args.destination + '"}'
    else:
        # product will use default location of user's My Content
        myData = '{"filename":"' + args.filename + '"}'

    if fileType == 'xlsx':
        uploadHeaders = {authkey: authvalue, "Content-Type": "application/json", "Accept-Encoding":"gzip, deflate"}
    else: 
        uploadHeaders = {authkey: authvalue, "Content-Type": "application/json"}
    uploadResponse = session.post(args.url + '/files/import', headers=uploadHeaders, data = myData)

    if (not uploadResponse):
        print('error uploading new file...')
        print('uploadResponse status code = {}'.format(uploadResponse.status_code))
        print('displaying uploadResponse and quitting...')
        print(uploadResponse.text)
        sys.exit(ERR_FAILED_UPLOAD)
    else:
        if (not args.silent):
            print('File upload started ok...')

else:
    # doing an update or append to existing file rather than create new file
    if (not args.silent):
            print('2/5 Get the upload file object for existing upload file and grab the segment id...')

    if (args.update is not None and not args.update == "match"):
        # update target file storeID provided
        fileStoreID = args.update
    else:
        if (args.append is not None and not args.append == "match"):
            # append target file storeID provided
            fileStoreID = args.append
        else:
            # target file storeID not provided, so doing a non-unique match on filename against query of all upload files
            getHeaders = {authkey: authvalue}
            response = session.get(args.url + '/files', headers=getHeaders)

            if (not response):
                print('error getting needed list of uploaded files...')
                print('response status code = {}'.format(response.status_code))
                print('displaying response and quitting...')
                print(response.text)
                sys.exit(ERR_FAILED_UPLOAD)
            else:
                if (not args.silent):
                    print('got list of uploaded files ok...')

            # grab the storeID of the target file
            match = next(d for d in response.json()['files'] if d['defaultName'] == args.filename)
            fileStoreID = match["id"]
    
    if (not args.silent):
        print('{} storeID = {}'.format(args.filename, fileStoreID))

    uploadHeaders = {authkey: authvalue, "Content-Type": "application/json"}
    if (args.append is not None):
        appendFlag = 'true'
    else:
        appendFlag = 'false'
    uploadResponse = session.put(args.url + '/files/import/' + fileStoreID + '?append=' + appendFlag + '&filename=' + args.filename, headers=uploadHeaders)

    if (not uploadResponse):
        print('error uploading update/append file...')
        print('uploadResponse status code = {}'.format(uploadResponse.status_code))
        print('displaying uploadResponse and quitting...')
        print(uploadResponse.text)
        sys.exit(ERR_FAILED_UPLOAD)
    else:
        if (not args.silent):
            print('file upload started ok...')

# grab the segment/import path
myImportPath = uploadResponse.json()['importPath']
if (not args.silent):
    print('File upload: import path = {}'.format(myImportPath))

# grab just the segment - from /files to the end 
myEndpoint = myImportPath[7:]
if (not args.silent):
    print('File upload: segment = {}'.format(myEndpoint))
    

# step 3/5 Upload file data
# NOTE: Optionally, the file data can be sent in multiple chunks, incrementing 
#       the index by 1 on each subsequent send.  This script does not demonstrate this method.
if (not args.silent):
        print('3/5 Upload file data...')
        print('reading local file {} for upload, may take some time...'.format(args.filename))

with open(args.filename, mode=fileOpenMode) as file:
    myFileData = file.read()
if (not args.silent):
        print('file read.  uploading file data...')
uploadHeaders = {authkey: authvalue, "Content-Type": fileTypeContentType}
uploadResponse = session.put(args.url + myEndpoint + '?index=1', headers=uploadHeaders, data = myFileData)

if (not uploadResponse):
    print('error uploading file data...')
    print('uploadResponse status code = {}'.format(uploadResponse.status_code))
    print('displaying uploadResponse and quitting...')
    print(uploadResponse.text)
    sys.exit(ERR_FAILED_UPLOAD)
else:
    if (not args.silent):
        print('file upload started ok...')
    

# step 4/5 Upload end of file flag and grab the task id url...
if (not args.silent):
        print('4/5 uploading end of file flag & grabbing task id...')

uploadHeaders = {authkey: authvalue, "Content-Type": "text/csv"}

uploadResponse = session.put(args.url + myEndpoint + '?index=-1', headers=uploadHeaders)

if (not uploadResponse):
    print('error uploading file data end of file flag...')
    print('uploadResponse status code = {}'.format(uploadResponse.status_code))
    print('displaying uploadResponse and quitting...')
    print(uploadResponse.text)
    sys.exit(ERR_FAILED_UPLOAD)
else:
    if (not args.silent):
        print('file upload started ok...')
        print('uploadResponse status code = {}'.format(uploadResponse.status_code))
        print(uploadResponse.text)
        print('uploadResponse = {}'.format(uploadResponse.json()))

# grab the upload task id & url
myHREF = uploadResponse.json()['href']
if (not args.silent):
    print('task id url = {}'.format(myHREF))


# step 5/5 Check for file upload completion using the task id...
# note: response can include "state":"EXECUTING" and "state":"SUCCESS"
if (not args.silent):
    print('5/5 checking for upload completion status...', end='', flush=True)

getHeaders = {authkey: authvalue, "Content-Type": "text/csv"}

while True: 
    getResponse = session.get(args.url + '/files/import' + myHREF, headers=getHeaders)
    if (not getResponse):
        print('', flush=True)
        print('error uploading file, failed upload completion check...', flush=True)
        print('getResponse status code = {}'.format(getResponse.status_code))
        print('displaying getResponse and quitting...')
        print(getResponse.text)
        sys.exit(ERR_FAILED_UPLOAD)

    else:
        if getResponse.json()['state'] == 'SUCCESS' :
            break
        else:
            if (not args.silent):
                print('.', end='', flush=True)
            time.sleep(1)

# all done
if (not args.silent):
    print('', flush=True)
    print('file upload successful!  exiting...')
sys.exit(0)