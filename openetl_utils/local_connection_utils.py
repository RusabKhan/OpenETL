"""This module contains functions related to store managing and retrieving information from .local folder.
"""
import os
import json
from typing import List, Tuple
import regex as re

from openetl_utils.enums import LogsType

directory = f'{os.getcwd()}/.local'
pipelines_directory = f"{directory}/pipelines"
connections_directory = f"{directory}/connections"
profile_reports = f"{directory}/profile_reports"
# jars_directory = f"{directory}/jars"
api_directory = f"{directory}/api"
dags_directory = f"{directory}/dags"

dirs = [directory,dags_directory]
json_files_data = None


def create_con_directory():
    """Create all directories in dirs array.
    """
    for directory in dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Directory '{directory}' created successfully.")
        else:
            print(f"Directory '{directory}' already exists.")


def read_connection_configs(configs):
    """Read all configuration files in config from .local folder

    Args:
        configs (list): Names of configuration files

    Returns:
        dict: {'filename':'myconfiguration'}
    """
    json_files_data = []
    for config in configs:
        file_path = os.path.join(connections_directory, f"{config}.json")
        with open(file_path) as json_file:
            json_data = json.load(json_file)
            json_data_with_filename = {
                'filename': config,
                'data': json_data
            }
            json_files_data.append(json_data_with_filename)
    return json_files_data


def read_single_connection_config(config):
    """Read single connection configuration from connection directory

    Args:
        config (string): Name of the pipeline

    Returns:
        dict: config of the pipeline
    """
    file_path = os.path.join(connections_directory, f"{config}.json")
    with open(file_path) as json_file:
        json_data = json.load(json_file)
        return json_data


def store_connection_config(json_data, filename="", is_api=False, connection_name=""):
    """Store connection settings in a file in .local

    Args:
        filename (string): Connection name picked as filename
        json_data (dict): Connection details as key value pair.

    Returns:
        Boolean: True if saved else False
    """
    try:
        filename = filename.lower()
        if is_api:
            json_data['schema'] = 'public'
            json_data['database'] = 'public'
            with open(f"{api_directory}/{filename}.json", 'w') as file:
                json.dump(json_data, file, indent=4)
        with open(f"{connections_directory}/{connection_name}.json", 'w') as file:
            json.dump(json_data, file, indent=4)
            return True
    except Exception as e:
        return False


def get_all_connection_configs():
    """Get all connection configs from .local

    Returns:
        list: array of connection configs
    """
    return [
        filename.replace(".json", "")
        for filename in os.listdir(connections_directory)
        if filename.endswith('.json')
    ]


def read_connection_config(config):
    """Read a single config file from connections_directory in .local

    Args:
        config (string): Name of the config file

    Returns:
        dict: {'filename':'myconfiguration', 'data':'json_data'}
    """
    json_data_with_filename = {}
    file_path = os.path.join(connections_directory, f"{config}.json")
    try:
        with open(file_path) as json_file:
            json_data = json.load(json_file)
            json_data_with_filename = {
                'filename': config,
                'data': json_data
            }
    except Exception as e:
        return json_data_with_filename
    return json_data_with_filename


def read_all_connection_configs():
    """Read all connection configs database and JDBC

    Returns:
        dict: {"database": database_data,"api": jdbc_data}
    """
    database_data = []
    api_data = []
    configs = get_all_connection_configs()
    for config in configs:
        with open(f"{connections_directory}/{config}.json") as json_file:
            data = json.load(json_file)

        if data.get('connection_type') == 'database':
            database_data.append(
                {"connection_name": config, "connection": data})
        elif data.get('connection_type') == 'api':
            api_data.append({"connection_name": config, "connection": data})

    return {"database": database_data, "api": api_data}


def read_all_pipeline_configs():
    """Read all pipeline configurations from .local/pipelines

    Returns:
        list: List of all pipelines
    """
    return [
        filename.replace(".json", "")
        for filename in os.listdir(pipelines_directory)
        if filename.endswith('.json')
    ]


