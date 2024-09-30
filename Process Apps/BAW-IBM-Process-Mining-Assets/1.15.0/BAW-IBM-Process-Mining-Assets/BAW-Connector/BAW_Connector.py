"""
IBM Confidential
OCO Source Materials
5900-AEO
Copyright IBM Corp. 2024.
The source code for this program is not published or otherwise
divested of its trade secrets,
irrespective of what has been deposited with the U.S Copyright Office.
"""

import asyncio
import csv
import gzip
import json
import logging
import os
import pathlib
import re
import shutil
import sys
import time
from getpass import getpass
from typing import List, Dict, Union, Tuple
from croniter import croniter
from datetime import datetime, timedelta

import aiohttp
import requests
import urllib3
from requests.auth import HTTPBasicAuth
from tqdm import tqdm

requests.packages.urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PROCESS_SEARCH_URL = "bas/rest/bpm/wle/v1/processes/search?"
PROCESS_SEARCH_BPD_FILTER = "searchFilter="
PROCESS_SEARCH_PROJECT_FILTER = "&projectFilter="
TASK_SUMMARY_URL = "bas/rest/bpm/wle/v1/process/"
TASK_SUMMARY_URL_SUFFIX = "/taskSummary/"
TASK_DETAIL_URL = "bas/rest/bpm/wle/v1/task/"
TASK_DETAIL_URL_SUFFIX = "?parts=data"

validation_result = None
envUsage = None

global valid_time_expression

def build_instance_search_url(config: Dict[str, Union[str, int]], logger: logging.Logger) -> str:
    # Ensure root_url ends with a backslash
    root_url = config['root_url'].rstrip('/') + '/'

    # Ensure there is at least one backslash between root_url and PROCESS_SEARCH_URL
    if not root_url.endswith('/'):
        url = root_url + '/' + PROCESS_SEARCH_URL
    else:
        url = root_url + PROCESS_SEARCH_URL

    # Check for multiple backslashes and keep only one
    url = '/'.join(part.rstrip('/') for part in url.split('/'))

    # from_date and from_date_criteria
    from_date_str = config['from_date_criteria']+"="+config['from_date']

    # to_date and to_date_criteria
    to_date_str = config['to_date_criteria']+"="+config['to_date']

    url = url + from_date_str + "&" + to_date_str

    # Add the process name and project to the URL
    url = url + "&searchFilter=" + config['process_name'] + PROCESS_SEARCH_PROJECT_FILTER + config['project']

  
    if config['instance_limit'] > 0 :
        url = url + f"&limit={str(config['instance_limit'])}"

    if config['offset'] > 0 :
        url = url + f"&offset={str(config['offset'])}"

    if config['status_filter'] != "":
        url = url + "&statusFilter="+config['status_filter']

    log_and_print(logger, logging.INFO, f"Build URL: {format(url)}")
    return url

def get_aiohttp_BAW_auth(config: Dict[str, Union[str, int]], logger: logging.Logger) -> Union[int, aiohttp.BasicAuth]:
    # Read the Credentials from Environment Variables    
    bawUsername=""
    bawPassword=""    
    if envUsage is None:
        # Read the Credentials from Config Object
        if config is not None and 'user_name' in config and config['user_name'] != "":
            bawUsername = config['user_name']
            if 'password' in config and config['password'] != "":
                bawPassword = config['password']
            else:
                bawPassword = getpass("\nEnter BAW password: \n")
    else:
        if 'BAW_USERNAME' in os.environ and os.environ['BAW_USERNAME'] != "" and 'BAW_PASSWORD' in os.environ and os.environ['BAW_PASSWORD'] != "":
            bawUsername = os.environ['BAW_USERNAME']
            bawPassword = os.environ['BAW_PASSWORD']
    
    if bawUsername is None or bawUsername == "" or bawPassword is None or bawPassword == "":
        log_and_print(logger, logging.ERROR, "Either username or password is not configured")
        return 0

    # Prepare the aiohttp_BAW_auth from Credentials
    aiohttp_BAW_auth = aiohttp.BasicAuth(login=bawUsername, password=bawPassword, encoding='utf-8')
    return aiohttp_BAW_auth

async def get_task_details(
    session: aiohttp.ClientSession,
    instance: str,
    task_list: List[str],
    baw_raw_data: List[Dict],
    pbar: tqdm,
    config: Dict[str, Union[str, int]],
    logger: logging.Logger) -> None:
    
    auth = get_aiohttp_BAW_auth(config, logger)
    if auth == 0:
        log_and_print(logger, logging.ERROR, 'ERROR getting Auth')
        return

    for task_id in task_list:
        message = f"Fetching task details for bpd instance : {instance} and Task : {task_id}"
        logger.debug(message)
        url = config['root_url'] + '/' + TASK_DETAIL_URL + task_id + TASK_DETAIL_URL_SUFFIX

        async with session.get(url, auth=auth, ssl=False) as task_details_response:
            task_details_status = task_details_response.status
            if task_details_status == 200:
                logger.debug('Successful response for fetching task details for task_id : ' + task_id)
                task_detail_data = await task_details_response.json()
                baw_raw_data.append(task_detail_data['data'])
                pbar.update(1)
            else:
                err_message = "GET task details error for instance: " + instance + ", taskId: " + task_id + " with HTTP response status: " + str(task_details_response.status)
                log_and_print(logger, logging.WARNING, err_message)

