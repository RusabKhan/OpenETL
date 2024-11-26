import importlib
import os
import sys
home = os.environ['OPENETL_HOME']
sys.path.append(home)
import json
from utils.database_utils import DatabaseUtils, OpenETLDocument
from utils.enums import *
import streamlit as st


connectors_directory = f"{home}/connectors"

@st.cache_data(ttl=int(os.environ.get("OPENETL_CACHE_TTL")))
def get_installed_connectors(connector_type=ConnectionType.DATABASE):
    """
    Checks the available connectors based on the specified connector type.

    Parameters:
        connector_type (ConnectionType): The type of connector to check, defaults to ConnectionType.DATABASE.

    Returns:
        list: A list of available connectors based on the specified connector type.
    """
    files = None
    if connector_type == ConnectionType.DATABASE:
        files = os.listdir(f"{connectors_directory}/database")
    elif connector_type == ConnectionType.API:
        files = os.listdir(f"{connectors_directory}/api")
        
    return [file.replace('.py', '') for file in files if file.endswith('.py')]


@st.cache_data(ttl=int(os.environ.get("OPENETL_CACHE_TTL")))
def get_connector_auth_details(connector_name, connector_type=ConnectionType.DATABASE):
    """
    Returns the authentication details for the specified connector.

    Parameters:
        connector_name (str): The name of the connector.
        connector_type (ConnectionType): The type of connector, defaults to ConnectionType.DATABASE.

    Returns:
        dict: A dictionary containing the authentication details for the specified connector.
    """
    path = None
    if connector_type == ConnectionType.DATABASE:
        path = f"{connectors_directory}/database/{connector_name}.py"
    elif connector_type == ConnectionType.API:
        path = f"{connectors_directory}/api/{connector_name}.py"
    module = import_module(connector_name, path)
    return module.authentication_details


def get_db_connector_engine(connector_name):
    path = f"{connectors_directory}/database/{connector_name}.py"
    module = import_module(connector_name, path)
    return module.engine

def import_module(module_name, module_path, class_name="Connector", *args, **kwargs):
    """
    Imports a module and initializes a class within it.

    Args:
        module_name (str): The name of the module (without the .py extension).
        class_name (str): The name of the class to initialize.
        *args: Positional arguments to pass to the class constructor.
        **kwargs: Keyword arguments to pass to the class constructor.

    Returns:
        object: An instance of the initialized class.
    """
    try:
        # Import the module
        if os.path.exists(module_path):
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Get the class from the module
            class_ = getattr(module, class_name)

            # Initialize the class with provided arguments
            instance = class_(*args, **kwargs)

            return instance
    except ImportError as e:
        print(f"Error: Module '{module_name}' not found. {str(e)}.")
    except AttributeError as e:
        print(
            f"Error: Class '{class_name}' not found in module '{module_name}'. {str(e)}.")
    except Exception as e:
        print(
            f"Error initializing class '{class_name}' from module '{module_name}': {str(e)}.")


def connector_test_connection(connector_name, connector_type=ConnectionType.DATABASE, auth_type=AuthType.BASIC, **auth_params):
    """
    Tests the connection to the specified connector.

    Args:
        connector_name (str): The name of the connector.
        connector_type (ConnectionType): The type of connector, defaults to ConnectionType.DATABASE.

    Returns:
        bool: True if the connection is successful, False otherwise.
    """
    try:
        if connector_type == ConnectionType.DATABASE:
            path = f"{connectors_directory}/database/{connector_name}.py"
            module = import_module(connector_name, path)
            module.create_engine(**auth_params)
            return module.test_connection()
        
        elif connector_type == ConnectionType.API:
            path = f"{connectors_directory}/api/{connector_name}.py"
            module = import_module(connector_name, path)
            api_session = module.connect_to_api(auth_type=auth_type, **auth_params)
            return module.test_connection(api_session)
    except Exception as e:
        print(f"Error: {str(e)}")
        
