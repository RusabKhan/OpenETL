import importlib
import os
import sys
home = os.environ['OPENETL_HOME']
sys.path.append(home)
from utils.enums import *


connectors_directory = f"{home}/connectors"


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



def get_connector_auth_details(connector_name, connector_type=ConnectionType.DATABASE):
    """
    Returns the authentication details for the specified connector.

    Parameters:
        connector_name (str): The name of the connector.
        connector_type (ConnectionType): The type of connector, defaults to ConnectionType.DATABASE.

    Returns:
        dict: A dictionary containing the authentication details for the specified connector.
    """
    if connector_type == ConnectionType.DATABASE:
        path = f"{connectors_directory}/database/{connector_name}.py"
    elif connector_type == ConnectionType.API:
        path = f"{connectors_directory}/api/{connector_name}.py"
    module = import_module(connector_name, path)
    return module.authentication_details


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