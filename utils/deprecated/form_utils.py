"""
This module contains utility functions related to form generation.

Functions:
- GenerateForm: A class that generates different types of forms based on the specified parameters.
- database_form: Generates a database form for SQLAlchemy connections.
- create_connection: Creates a new connection based on the provided arguments.
- api_form: Generates an API form based on the specified engine.
- jdbc_form: Generates a JDBC form based on the specified engine.
"""
import streamlit as st

from utils.deprecated.api_utils import send_request
from utils.enums import *

"""This module contains functions related to form generation and card generation.
"""

class GenerateForm():
    """
    A class that generates a form based on the specified engine type and engine.

    Attributes:
    - engine_type (string): Type of the engine, either 'database' or 'JDBC'.
    - engine (string): Valid engine for SQLAlchemy connection, such as 'pymysql'.

    Methods:
    - __init__: Initializes the GenerateForm class with the engine type and engine.
    - create_connection: Prints the arguments and keyword arguments, simulating the creation of a connection.
    - connection_form: Generates a form for creating a connection based on the engine type and engine provided.
    """

    def __init__(self, engine_type, engine):
        """Initialize GenerateForm class. 

        Args:
            type (string): database or JDBC. The type of form you wish to generate
            engine (string): Valid engine for sqlalchemy connection such as pymysql
        """
        self.connection_form(engine,engine_type)

    def create_connection(self, *args, **kwargs):
        print('args', args)
        print('kwargss', kwargs)
        print("Creating connection...")

    def connection_form(self, engine="",engine_type=""):
        con_data = send_request("connector/get_connector_auth_details/{}/{}".format(engine,engine_type.value), method=APIMethod.GET, timeout=10)
        auth_types = list(con_data.keys())
        auth_value = {}
        connection_name = None
        authentication_type = None
        stored = None

        col1, col2 = st.columns(2)

        with col1:
                authentication_type = st.selectbox(
                    "Authentication Type", auth_types, index=st.session_state.con_tab_selected_index_auth_types)
                st.session_state.con_tab_selected_index_auth_types = auth_types.index(
                    authentication_type)
        with col2:
            connection_name = st.text_input("Connection Name", "my_connection")

        col1, col2 = st.columns(2)
        current_col = col1
        for auth_type, auth_details in con_data.items():
            if auth_type == authentication_type:
                for i, (key, value) in enumerate(auth_details.items()):
                    if i % 2 == 0:
                        current_col = col1
                    else:
                        current_col = col2

                    with current_col:
                        backup_key = key    
                        key = key.replace("_", " ").capitalize()
                        input_label = f"{key}:"
                        
                        if isinstance(value, str):
                            auth_value[backup_key] = st.text_input(input_label, value="", key=backup_key) if "pass" not in input_label.lower() else st.text_input(
                                input_label, value="", type="password", key=backup_key)
                        elif isinstance(value, int):
                            auth_value[backup_key] = st.number_input(input_label, value=value, key=backup_key)

        test_col, save_col = st.columns(2, gap="small")

        with test_col:
            if st.button("Create Connection"):
                data={"auth_type":authentication_type, "connector_type":engine_type.value, 
                                                       "connector_name":engine, "auth_params":auth_value}
                
                test = send_request("connector/test_connection",
                                    method=APIMethod.POST, json=data, timeout=10)
                if test == True:

                    
                    json_data = {"connection_credentials": auth_value,"connector_name": engine, "auth_type": authentication_type
                                 ,"connection_name": connection_name, "connection_type": engine_type.value
                                 }
                    test_conn_request_data = {"auth_params": auth_value, "connector_name": engine,
                                              "auth_type": authentication_type, "connector_type": engine_type.value}
                    if send_request("connector/test_connection", method=APIMethod.POST, json=test_conn_request_data, timeout=10) == True:
                        stored = send_request("connector/store_connection", method=APIMethod.POST, json=json_data, timeout=10)
                    if stored[0]:
                        st.success('Connection created!', icon="✅")
                    else:
                        st.error(f"Connection failed. Please try again. Or check the connection details:{stored[1]}",icon="❌")
                else:
                    st.error("Connection failed. Please try again. Or check the connection details:")


def on_button_click(button_name):
    """Set session variable 'clicked_button'. Used in connection and pipeline cards.

    Args:
        button_name (string): Name of the button clicked.
    """
    st.session_state.clicked_button = button_name


def create_button_columns(data,connection_type, num_columns=5):
    """
    Create columns of buttons.

    Args:
        names (list): A list of button names.

    """
    # Calculate the number of columns
    num_names = len(data)
    num_rows = (num_names + num_columns - 1) // num_columns
    
    for row in range(num_rows):
        cols = st.columns(num_columns)
        
        start_index = row * num_columns
        end_index = min(start_index + num_columns, num_names)
        
        for i in range(start_index, end_index):
            url = "connector/get_connector_image/{}/{}".format(data[i]['connector_name'],connection_type)
            default_img = send_request(url, method=APIMethod.GET, timeout=10)
            with cols[i % num_columns]:
                # Creating a container for the image and button
                    st.image(default_img, width=100)
                    st.button(data[i]['connection_name'], key="{}{}{}".format(connection_type,data[i]['connector_name'],i))