async def get_task_summaries(
    session: aiohttp.ClientSession,
    instance: str,
    bpd_instance_dict: Dict[str, List[str]],
    pbar: tqdm,
    config: Dict[str, Union[str, int]],
    logger: logging.Logger) -> None:
    
    url = config['root_url'] + '/' + TASK_SUMMARY_URL + instance + TASK_SUMMARY_URL_SUFFIX

    auth = get_aiohttp_BAW_auth(config, logger)
    if auth == 0:
        log_and_print(logger, logging.ERROR, 'ERROR getting Auth')
        return

    async with session.get(url, auth=auth, ssl=False) as task_summary_response:
        task_summary_status = task_summary_response.status
        if task_summary_status == 200:
            task_summary_data = await task_summary_response.json()

            task_list = []
            for task_summary in task_summary_data['data']['tasks']:
                task_id = task_summary['tkiid']
                logger.debug(f"Instance {instance} found Task : {task_id}")
                task_list.append(task_id)

            # Update the bpd_instance_dict
            bpd_instance_dict[instance] = task_list
            pbar.update(1)
        else:
            message = "GET task summaries error for instance: " + instance + " with HTTP response status: " + str(task_summary_response.status)
            log_and_print(logger, logging.WARNING, message)            
            
async def get_instance_data(
    instance_list: List[str],
    baw_raw_data: List[Dict],
    config: Dict[str, Union[str, int]],
    logger: logging.Logger) -> None:
    
    # Dictionary to hold bpd instances and related tasks
    bpd_instance_dict = {}

    instance_count = len(instance_list)
    log_and_print(logger, logging.INFO, f"Processing {instance_count} instances. Fetching task summaries .....")

    # Initialise the connector
    connector = aiohttp.TCPConnector(limit=config['thread_count'])

    # create a ClientTimeout to allow for long running jobs
    infinite_timeout = aiohttp.ClientTimeout(total=None , connect=None,
                          sock_connect=None, sock_read=None)

    # Get the task list for each instance
    async with aiohttp.ClientSession(connector=connector, timeout=infinite_timeout) as session:
        async_tasks = []
        pbar = tqdm(total=instance_count)
        for instance in instance_list:
            async_task = asyncio.ensure_future(get_task_summaries(session, instance, bpd_instance_dict, pbar, config, logger))
            async_tasks.append(async_task)

        await asyncio.gather(*async_tasks)
        pbar.close()

    # Re-initialise the connector
    connector = aiohttp.TCPConnector(limit=config['thread_count'])

    # At this point the bpd_instance_dict variable will be populated as it is passed as a parameter
    # to get_task_summaries() and updated each time we fetch the tasks associated with a process instance

    # Calculate how many tasks exist in the dictionary
    task_count = 0
    for key, value in bpd_instance_dict.items():
        if isinstance(value, list):
            task_count += len(value)
    log_and_print(logger, logging.INFO, f"Processing {task_count} tasks. Fetching task details .....")

    async with aiohttp.ClientSession(connector=connector, timeout=infinite_timeout) as session:
        async_tasks = []

        pbar = tqdm(total=task_count)
        for instance in instance_list:
            task_list = bpd_instance_dict[instance]
            # From the list of task_ids associated with this instance id, get the task details of each into the new list baw_raw_data
            async_task = asyncio.ensure_future(get_task_details(session, instance, task_list, baw_raw_data, pbar, config, logger))
            async_tasks.append(async_task)

        await asyncio.gather(*async_tasks)
        pbar.close()


async def get_instance_list(config: Dict[str, Union[str, int]], logger: logging.Logger) -> List[str]:
    instance_list = []
    
    auth = get_aiohttp_BAW_auth(config, logger) 
    
    # Re-initialise the connector
    thread_count = config.get('thread_count')
    connector = aiohttp.TCPConnector(limit=thread_count)
    
    # create a ClientTimeout to allow for long running jobs
    infinite_timeout = aiohttp.ClientTimeout(total=None , connect=None,
                          sock_connect=None, sock_read=None)
    try:
        url = build_instance_search_url(config, logger)
        message = f"Search URL: {url}"
        logger.info(message)
        
        async with aiohttp.ClientSession(connector=connector, timeout=infinite_timeout) as session:
            print("About to connect to {0}\n".format(url))
            async with session.get(url, auth=auth, ssl=False) as response:
                status = response.status
                if status == 200:
                    instance_data_json = await response.json()

                    for bpd_instance in instance_data_json['data']['processes']:
                        instance_list.append(bpd_instance['piid'])
                else:
                    error = await response.text()
                    message = f"\nBAW REST API response code: {response.status}, reason: {response.reason}, {error}"
                    log_and_print(logger, logging.ERROR, message)
    except KeyError as e:
        message = f"\nIssue with the config variable key(s) while processing BPD: {str(config)}"
        log_and_print(logger, logging.ERROR, message)
        logger.error(e)
        raise e
    
    except Exception as e:
        message = f"\nUnexpected error processing BPD: {str(config)}"
        log_and_print(logger, logging.ERROR, message)
        log_and_print(logger, logging.ERROR, str(e))

    return instance_list

