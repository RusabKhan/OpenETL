"""This module contains functions related to store managing and retrieving information from .local folder.
"""
import os
import json


directory = f'{os.getcwd()}/.local'
pipelines_directory = f"{directory}/pipelines"
connections_directory = f"{directory}/connections"
profile_reports = f"{directory}/profile_reports"
# jars_directory = f"{directory}/jars"
api_directory = f"{directory}/api"

dirs = [directory, pipelines_directory,
        connections_directory, profile_reports, api_directory]
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
