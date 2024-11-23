"""This module contains utilitiy functions which can be used in particular case and are not relevant to any one scenario.
"""
from .database_utils import DatabaseUtils
from .local_connection_utils import read_connection_config
import streamlit as st
from .jdbc_engine_utils import JDBCEngine
from utils import connector_utils


def set_page_config(page_title="OpenETL", menu_items={}, initial_sidebar_state="expanded", page_icon=None, layout="wide", page_style_state_variable=None):
    """
    Sets the page configuration for a Streamlit application.

    Parameters:
        page_title (str): The title of the page. Defaults to "OpenETL".
        menu_items (dict): A dictionary representing the menu items. Defaults to an empty dictionary.
        initial_sidebar_state (str): The initial state of the sidebar. Can be "expanded" or "collapsed". Defaults to "expanded".
        page_icon (str): The URL of the page icon. Defaults to None.
        layout (str): The layout of the page. Can be "wide" or "centered". Defaults to "wide".
        page_style_state_variable (str): The state variable used to check if the page style is already set. Defaults to None.

    Returns:
        None
    """
    is_set = bool(st.session_state.get(page_style_state_variable)) 
    if not is_set:
        st.set_page_config(page_title=page_title, page_icon=page_icon,
                           initial_sidebar_state=initial_sidebar_state, layout=layout, menu_items=menu_items)
        st.session_state[page_style_state_variable] = True


def extract_connections_db_or_api(db_or_api, configs):
    """Get connections from config variable and divide them into a list of python/java based connections.

    Args:
        py_or_java (string): Python or Java. The connections type to be fetched from config variable.
        configs (list): list of configurations

    Returns:
        _type_: list
    """
    options = []
    if db_or_api == "database":
        for config in configs['database']:
            options.append(config["connection_name"]) if config["connection_type"] == "database" else None
    elif db_or_api == "api":
        for config in configs['api']:
            options.append(config["connection_name"]) if config["connection_type"] == "api" else None
    return options


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
            module = connector_utils.import_module(data["connection_name"], f"{connector_utils.connectors_directory}/{connection_type}/{data['connector_name']}.py")
            auth_details = main_data["connection_credentials"]
            return module.get_metadata(**auth_details)
                    
    except Exception as e:
        st.error("Data does not exist for selected type of connection")
        return {"tables": [], "schema": []}


def execute(connection, query, is_java=False):
    """Execute a query on the given connection

    Args:
        connection (string): Name of the connection 
        query (string): The query to execute

    Returns:
        Dataframe: Database response in dataframe
    """
    metadata = read_connection_config(connection)['data']

    if is_java:
        return JDBCEngine(**metadata).execute_query(query)
    return DatabaseUtils(**metadata).execute_query(query)


def check_missing_values(**kwargs):
    """Check on submit connection if any form field is missing values.

    Returns:
        tuple: Boolean value indicating whether a key is missing value and the key. For e.g if hostname is null, True, hostname. Else False,None
    """
    for key, value in kwargs.items():
        if len(str(value)) < 1:
            return True,  key
    return False, None
 
 
 