async def extract_baw_data(instance_list: List[str], baw_raw_data: List[Dict], config: Dict[str, Union[str, int]], logger: logging.Logger) -> List[str]:
    try:
        log_and_print(logger, logging.INFO, 'Extraction from BAW starting')
        # if instance_list size is 0, fetch the processes
        if len(instance_list) == 0:
            run_instance_list = await get_instance_list(config, logger)
            if len(run_instance_list) == 0:
                log_and_print(logger, logging.INFO, "No instances match the search")
                return instance_list
            else:
                log_and_print(logger, logging.INFO, f"Found : {len(run_instance_list)} instances of BPD {config['process_name']} in project {config['project']}")
        else:
            # we use another loop to fetch data from the instance list
            run_instance_list = instance_list

        # If loop and paging size: we fetch all the instance lists, we extract the task details for at max paging
        # size instance at each loop. In this case we don't update last_before and last_after because we have not
        # searched new instances in BAW split the instance list to fetch at max config['paging_size']. The rest will
        # be processed at next loops
        if config['loop_rate'] > 0 and 0 < config['paging_size'] < len(run_instance_list):
            instance_list = run_instance_list[config['paging_size']:]
            run_instance_list = run_instance_list[:config['paging_size']]

        else:
            # all the instances are fetched
            instance_list = []

        # get_instance_data() calls get_task_summaries() then get_task_details()
        await get_instance_data(run_instance_list, baw_raw_data, config, logger)

    except Exception as e:
        log_and_print(logger, logging.ERROR, 'There was an error in the execution' + str(e))

    log_and_print(logger, logging.INFO, f"Still {len(instance_list)} instances to process")

    return instance_list


def file_compress(file_to_write: str, out_zip_file: str, logger: logging.Logger) -> None:
    try:
        # Validate input file existence
        if not os.path.exists(file_to_write):
            message = f"Input CSV file to write: '{file_to_write}' not found."
            log_and_print(logger, logging.ERROR, message)
            raise FileNotFoundError(message)

        # Validate non-empty CSV data
        if os.stat(file_to_write).st_size == 0:
            message = f"Input CSV file to write: '{file_to_write}' is empty."
            log_and_print(logger, logging.ERROR, message)
            raise ValueError()

        # Compress and write to gzip file
        with open(file_to_write, 'rt', encoding='utf-8') as csv_file:
            with gzip.open(out_zip_file, 'wt', encoding='utf-8') as gzip_file:
                shutil.copyfileobj(csv_file, gzip_file)

        log_and_print(logger, logging.INFO, f"\nCSV file '{file_to_write}' compressed to '{out_zip_file}' successfully.")

    except FileNotFoundError as e:
        log_and_print(logger, logging.ERROR, f"Input CSV file to write: '{file_to_write}' not found.")
        logger.error(e)
    except ValueError as e:
        log_and_print(logger, logging.ERROR, f"Input CSV file to write: '{file_to_write}' is empty.")
        logger.error(e)
    except Exception as e:
        log_and_print(logger, logging.ERROR, f"Error: An unexpected error occurred: {e}")

def generate_csv_file(baw_raw_data: List[Dict], config: Dict[str, Union[str, int]], logger: logging.Logger) -> str:
        logger.info(sanitize_pii(f"\nGenerating csv file. Config = {config} \n"))
        if not isinstance(baw_raw_data, list) or not baw_raw_data:
            raise ValueError("No BAW data extracted. It should be a non-empty list of BAW data.")

        if config is None or not config.get('csvpath') or not config.get('csvfilename'):
            raise ValueError("Invalid config. It should be a non-empty dictionary with 'csvpath' and 'csvfilename'.")
        elif hasDoubleDot(config.get('csvpath')) or hasDoubleDot(config.get('csvfilename')):
            raise ValueError("Invalid config. It should not contain '..' with 'csvpath' and 'csvfilename'.")
        else:
            # Ensure there is at least one backslash
            filepath = os.path.join(config.get("csvpath"), config.get("csvfilename") + "." + "csv")
            gzip_filepath = filepath + ".gz"

        try:
            fieldnames = list(baw_raw_data[0].keys())
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                csv_writer.writeheader()
                csv_writer.writerows(baw_raw_data)

            log_and_print(logger, logging.INFO, "\nCSV file generated successfully.")

            file_compress(filepath, gzip_filepath, logger)

            return gzip_filepath
        except Exception as e:
            log_and_print(logger, logging.ERROR, f"\nError generating CSV file : {e}")
            raise e


def validate_cron_expression(cron_expression: str, logger: logging.Logger) -> Tuple[bool, str]:
    if (cron_expression and croniter.is_valid(cron_expression)):
        currentDate = datetime.now()
        nextRunDate = croniter(cron_expression, currentDate).get_next(datetime)
        cron_converted_schedule_time = nextRunDate.strftime('%H:%M')
        if (nextRunDate - currentDate) <= timedelta(hours=24):
            log_and_print(logger, logging.INFO, f"\nValid cron expression found: {cron_expression}")
            return True, cron_converted_schedule_time
        else:
            logger.warning("The following cron expression is not valid as it is not within the next 24 hours: " +cron_expression)
            return False, "Invalid"
    else:
        message = "Cron expression or H:M format is invalid or not set"
        return False, message

def validate_time_expression(time_expression: str, logger: logging.Logger) -> bool:
    # Regular expression pattern for time in the next 24 hours format (HH:MM)
    time_pattern = r'^([01]\d|2[0-3]):([0-5]\d)$'

    # Check if the provided time string matches the pattern
    if re.match(time_pattern, time_expression):
        message = f"\nThe given time '{time_expression}' is a text based time."
        log_and_print(logger, logging.INFO, message)
        return True
    else:
        return False


async def calculate_next_execution_time(schedule_time: str, logger: logging.Logger) -> datetime:
    # Parse the schedule time string (e.g., "10:00")
    hour, minute = map(int, schedule_time.split(':'))

    # Get the current date and time
    now = datetime.now()

    # Calculate the target time for today
    target_time_today = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # If the target time is already passed for today, schedule for tomorrow
    if now > target_time_today:
        target_time_today += timedelta(days=1)

    return target_time_today

