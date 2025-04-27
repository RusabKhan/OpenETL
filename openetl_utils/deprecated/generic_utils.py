"""This module contains utilitiy functions which can be used in particular case and are not relevant to any one scenario.
"""
from openetl_utils.database_utils import DatabaseUtils
from openetl_utils.local_connection_utils import read_connection_config
import streamlit as st
from openetl_utils.deprecated.jdbc_engine_utils import JDBCEngine
from openetl_utils import connector_utils


def set_page_config(page_title="OpenETL", menu_items={}, initial_sidebar_state="expanded", page_icon=None, layout="wide", page_style_state_variable=None):
    """
    Configures the Streamlit application page settings if they have not been previously set.
    
    This function sets up various page parameters such as title, icon, layout, sidebar state, and custom menu items for a Streamlit app.
    If a session state variable is provided via page_style_state_variable and is already set in st.session_state, the configuration is not reapplied,
    ensuring that the setup occurs only once per session.
    
    Parameters:
        page_title (str): The title displayed on the browser tab. Defaults to "OpenETL".
        menu_items (dict): A dictionary of custom menu items for the app's menu. Defaults to an empty dictionary.
        initial_sidebar_state (str): The initial state of the sidebar; either "expanded" or "collapsed". Defaults to "expanded".
        page_icon (str): The URL or emoji representing the page icon. Defaults to None.
        layout (str): The layout mode of the page; either "wide" or "centered". Defaults to "wide".
        page_style_state_variable (str, optional): A key for a session state variable used to track whether the page configuration has already been applied.
                                                   If this variable exists and is truthy in st.session_state, the configuration will not be set again.
    
    Returns:
        None
    
    Example:
        set_page_config(
            page_title="MyApp",
            menu_items={"Get Help": "https://example.com/help"},
            initial_sidebar_state="collapsed",
            page_icon=":smile:",
            layout="centered",
            page_style_state_variable="page_configured"
        )
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
 
 
 
