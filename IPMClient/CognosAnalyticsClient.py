# From CAFileUpload.py
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
# 1/4 Create or get (for update/append) the upload file object and grab the segment id
# 2/4 Upload file data
# 3/4 Upload end of file flag and grab the task id url
# 4/4 Check for file upload completion status using the task id

# python library imports
import requests, json, time, urllib3, sys
requests.packages.urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def cognosCreateCredentials(obj):
    if obj['CAMAPILoginKey'] != "":
        return {
            "parameters": [
                {
                    "name": "CAMAPILoginKey",
                    "value": obj['CAMAPILoginKey']
                }
            ]
        }
    else:
        return {
            "parameters": [
                {
                    "name": "CAMNamespace",
                    "value": obj["CAMNamespace"]
                },
                {
                    "name": "CAMUsername",
                    "value": obj["CAMUsername"]
                },
                {
                    "name": "CAMPassword",
                    "value":obj["CAMPassword"]
                }
            ]
        }

def cognosCreateSession(url, credentials, silent=False):
    if (not silent):
        print('Creating a session and grabbing session_key or XSRF token...')
    session = requests.Session()
    response = session.put(url + '/session', json=credentials)

    if (not response):
        print('error creating session...')
        print('response status code = {}'.format(response.status_code))
        print('displaying response and quitting...')
        print(response.text)
        return
    else:
        if (not silent):
            print('Session creation successful...')

    # test whether we're hitting Cognos 11.2 (session_key) or 11.1 (XSRF-Token cookie)
    json_response = response.json()
    if "session_key" in json_response:
        # Cognos 11.2 so we want to use session_key in all headers
        session_key = json_response["session_key"]
        return {'authkey': 'IBM-BA-Authorization',
                'authvalue': session_key}
    else:
        # Cognos 11.1.7 so we want to use XSRF-Token in all headers
        XSRFValue = session.cookies.get_dict()["XSRF-TOKEN"]
        return {'authkey': 'IBM-BA-Authorization',
                'authvalue': XSRFValue}

def cognosGetFiles(url, authkey, authvalue):
    url = url+'files'
    headers = {authkey: authvalue}

    r = requests.get(url, headers=headers, verify=False)
    if r.status_code == 200:
        return r.json()
    print("Cognos REST API Error %s: %s" % (url, r.status_code))
    return False