def validate_schedule_time(schedule_time: str, logger: logging.Logger) -> str:
    cron_converted_time_expression = validate_cron_expression(schedule_time, logger)
    
    if cron_converted_time_expression[0]:
        valid_time_expression = cron_converted_time_expression[1]
    elif validate_time_expression(schedule_time, logger):
        valid_time_expression = schedule_time
    else:
        message = "Cron expression is invalid or not set"
        logger.debug(message)
        raise ValueError(message)
    return valid_time_expression

# Function to schedule BAW data extraction
async def schedule_extraction(schedule_time: str, config: Dict[str, Union[str, int]], logger: logging.Logger) -> None: 
    valid_time_expression = validate_schedule_time(schedule_time, logger)
     
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"Scheduling extraction at {schedule_time}, current time: {now}"
    log_and_print(logger, logging.info, message)
    
    # Calculate the delay until the next scheduled execution
    next_execution = await calculate_next_execution_time(valid_time_expression, logger)
    delay = max(0, (next_execution - datetime.now()).total_seconds())
    minutes, seconds = divmod(delay, 60)
    message = f"Next execution scheduled in: {int(minutes)} minutes and {int(seconds)} seconds"
    log_and_print(logger, logging.info, message)
        
    if schedule_time != valid_time_expression:
        # commenting on cron expression converted to a time
        message=f"Cron expression '{schedule_time}' is interpreted to run at {valid_time_expression}"
        log_and_print(logger, logging.info, message)
    
    print("\u23F2")
    
    countdown_seconds = get_seconds_until(valid_time_expression)
    await display_countdown(countdown_seconds)
    
    # Execute the extraction request
    await processExtractionRequest(config, logger)

async def system_extract_baw_data(config: Dict[str, Union[str, int]] = None):
    
    envUsage = True

    env_config = {        
        'root_url': os.environ.get('BAW_ROOT_URL', ""),
        'process_name': os.environ.get('BAW_PROCESS_NAME', ""),
        'project': os.environ.get('BAW_PROJECT_NAME', ""),
        'from_date': os.environ.get('BAW_START_DATE', ""),
        'from_date_criteria': os.environ.get('BAW_START_DATE_CRITERIA', ""),
        'to_date': os.environ.get('BAW_END_DATE', ""),
        'to_date_criteria': os.environ.get('BAW_END_DATE_CRITERIA', ""),
        'status_filter': os.environ.get('BAW_STATUS_FILTER', ""),
        'instance_limit': os.environ.get('BAW_INSTANCE_LIMIT', ""),
        'offset': os.environ.get('BAW_OFFSET', ""),
        'thread_count': os.environ.get('BAW_THREAD_COUNT', ""),
        'csvpath': os.environ.get('BAW_CSV_PATH', ""),
        'csvfilename': os.environ.get('BAW_CSV_FILENAME', ""),
        'logfile': os.environ.get('BAW_LOG_FILE', ""),
        'user_name': os.environ.get('BAW_USERNAME', ""),
        'password': os.environ.get('BAW_PASSWORD', ""),
        'schedule_time':os.environ.get('BAW_SCHEDULE_TIME', "")
    }    

    # Validate env_config variables at first place if some variable values are empty or failing the validation
    validation_result = validate_config(env_config)
    if validation_result['valid']:
        config = env_config
    elif config != None:
        # Validate again config passed in the function if env_config fails
        validation_result = validate_config(config)

    if validation_result['valid']:
        # Set up the logger
        logger = setup_logger(config, logging.INFO)
        try:
            # valid_time_expression = validate_schedule_time(config['schedule_time'], logger)
            if config['schedule_time'] and config.get('schedule_time') != None and config.get('schedule_time') !=  "":
                await schedule_extraction(config['schedule_time'], config, logger)
            else:   
                await processExtractionRequest(config, logger)
        except Exception as e:
            # Handle exceptions gracefully
            log_and_print(logger, logging.ERROR, f"\nError: {e}")
            sys.exit(1)
    else:
        print(f"\nInvalid configuration: {validation_result['errors']}")
        sys.exit(1)

# If config is None or if config['logfile'] is None. 
# If either condition is true, we add a NullHandler to the logger, which effectively discards log messages. 
def setup_logger(config: Dict[str, Union[str, int]], level: int) -> logging.Logger:
    logger = logging.getLogger(__name__)
    
    if config is None or config.get('logfile') is None:
        # Handle the case where config is None or logfile is None
        handler = logging.NullHandler()
    else:
        if not os.path.isdir(config['csvpath']):    
            os.makedirs(config['csvpath'])
        log_file_path_full = os.path.join(pathlib.Path(os.path.abspath(config['csvpath'])), config['logfile'] + ".log")
        formatter = logging.Formatter('%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s')
        file_handler = logging.FileHandler(log_file_path_full)
        file_handler.setFormatter(formatter)
        handler = file_handler

    logger.addHandler(handler)
    logger.setLevel(level)
    
    # Since the print statement already print to the console, the logger is also printing on the console. 
    # This prevents logger from printing to the console again.
    logger.propagate = False

    return logger


def get_user_input(prompt: str, default: str = None, password: bool = False) -> str:
    while True:
        if password:
            user_input = getpass(prompt)
        else:
            user_input = input(prompt)

        if user_input == "" and default is not None:
            return default
        elif user_input != "":
            return user_input
        
