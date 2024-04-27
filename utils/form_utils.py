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
from .jdbc_engine_utils import JDBCEngine
from .database_utils import DatabaseUtils
import pandas as pd
from .local_connection_utils import store_connection_config, read_api_config
from .generic_utils import check_missing_values, get_open_etl_document_connection_details
import json
import os
from utils.api_utils import test_api
from utils.enums import *
import utils.connector_utils as con_utils

"""This module contains functions related to form generation and card generation.
"""

default_img = "https://cdn5.vectorstock.com/i/1000x1000/42/09/connection-vector-28634209.jpg"


class GenerateForm():
    """
    A class which generates form.
    """

    def __init__(self, engine_type, engine):
        """Initialize GenerateForm class. 

        Args:
            type (string): database or JDBC. The type of form you wish to generate
            engine (string): Valid engine for sqlalchemy connection such as pymysql
        """
        if engine_type == ConnectionType.DATABASE:
            self.database_form(engine=engine)
        elif engine_type == "jdbc":
            self.jdbc_form(engine=engine)
        elif engine_type == ConnectionType.API:
            self.api_form(engine=engine)

    def database_form(self, engine):  # sourcery skip: raise-specific-error
        """Generate database form for sqlalchemy connections

        Args:
            engine (string): Valid engine for sqlalchemy connection such as pymysql
        """
        host = None
        username = None
        password = None
        port = None
        database = None
        connection_name = None

        with st.form('database', clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                connection_name = st.text_input(
                    'Connection name',  placeholder="demo db connection")
                host = st.text_input(
                    'Hostname',  placeholder="db.example.com")
                username = st.text_input('username',  placeholder="John Doe")
                password = st.text_input(
                    'Password',  type="password", placeholder="Top secret password. No @")
            with col2:
                port = st.number_input('port', min_value=1)
                database = st.text_input(
                    'Database',  placeholder="testDB")

            if submit := st.form_submit_button(
                "Create connection"
            ):
                check = check_missing_values(connection_name=connection_name,
                                             hostname=host, username=username, password=password, port=port, database=database, engine=engine)
                if check[0]:
                    st.error(f"{check[1]} is missing")
                else:
                    try: 
                        test_passed = DatabaseUtils(connection_name=connection_name,
                                                    hostname=host, username=username, password=password, port=port, database=database, engine=engine).test()
                    except Exception as e:
                        st.error(e)
                        
                    json_data = {"connection_credentials":{"hostname": host, "username": username, "password": password,
                                 "port": port, "database": database, "engine": engine, "connection_type": "database"},
                                 "connection_name": connection_name, "connection_type": "database"
                                 }
                    stored = DatabaseUtils(**get_open_etl_document_connection_details()).write_document(json_data)
                    if stored:
                        st.success('Connection created!', icon="✅")

    def create_connection(self, *args, **kwargs):
        print('args', args)
        print('kwargss', kwargs)
        print("Creating connection...")

    def api_form(self, engine=""):
        con_data = con_utils.get_connector_auth_details(engine, ConnectionType.API)
        auth_types = list(con_data.keys())
        auth_value = {}
        connection_name = None

        col1, col2 = st.columns(2)

        with col1:
            authentication_type = st.selectbox(
                "Authentication Type", auth_types, index=st.session_state.con_tab_selected_index_auth_types)
            st.session_state.con_tab_selected_index_auth_types = auth_types.index(
                authentication_type)
        with col2:
            connection_name = st.text_input("Connection Name", "my_api_connection")

        for auth_type, auth_details in con_data.items():
            if auth_type == authentication_type:
                for key, value in auth_details.items():
                    if isinstance(value, str):
                        backup_key = key
                        key = key.replace("_", " ").capitalize()
                        input_label = f"{key}:"
                        auth_value[backup_key] = st.text_input(input_label, value="", key=value) if "pass" not in input_label.lower() else st.text_input(
                            input_label, value="", type="password", key=value)

        test_col, save_col = st.columns(2, gap="small")

        with test_col:
            if st.button("Create Connection"):
                test = con_utils.connector_test_connection(auth_type=authentication_type, connector_type=ConnectionType.API, 
                                                       connector_name=engine, **auth_value)
                if test == True:
                    auth_value["connector_name"] = engine
                    auth_value["auth_type"] = authentication_type.value
                    
                    json_data = {"connection_credentials": auth_value,
                                 "connection_name": connection_name, "connection_type": "api"
                                 }
                    vals = get_open_etl_document_connection_details()
                    stored = DatabaseUtils(**vals).write_document(json_data)
                    if stored:
                        st.success('Connection created!', icon="✅")
                else:
                    st.error("Connection failed. Please try again. Or check the connection details.")

    def jdbc_form(self, engine):
        host = None
        username = None
        password = None
        port = None
        database = None
        connection_name = None

        with st.form('jdbc', clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                connection_name = st.text_input('Connection name',
                                                placeholder="demo db connection")
                host = st.text_input('Hostname',  placeholder="db.example.com")
                username = st.text_input('username',  placeholder="John Doe")
                password = st.text_input('Password',  type="password",
                                         placeholder="Top secret password. No @")
            with col2:
                port = st.number_input('port', min_value=1)
                database = st.text_input(
                    'Database',  placeholder="testDB")
            if submit := st.form_submit_button(
                "Create connection"
            ):
                check = check_missing_values(connection_name=connection_name,
                                             hostname=host, username=username, password=password, port=port, database=database, engine=engine)
                if check[0]:
                    st.error(f"{check[1]} is missing")
                else:
                    test_passed = JDBCEngine(connection_name=connection_name,
                                             hostname=host, username=username, password=password, port=port, database=database, engine=engine).test()

                    json_data = {"hostname": host, "username": username, "password": password,
                                 "port": port, "database": database, "engine": engine, "connection_type": "java"}
                    stored = store_connection_config(
                        connection_name=connection_name, json_data=json_data) if test_passed else False
                    if stored:
                        st.success('Connection created!', icon="✅")


def on_button_click(button_name):
    """Set session variable 'clicked_button'. Used in connection and pipeline cards.

    Args:
        button_name (string): Name of the button clicked.
    """
    st.session_state.clicked_button = button_name


def create_button_columns(names, num_columns=7):
    """
    Create columns of buttons.

    Args:
        names (list): A list of button names.

    """
    # Calculate the number of columns
    num_names = len(names)
    num_rows = (num_names + num_columns - 1) // num_columns
    for row in range(num_rows):
        cols = st.columns(num_columns)

        start_index = row * num_columns
        end_index = min(start_index + num_columns, num_names)

        for i in range(start_index, end_index):
            cols[i % num_columns].image(default_img, width=150)
            cols[i % num_columns].button(names[i], use_container_width=True)
