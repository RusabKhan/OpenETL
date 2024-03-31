import streamlit as st
from .jdbc_engine_utils import JDBCEngine
from .sqlalchemy_engine_utils import SQLAlchemyEngine
import pandas as pd
from .local_connection_utils import store_connection_config, read_api_config
from .generic_utils import check_missing_values
import json
import os
from utils.api_utils import test_api

"""This module contains functions related to form generation and card generation.
"""

default_img = "https://cdn5.vectorstock.com/i/1000x1000/42/09/connection-vector-28634209.jpg"

class GenerateForm():
    """
    A class which generates form.
    """

    def __init__(self, type, engine):
        """Initialize GenerateForm class. 

        Args:
            type (string): database or JDBC. The type of form you wish to generate
            engine (string): Valid engine for sqlalchemy connection such as pymysql
        """
        if type == "database":
            self.database_form(engine=engine)
        elif type == "jdbc":
            self.jdbc_form(engine=engine)
        elif type == "api":
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
                    test_passed = SQLAlchemyEngine(connection_name=connection_name,
                                                   hostname=host, username=username, password=password, port=port, database=database, engine=engine).test()

                    json_data = {"hostname": host, "username": username, "password": password,
                                 "port": port, "database": database, "engine": engine, "connection_type": "database"}
                    stored = store_connection_config(
                        connection_name=connection_name, json_data=json_data) if test_passed else False
                    if stored:
                        st.success('Connection created!', icon="✅")

    def create_connection(self, *args, **kwargs):
        print('args', args)
        print('kwargss', kwargs)
        print("Creating connection...")

    def api_form(self, engine=""):
        con_data = read_api_config(engine)
        auth_types = list(con_data['authentication_details'].keys())
        auth_value = {}
        api_name = None

        col1, col2 = st.columns(2)

        with col1:
            authentication_type = st.selectbox(
                "Authentication Type", auth_types, index=st.session_state.con_tab_selected_index_auth_types)
            st.session_state.con_tab_selected_index_auth_types = auth_types.index(
                authentication_type)
        with col2:
            api_name = st.text_input("Connection Name", "my_api_connection")

        for auth_type, auth_details in con_data["authentication_details"].items():
            if auth_type.lower() == authentication_type.lower():
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
                auth_value['base_url'] = con_data['base_url']
                con_data['api'] = engine
                auth_value['api'] = engine
                resp = test_api(con_type=authentication_type.lower(),
                            data=auth_value)
                if resp["status_code"] == 200:
                    st.success("Connection Successful")
                    con_data['schema'] = 'public'
                    con_data['database'] = 'public'
                    con_data['auth_types'] = authentication_type.lower()
                    con_data['auth_values'] = auth_value

                    store_connection_config(
                        connection_name=api_name, json_data=con_data, is_api=False)
                else:
                    st.error(resp)
                    

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


def create_button_columns(names,num_columns=7):
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