def get_Config_from_user_in_one_line() -> dict:
    while True:
        config_str_without_password = input("\nEnter config variables in the key=value format separated by spaces (no quotes, no password): \n")
        if "password=" in config_str_without_password.lower():
            print("\nNOTE: You cannot enter password with the input configuration\n")
            continue
        else:
            break    
    password_str = getpass("\nEnter BAW password: \n")
    config_str = config_str_without_password + " password=" + password_str 

    #remove any spaces around the '=' sign
    config_str = re.sub("[ ]*=[ ]*", "=", config_str)
    
    # Split the input string by spaces to get individual config variables
    config_vars = config_str.split()

    # Create a dictionary to store the config variables
    config = {}

    # Parse each config variable and add it to the dictionary
    previous_key = None
    for var in config_vars:
        # Split the variable into key and value based on the first occurrence of '='
        split_var = var.split('=', 1)
        
        # Ensure there is a key and a value
        if len(split_var) == 2:
            key, value = split_var
            config[key] = value
            previous_key=key
        else:
            if previous_key:
                config[key] = config.pop(previous_key) +' ' +split_var[0]
    
    return config

def validate_config(config: Dict[str, Union[str, int]]) -> Dict[str, Union[bool, list]]:
    errors = []

    # Validate 'root_url'
    if not re.match(r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+$', config.get('root_url', '')):
        errors.append('Invalid root URL format')

    # Validate process_name and project (allow alphanumeric, space(s), underscore and hyphen)
    if 'process_name' in config:
        process_name = config.get('process_name')
        if not isinstance(process_name, str) or not re.match(r'^[\w\s\-_]*$', process_name):
            errors.append('Invalid process_name format. Should be alphanumeric, underscore, or hyphen')
    else:
        errors.append('Process name (process_name) must be provided')

    # Validate project and project (allow alphanumeric, space(s), underscore and hyphen)
    if 'project' in config:
        project = config.get('project')
        if not isinstance(project, str) or not re.match(r'^[\w\s\-_]*$', project):
            errors.append('Invalid project format. Should be alphanumeric, underscore, or hyphen')
    else:
        errors.append('Project name (project) must be provided')

    # Validate 'from_date' and 'to_date'
    date_format = re.compile(r'\d{4}-\d{2}-\d{2}')
    for key in ['from_date', 'to_date']:
        if not re.match(date_format, config.get(key, '')):
            errors.append(f'Invalid {key} format. Should be YYYY-MM-DD, or ISO8601 format e.g. 2011-08-04T03:12:53Z')

    # Validate 'from_date_criteria' and 'to_date_criteria'
    valid_from_criteria = ["modifiedAfter","createdAfter","closedAfter"]
    valid_to_criteria = ["modifiedBefore","createdBefore","closedBefore"]
    if not isinstance(config.get('from_date_criteria'), str) or config.get('from_date_criteria') not in valid_from_criteria:
         errors.append(f'Invalid start date criteria format. Must be one of the following: {valid_from_criteria}')
    if not isinstance(config.get('to_date_criteria'), str) or config.get('to_date_criteria') not in valid_to_criteria:
         errors.append(f'Invalid end date criteria format. Must be one of the following: {valid_to_criteria}')

    # Validate Statuses filter
    valid_status_filter = ["Active","Completed","Failed","Terminated","Suspended","Late","At_Risk"]
    provided_statuses = config.get('status_filter', '').split(',')
    for val in provided_statuses:
        if val not in valid_status_filter:
            errors.append(f'Invalid status: {val}. Must be one of the following: {valid_status_filter}')

    # Validate integer values
    int_keys = ['instance_limit', 'offset', 'thread_count']
    for key in int_keys:
        # We need a default value ('') in case the BAW_Connector module is run with empty arguments.
        if not str(config.get(key, '')).isdigit():
            errors.append(f'Invalid {key} format. Should be an integer')
        else:
            config[key] = int(config.get(key))

    config['loop_rate'] = 0
    config['paging_size'] = 0
            
    # Validate 'csvpath'
    if 'csvpath' in config:
        csvpath = config.get('csvpath')  
        if not isinstance(csvpath, str) or ((os.name == 'nt' and re.match(r'^[a-zA-Z]:\\(?:[\w]+\\)*[\w]+$', csvpath) is None) and 
                                            (re.match(r'^\/(?:[^\/\0]+\/?)*$', csvpath) is None)) or hasDoubleDot(csvpath):
            errors.append('Invalid csvpath format. Should be a valid filesystem path with no double dots')
    else:
        errors.append('CSV output path (csvpath) must be provided as a valid filesystem path')

    # Validate 'csvfilename'
    csvfilename = config.get('csvfilename', '')
    if not re.match(r'^[\w]+$', csvfilename) or hasDoubleDot(csvfilename):
        errors.append('Invalid csvfilename format. Should be a string without extension and no double dots')

    # Validate 'logfile'
    if 'logfile' in config:
        logfile = config.get('logfile')
        if not isinstance(logfile, str) or not re.match(r'^[\w.]+$', logfile) or hasDoubleDot(logfile):
            errors.append('Invalid logfile format. Should be a string without double-dots')
    else:
        errors.append('Log file name (logfile) must be provided')

    # Validate 'user_name' and 'password'
    for key in ['user_name', 'password']:
        if not config.get(key, ''):
            errors.append(f'{key} is required')

    if not errors:
        # No errors
        valid = True
    else:
        # Errors found
        valid = False
    
    return {'valid': valid, 'errors': errors}

    
async def processExtractionRequest(config: Dict[str, Union[str, int]], logger: logging.Logger) -> None:
    baw_raw_data = []  
    instance_list = []
    
    # Execute immediately
    await extract_baw_data(instance_list, baw_raw_data, config, logger)

    # Generate CSV file
    csv_file_path = generate_csv_file(baw_raw_data, config, logger)
    
    log_and_print(logger, logging.INFO, f"CSV file generated at: {csv_file_path}")    
    log_and_print(logger, logging.INFO, "BAW data extraction completed!")
    sys.exit(0)

async def checkForScheduleRequest(config: Dict[str, Union[str, int]], logger: logging.Logger) -> None:
    # If the user provided a schedule_time attribute/key in the config and also provided the schedule_time value.
    if 'schedule_time' in config and config.get('schedule_time') != '' and config.get('schedule_time') != 'None':
        await schedule_extraction(config.get('schedule_time'), config, logger)
    elif 'schedule_time' in config and (config.get('schedule_time') == '' or config.get('schedule_time') == 'None'):
        # The user has the scheduled_time attribute but not the scheduled_time value. So, it can be interpreted as not wanting to schedule.
        print("While schedule_time key exists, value was not specified, thus no scheduling is required")
        await processExtractionRequest(config, logger)
    else:
        message = "\nschedule_time attribute/key does exist. This could be an unintended omission, thus need to ask if scheduling is required"
        log_and_print(logger, logging.INFO, message)
        # Ask the user if they want to schedule the extraction
        schedule_choice = get_user_input("\nDo you want to schedule the extraction? (y/n): \n").lower().strip()
        
        if schedule_choice == 'y':
            # schedule_time = get_user_input("Enter the scheduled time within the next 24 hours with 5 minutes minimum starting time in either hour:time format (i.e., 00:05 to 24:00) or cron expression: ").lower().strip()
            schedule_time = get_user_input("\nEnter the scheduled time within the next 24 hours in either hour:minute time format (i.e., 00:05 to 23:59) or cron expression (e.g, '*/5 * * * *'): \n").lower().strip()
            await schedule_extraction(schedule_time, config, logger)
        elif schedule_choice == 'n':
             await processExtractionRequest(config, logger)
        elif schedule_choice == 'q':
            message = "\nExiting the BAW Data Extraction Tool."
            log_and_print(logger, logging.INFO, message)
            sys.exit(0)
        else:
            message = "\nUnknown selection. Exiting the BAW Data Extraction Tool."
            log_and_print(logger, logging.ERROR, message)
            sys.exit(0)

def get_seconds_until(schedule_time: str) -> int:
    # Parse the schedule time string
    schedule_time_obj = time.strptime(schedule_time, '%H:%M')
    
    # Convert the parsed time to seconds
    schedule_seconds = schedule_time_obj.tm_hour * 3600 + schedule_time_obj.tm_min * 60
    
    # Calculate the current time in seconds
    current_time = time.localtime()
    current_seconds = current_time.tm_hour * 3600 + current_time.tm_min * 60 + current_time.tm_sec
    
    # Calculate the time difference between the schedule time and current time
    seconds_until = schedule_seconds - current_seconds
    
    # Adjust for negative values (if the schedule time is in the past)
    if seconds_until < 0:
        seconds_until += 86400  # Add one day (24 hours) in seconds
    
    return seconds_until

async def display_countdown(countdown_seconds: int) -> None:
    # Function to display the countdown timer
    while countdown_seconds > 0:
        minutes, seconds = divmod(countdown_seconds, 60)
        
        # DO NOT PUT THE PRINT BELOW IN THE log_and_print FUNCTION. THE COUNT DOWN WILL PRINT ON DIFFERENT LINE OTHERWISE.
        print(f"Count down to the time until the scheduled BAW data extraction starts (Minutes:Seconds): {minutes:02d}:{seconds:02d}", end='\r')
        
        await asyncio.sleep(1)  # Wait for 1 second asynchronously
        countdown_seconds -= 1

def print_help_information():
    print("")
    print("========================================================================================")
    print("HOW TO RUN THE BAW CONNECTOR MODULE TO FETCH BAW DATA")
    print("========================================================================================")
    print("Below are the 3 starting points for the BAW Connector module. You can pass variables in directly, through a file directly or specify neither, and press enter to open the menu for all other options.")
    print("\nAny of the following commands can be used to run/execute the BAW Connector module in a command line:")
    print("\n(1) Executing the connector module with the correct command line but nothing passed as command arguments:\n\npython BAW_Connector.py\n")
    print("\nIf there no command arguments and no JSON file provided (i.e. the 3rd method mentioned above) or there is an error in the provided config variables (either in the command line arguments or in JSON file), an interactive mode will be displayed with further instructions as shown below.")
    print("\n - 'i' will be for adding all variables individually when prompted (no quotes on strings)")
    print("\n - 'c' will be for adding all variables in 1 line, space separated as key=value pairs and with no quotes.\n   After pressing 'c' and prompted for variables, enter:\n\n   root_url= process_name= project= from_date= from_date_criteria=<one of these: modifiedAfter/createdAfter/closedAfter> to_date= to_date_criteria=<one of these: modifiedBefore/createdBefore/closedBefore> status_filter=<either one or all of these: Active,Completed,Failed,Terminated,Suspended,Late,At_Risk> instance_limit= offset= thread_count= csvpath= csvfilename= logfile= user_name= password= schedule_time=<HH:mm (e.g. 13:33) or cron expression (e.g. 33 13 * * *   or   */1 * * * *)>\n")
    print("\n - 'p' will be for adding all variables through a json file, similar to option (3)")
    print("\n - 's' will be for reading all variables through environment variables.\n")
    print("\n(2) Executing the connector module with the correct command line and command arguments as source of config variables. e.g. \n\npython BAW_Connector.py root_url=\"\" process_name=\"\" project= from_date= from_date_criteria=<one of these: modifiedAfter/createdAfter/closedAfter> to_date= to_date_criteria=<one of these: modifiedBefore/createdBefore/closedBefore> status_filter=<either one or all of these: Active,Completed,Failed,Terminated,Suspended,Late,At_Risk> instance_limit= offset= thread_count= csvpath=\"\" csvfilename= logfile= user_name= password= schedule_time=\"<HH:mm (e.g. 13:33) or cron expression (e.g. 33 13 * * *   or   */1 * * * *)>\"\n")
    print("\nNOTE: This is similar to the 'c' selection in option (1) EXCEPT we include quotes here on the root_url, process_name, csvpath and schedule_time values.\n")
    print("\n(3) Executing the connector module with the correct command line and on a JSON config file as the source of config variables:\n\npython BAW_Connector.py ./baw_config.json\n")
    print("\t\t---------------------------------")
    print("\nFor all the above examples, only the <schedule_time> variable is optional. It can also be accepted in 2 formats, a time (hours:minutes) or cron expression.")
    print("So the following prompt will be shown: \n   \"Enter the scheduled time within the next 24 hours in either hour:minute time format (i.e., 00:05 to 24:00) or cron expression:\"")
    print("\nThen enter the time in a format similar to this:\n\t13:33\n")
    print("\nOr enter the cron expression in a format similar to this:\n\t33 13 * * *\nOr this:\n\t*/1 * * * *\n")
   

def print_display_instructions():
        print("\n----------------------------------------------------------------------------------------")
        print("Instructions:")
        print("----------------------------------------------------------------------------------------")
        print("  - For help on how to run the BAW Connector module, type 'h' ")
        print("  - To provide configuration variables interactively (one at a time), type 'i' ")
        print("  - To provide all the configuration variables on a single line, type 'c' ")
        print("  - To provide a path to a JSON file that contains the configuration variables, type 'p' ")
        print("  - To extract BAW data based on the configuration set as environment variables, type 's' ")
        print("  - To quit at the configuration process and exit the tool, type 'q'.\n")
    
# Do not use print_and_log functions here because as config may bot be in scoped before calling the config validation.
async def getConfigFromOtherMeans(validation_result):
    if not validation_result['valid']:
        print("")
        print("========================================================================================")
        print("Welcome to the BAW Data Extraction Tool!")
        print("========================================================================================")
        print("")
        
        if validation_result['errors']:
            print("----------------------------------------------------------------------------------------")
            print("Parameters passed to the BAW Data Extraction Tool are not valid for this command line.")
            print("----------------------------------------------------------------------------------------")
            print(validation_result['errors'])
            
        # Display instructions
            print_display_instructions()

# Ask the user if they want to provide configuration interactively or upload a config file
        config_choice = get_user_input("\nPlease enter your configuration choice to progress: \n").lower().strip()

        while config_choice == 'h':
            print_help_information()
            print_display_instructions()
            config_choice = get_user_input("\nPlease enter your configuration choice to progress: \n").lower().strip()

        if config_choice == 'i':
            # Interactively gather configuration details
            config = {
                'root_url': get_user_input("\nEnter BAW root URL: \n").strip(),
                'process_name': get_user_input("\nEnter BAW process name: \n").strip(),
                'project': get_user_input("\nEnter BAW project name: \n").strip(),
                'from_date': get_user_input("\nEnter start date (like YYYY-MM-DD, or ISO8601 format e.g. 2011-08-04T03:12:53Z): \n").strip(),
                'from_date_criteria': get_user_input("\nEnter start date criteria (modifiedAfter/createdAfter/closedAfter): \n").strip(),
                'to_date': get_user_input("\nEnter end date (like YYYY-MM-DD, or ISO8601 format e.g. 2011-08-04T03:12:53Z): \n").strip(),
                'to_date_criteria': get_user_input("\nEnter end date criteria (modifiedBefore/createdBefore/closedBefore): \n").strip(),
                'status_filter': get_user_input("\nEnter any statuses to search for (can be multiple statuses when comma separated, can be any of: Active,Completed,Failed,Terminated,Suspended,Late,At_Risk): \n").strip(),
                'instance_limit': get_user_input("\nEnter instance limit (0 for no limit): \n", default='0').strip(),
                'offset': get_user_input("\nEnter offset value: \n", default='0').strip(),
                'thread_count': get_user_input("\nEnter thread count: \n", default='10').strip(),
                'csvpath': get_user_input("\nEnter CSV output path: \n").strip(),
                'csvfilename': get_user_input("\nEnter CSV output filename (without extension): \n").strip(),
                'logfile': get_user_input("\nEnter log file name (without extension): \n").strip(),
                'user_name': get_user_input("\nEnter BAW username: \n").strip(), 
                'password': get_user_input("\nEnter BAW password: \n", password=True).strip()
            }

            # Validate config variables
            validation_result = validate_config(config)
            if not validation_result['valid']:
                try:
                    await getConfigFromOtherMeans(validation_result)
                except ValueError as ve:
                    message = f"\nError in calling getConfigFromOtherMeans in 'i' mode: {ve}"
                    print(message)

        elif config_choice == 'p':
            # Ask the user to upload a config file
            config_file_path = get_user_input("\nEnter the path to the config file: \n").strip()
            try:
                with open(config_file_path, 'r') as config_file:
                    config = json.load(config_file)
                    # Validate config for password                  
                    if 'password' in config:
                        print("\nPassword cannot be included in the config file, Exiting\n")
                        sys.exit(1)
                    else:
                        password_str = getpass("\nEnter BAW password: \n")
                        config['password'] = password_str
                        # Validate config variables
                        validation_result = validate_config(config)
                        if not validation_result['valid']:
                            try:
                                await getConfigFromOtherMeans(validation_result)
                            except ValueError as ve:
                                message = f"\nError in calling getConfigFromOtherMeans in 'p' mode: {ve}"
                                print(message)
            except FileNotFoundError:
                message = f"\nError: Config file not found at {config_file_path}"
                print(message)
                sys.exit(1)
            except json.JSONDecodeError:
                message = "\nError: Invalid JSON format in config file"
                print(message)
                sys.exit(1)
                
        elif config_choice == 's':
            await system_extract_baw_data()

        elif config_choice == 'c':
            config = get_Config_from_user_in_one_line()
            # Validate config variables
            validation_result = validate_config(config)
            if not validation_result['valid']:
                try:
                    await getConfigFromOtherMeans(validation_result)
                except ValueError as ve:
                    message = f"\nError in calling getConfigFromOtherMeans in 'c' mode: {ve}"
                    print(message)

        elif config_choice == 'q':
            # Quit if user enters 'Q'
            message = "\nExiting the BAW Data Extraction Tool."
            print(message)
            sys.exit(0)
            
        else:
            message = "\nInvalid choice. Exiting."
            print(message)
            sys.exit(1)

    try:
       # Set up logger with user's config.
        logger = setup_logger(config, logging.INFO)
        await checkForScheduleRequest(config, logger)
    except ValueError as ve:
        message = f"\nError: {ve}"
        log_and_print(logger, logging.ERROR, message)
        
    message = "\nDONE!!!"
    log_and_print(logger, logging.INFO, message)      

def getConfigFromCmdLineArgs()-> Dict[str, Union[str, int]]:
    # Set up default logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Get command-line arguments
    args = sys.argv[1:]

    # Check if a JSON file path is provided
    if args and args[0].endswith('.json'):
        config_file_path = args[0]
        try:
            with open(config_file_path, 'r') as config_file:
                config_dict = json.load(config_file)
        except FileNotFoundError:
            message = f"Config file not found: {config_file_path}"
            log_and_print(logger, logging.ERROR, message)
            sys.exit(1)
        except json.JSONDecodeError:
            message = f"Error decoding JSON in config file: {config_file_path}"
            log_and_print(logger, logging.ERROR, message)
            sys.exit(1)
    else:
        try:
            # Convert command-line arguments to a dictionary
            config_dict = {}
            for arg in args:
                key, value = arg.split('=')
                config_dict[key] = value
        except ValueError as err:
            message = f"\nError while processing command args: {err}"
            log_and_print(logger, logging.WARNING, message)
            message = (f"\nSwitching the application to an interactive mode with further instructions.")
            log_and_print(logger, logging.WARNING, message)

    return config_dict

def log_and_print(logger: logging.Logger, logLevel: int, message: str)-> None:
    message = sanitize_pii(message) 
    if logLevel == logging.INFO:
        logger.info(message)
    elif logLevel == logging.ERROR:
        logger.error(message)
    elif logLevel == logging.DEBUG:
        logger.debug(message)
    elif logLevel == logging.WARNING:
        logger.warning(message)
    print(message)

def sanitize_pii(message: str) -> str:
    # Regular expressions to match 'password': 'the-password'
    password_pattern = r"'password'\s*:\s*'([^']*)'"
    
    # Replace PII with placeholders
    sanitized_message = re.sub(password_pattern, '\'password\': ********', message)
    
    return sanitized_message

def hasDoubleDot(message: str) -> bool:
    doubledot_pattern = r'\.\.'
    return re.search(doubledot_pattern,message)

def print_banner():
    banner = """\
         __            __            __                      ___
        |__) /\ |  |  |  \ _ |_ _   |_   |_ _ _  _|_. _  _    | _  _ |
        |__)/--\|/\|  |__/(_||_(_|  |__)(|_| (_|(_|_|(_)| )   |(_)(_)|
        """
    print(banner)
    
# Main function
async def main():    
    print_banner()
    cmdArgsConfig = getConfigFromCmdLineArgs()
    if len(cmdArgsConfig) != 0:
        # Validate config for password                  
        if 'password' in cmdArgsConfig:
            print("\nPassword cannot be included in the config file or config parameters, Exiting\n")
            sys.exit(1)
        else:
            password_str = getpass("\nEnter BAW password: \n")
            cmdArgsConfig['password'] = password_str
    
    # Set up logger with user's config.
    logger = setup_logger(cmdArgsConfig, logging.INFO)
    
    # Validate config variables
    validation_result = validate_config(cmdArgsConfig)

    if validation_result['valid']:
        try:
            await checkForScheduleRequest(cmdArgsConfig, logger)
            message ="\n\nDONE!"
            log_and_print(logger, logging.INFO, message)
        except ValueError as ve:
            message = f"\nError: {ve}"
            log_and_print(logger, logging.ERROR, message)       
    else:
        try:
            await getConfigFromOtherMeans(validation_result)
        except ValueError as ve:
            message = f"\nError in calling getConfigFromOtherMeans in main mode: {ve}"
            log_and_print(logger, logging.ERROR, message)

if __name__ == "__main__":    
    if os.name == 'nt':  # Windows
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