@st.cache_data(ttl=int(os.environ.get("OPENETL_CACHE_TTL")))
def get_connector_metadata(connector_name, connector_type=ConnectionType.DATABASE.value):
    """
    Returns the metadata for the specified connector.

    Args:
        connector_name (str): The name of the connector.
        connector_type (ConnectionType): The type of connector, defaults to ConnectionType.DATABASE.

    Returns:
        dict: A dictionary containing the metadata for the specified connector.
    """
    if connector_type == ConnectionType.DATABASE.value:
        path = f"{connectors_directory}/database/{connector_name}.py"
    elif connector_type == ConnectionType.API.value:
        path = f"{connectors_directory}/api/{connector_name}.py"
    module = import_module(connector_name, path)
    return module.get_metadata()

def get_created_connections(connector_type=ConnectionType.DATABASE.value, connection_name = None) -> list:
    """
    Returns a list of created connections for the specified connector type.

    Args:
        connector_type (ConnectionType): The value of type of connector, defaults to ConnectionType.DATABASE.value

    Returns:
        list: A list of created connections.
    """
    return json.loads(DatabaseUtils(engine=os.getenv("OPENETL_DOCUMENT_ENGINE"),
                               hostname=os.getenv("OPENETL_DOCUMENT_HOST"),
                               port=os.getenv("OPENETL_DOCUMENT_PORT"),
                               username=os.getenv("OPENETL_DOCUMENT_USER"),
                               password=os.getenv("OPENETL_DOCUMENT_PASS"),
                               database=os.getenv("OPENETL_DOCUMENT_DB")).get_created_connections(connector_type=connector_type, connection_name = connection_name).to_json(orient='records'))
    
@st.cache_data(ttl=int(os.environ.get("OPENETL_CACHE_TTL")))
def fetch_metadata(connection, auth_options, connection_type):
    """Fetch metadata from the given connection.

    Args:
        connections (string): name of the connection 

    Returns:
        dict: {"tables": [],"schema":[]}
    """
    try:
        main_data = None
        for data in auth_options:
            if data["connection_name"] == connection:
                main_data = data
                module = import_module(data["connection_name"], f"{connectors_directory}/{connection_type}/{data['connector_name']}.py")
                auth_details = main_data["connection_credentials"]
        return module.get_metadata(**auth_details)
                    
    except Exception as e:
        st.error("Data does not exist for selected type of connection")
        return {"tables": [], "schema": []}
    
    
@st.cache_data
def get_connector_image(connector_name,connection_type):
    """Fetch metadata from the given connection.

    Args:
        connections (string): name of the connection 

    Returns:
        dict: {"tables": [],"schema":[]}
    """
    try:
        module = import_module(connector_name, f"{connectors_directory}/{connection_type}/{connector_name}.py")
        return module.logo
                    
    except Exception as e:
        print(f"Error: {str(e)}")
        return "https://cdn5.vectorstock.com/i/1000x1000/42/09/connection-vector-28634209.jpg"



def fetch_data_from_connector(connection_name, connection_type, table, schema="public",page_limit = 10000):
    """
    Fetches data from a connector based on the provided connection details.

    Args:
        connection_name (str): The name of the connection.
        connection_type (str): The type of the connection.
        table (str): The name of the table to fetch data from.
        schema (str, optional): The schema of the table. Defaults to "public".
        page_limit (int, optional): The maximum number of pages to fetch. Defaults to 10000.

    Returns:
        None
    """
    connector_details = get_created_connections(connection_type, connection_name=connection_name)[0]
    connector_name = connector_details['connector_name']
    auth_type = AuthType(connector_details['auth_type']['value'])
    auth_params = connector_details['connection_credentials']
    module = import_module(connector_name, f"{connectors_directory}/{connection_type}/{connector_name}.py")
    if connection_type == "api":
        api_session = module.connect_to_api(auth_type=auth_type, **auth_params)
        arr = []
        for page in module.fetch_data(api_session, table):
            yield module.return_final_df(page) # apply yield here to with page_limit 
    elif connection_type == "database":
        module.create_engine(**auth_params)
        yield module.read_table(table)
    


# if __name__ == "__main__":
#     source_connection = {'table': 'get_all_contacts', 'schema': 'public', 'connection_type': 'api', 
#                          'connection_name': 'my_connection'}
    

#     fetch_data_from_connector("my_connection", "api", "get_all_contacts","public")