def cognosUploadFile(url, authkey, authvalue, filename, append=False, silent=False):
    # set up the upload file type and file open mode
    fileType = filename.split(".")[-1] 
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
        return

    # Search filename in existing contents
    files = cognosGetFiles(url, authkey, authvalue)['files']
    fileStoreID = 0
    for file in files:
        print(file['defaultName'])
        if file['defaultName'] == filename:
            fileStoreID = file['id']
            break

    # 1/4 Create new or get existing (for update/append) upload file object and grab the segment id
    if (fileStoreID == 0): 
        # creating new upload file (neither update nor append arguments used)
        if (not silent):
                print('1/4 Create the upload file object for the new upload file and grab the segment id...')

        # product will use default location of user's My Content
        data = '{"filename":"' + filename + '"}'

        if fileType == 'xlsx':
            uploadHeaders = {authkey: authvalue, "Content-Type": "application/json", "Accept-Encoding":"gzip, deflate"}
        else: 
            uploadHeaders = {authkey: authvalue, "Content-Type": "application/json"}
        uploadResponse = requests.post(url + '/files/import', headers=uploadHeaders, data = data)

        if (not uploadResponse):
            print('error uploading new file...')
            print('uploadResponse status code = {}'.format(uploadResponse.status_code))
            print('displaying uploadResponse and quitting...')
            print(uploadResponse.text)
            return
        else:
            if (not silent):
                print('File upload started ok...')

    else: # fileStoreID exists
        # doing an update or append to existing file rather than create new file
        if (not silent):
                print('1/4 Get the upload file object for existing upload file and grab the segment id...')

        uploadHeaders = {authkey: authvalue, "Content-Type": "application/json"}
        if (append):
            appendFlag = 'true'
        else:
            appendFlag = 'false'
        uploadResponse = requests.put(url + '/files/import/' + fileStoreID + '?append=' + appendFlag + '&filename=' + filename, headers=uploadHeaders)

        if (not uploadResponse):
            print('error uploading update/append file...')
            print('uploadResponse status code = {}'.format(uploadResponse.status_code))
            print('displaying uploadResponse and quitting...')
            print(uploadResponse.text)
            return
        else:
            if (not silent):
                print('file upload started ok...')

    # grab the segment/import path
    myImportPath = uploadResponse.json()['importPath']
    if (not silent):
        print('File upload: import path = {}'.format(myImportPath))

    # grab just the segment - from /files to the end 
    myEndpoint = myImportPath[7:]
    if (not silent):
        print('File upload: segment = {}'.format(myEndpoint))
        

    # step 2/4 Upload file data
    # NOTE: Optionally, the file data can be sent in multiple chunks, incrementing 
    #       the index by 1 on each subsequent send.  This script does not demonstrate this method.
    if (not silent):
            print('2/4 Upload file data...')
            print('reading local file {} for upload, may take some time...'.format(filename))

    with open(filename, mode=fileOpenMode) as file:
        myFileData = file.read()
    if (not silent):
            print('file read.  uploading file data...')
    uploadHeaders = {authkey: authvalue, "Content-Type": fileTypeContentType}
    uploadResponse = requests.put(url + myEndpoint + '?index=1', headers=uploadHeaders, data = myFileData)

    if (not uploadResponse):
        print('error uploading file data...')
        print('uploadResponse status code = {}'.format(uploadResponse.status_code))
        print('displaying uploadResponse and quitting...')
        print(uploadResponse.text)
        return
    else:
        if (not silent):
            print('file upload started ok...')
        

    # step 3/4 Upload end of file flag and grab the task id url...
    if (not silent):
            print('3/4 uploading end of file flag & grabbing task id...')

    uploadHeaders = {authkey: authvalue, "Content-Type": "text/csv"}

    uploadResponse = requests.put(url + myEndpoint + '?index=-1', headers=uploadHeaders)

    if (not uploadResponse):
        print('error uploading file data end of file flag...')
        print('uploadResponse status code = {}'.format(uploadResponse.status_code))
        print('displaying uploadResponse and quitting...')
        print(uploadResponse.text)
        return
    else:
        if (not silent):
            print('file upload started ok...')
            print('uploadResponse status code = {}'.format(uploadResponse.status_code))
            print(uploadResponse.text)
            print('uploadResponse = {}'.format(uploadResponse.json()))

    # grab the upload task id & url
    myHREF = uploadResponse.json()['href']
    if (not silent):
        print('task id url = {}'.format(myHREF))


    # step 4/4 Check for file upload completion using the task id...
    # note: response can include "state":"EXECUTING" and "state":"SUCCESS"
    if (not silent):
        print('4/4 checking for upload completion status...', end='', flush=True)

    getHeaders = {authkey: authvalue, "Content-Type": "text/csv"}

    while True: 
        getResponse = requests.get(url + '/files/import' + myHREF, headers=getHeaders)
        if (not getResponse):
            print('', flush=True)
            print('error uploading file, failed upload completion check...', flush=True)
            print('getResponse status code = {}'.format(getResponse.status_code))
            print('displaying getResponse and quitting...')
            print(getResponse.text)
            return
        else:
            if getResponse.json()['state'] == 'SUCCESS' :
                break
            else:
                if (not silent):
                    print('.', end='', flush=True)
                time.sleep(1)

    # all done
    if (not silent):
        print('', flush=True)
        print('file upload successful!  exiting...')


def main(argv):

    configFileName = './CognosA.json'
    with open(configFileName, 'r') as file:
        cognosConfig = json.load(file)
    

    credentials =  cognosCreateCredentials(cognosConfig['url'])    
    cognosAuth = cognosCreateSession(cognosConfig['url'], credentials=credentials)
    cognosUploadFile(cognosConfig['url'], cognosAuth['authkey'], cognosAuth['authvalue'], filename='data/CAtest1.csv', append=False, silent=False)


if __name__ == "__main__":
    main(sys.argv)