def read_pipeline_detals(pipeline):
    """Read single pipeline configuration

    Args:
        pipeline (string): Name of the pipeline

    Returns:
        dict: details of the pipeline
    """
    json_data = {}
    file_path = os.path.join(pipelines_directory, f"{pipeline}.json")
    try:
        with open(file_path) as json_file:
            json_data = json.load(json_file)["run_details"]
    except Exception as e:
        return json_data
    return json_data


def check_jar_exists(jar):
    return os.path.exists(f"{jars_directory}/{jar}")


def read_all_apis():
    """
    Reads all the APIs from the API directory and returns a list of JSON file names.

    Returns:
        list: A list of JSON file names without the extension.
    """
    data = []
    files = os.listdir(api_directory)
    json_files = [file[:-5] for file in files if file.endswith('.json')]

    # Loop through each JSON file and read its content
    return json_files


def read_api_config(apiname):
    with open(os.path.join(api_directory, f"{apiname}.json")) as f:
        return json.load(f)

def paginate_log_content(log_file_paths: List[str], page: int, per_page: int) -> Tuple[List[str], int]:
    """
    Paginate the content of multiple log files.

    Args:
        log_file_paths: A list of paths to log files.
        page: The page number to retrieve.
        per_page: The number of lines per page.

    Returns:
        A tuple containing:
            - A list of paginated log entries from all log files (newest first).
            - The total number of pages across all log files.
    """

    log_entry_pattern = re.compile(
        r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]) "
        r"(0[0-9]|1[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9]),\d{3}"
    )

    def process_log_lines(lines: List[str]) -> List[str]:
        """Ensure that each entry is a single log starting with a timestamp."""
        processed_entries = []
        current_entry = ""

        for line in lines:
            if log_entry_pattern.match(line):  # Start of a new log entry
                if current_entry:  # Save the current entry if exists
                    processed_entries.append(current_entry.strip())
                current_entry = line  # Start a new log entry
            else:
                current_entry += line  # Append to the current log entry

        if current_entry:  # Append the last entry
            processed_entries.append(current_entry.strip())

        return processed_entries

    all_log_lines = []

    # Read all log files and process lines into complete entries
    for log_file_path in log_file_paths:
        with open(log_file_path, 'r') as log_file:
            log_lines = log_file.readlines()
            all_log_lines.extend(process_log_lines(log_lines))

    # Reverse log entries to have the newest entries first
    all_log_lines.reverse()

    # Calculate total pages
    total_lines = len(all_log_lines)
    total_pages = (total_lines // per_page) + (1 if total_lines % per_page != 0 else 0)

    # Slice the lines based on the requested page
    start = (page - 1) * per_page
    end = start + per_page
    paginated_lines = all_log_lines[start:end]

    return paginated_lines, total_pages


def get_log_file_path(
    logs_dir: str,
    integration_id: str | None = None,
    logs_type: str = "INTEGRATION"
) -> List[str]:
    """
    Get log files from the specified directory, filtered and sorted by modification time.

    Args:
        logs_dir: Directory where logs are stored.
        integration_id: ID of the integration (if applicable).
        logs_type: Type of log file (e.g., "INTEGRATION", "SCHEDULER", "CELERY", "API").

    Returns:
        A list of log file paths sorted by modification time (newest first).
    """

    log_files = []

    # Handle each log type case
    if logs_type == LogsType.SCHEDULER:
        file_path = os.path.join(logs_dir, "scheduler.log")
        if os.path.isfile(file_path):
            log_files.append(file_path)

    elif logs_type == LogsType.CELERY:
        file_path = os.path.join(logs_dir, "celery.log")
        if os.path.isfile(file_path):
            log_files.append(file_path)

    elif logs_type == LogsType.API:
        file_path = os.path.join(logs_dir, "api.log")
        if os.path.isfile(file_path):
            log_files.append(file_path)

    elif logs_type == LogsType.INTEGRATION and integration_id:
        log_files = [
            os.path.join(logs_dir, file)
            for file in os.listdir(logs_dir)
            if file.startswith(integration_id) and os.path.isfile(os.path.join(logs_dir, file))
        ]

    # Sort files by modification time, newest first
    log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)

    return log_files

