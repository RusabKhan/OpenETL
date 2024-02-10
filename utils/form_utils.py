import streamlit as st
from .jdbc_engine_utils import JDBCEngine
from .sqlalchemy_engine_utils import SQLAlchemyEngine
import pandas as pd
from .local_connection_utils import store_connection_config
from .generic_utils import check_missing_values
import json
import os

"""This module contains functions related to form generation and card generation.
"""


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
            self.api_form()

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
                        filename=connection_name, json_data=json_data) if test_passed else False
                    if stored:
                        st.success('Connection created!', icon="✅")

    def create_connection(self, *args, **kwargs):
        print('args', args)
        print('kwargss', kwargs)
        print("Creating connection...")

    def api_form(self,api_name=""):
        con_data = json.loads(f"{os.getcwd()}/.local/api")
        for auth_type, auth_details in con_data["authentication_details"].items():
            if auth_type.lower() == authentication_type.lower():
                for key, value in auth_details.items():
                    if isinstance(value, str):
                        backup_key = key
                        key = key.replace("_"," ").capitalize()
                        input_label = f"{key}:" 
                        auth_value[backup_key] = st.text_input(input_label, value="", key=value) if "pass" not in input_label.lower() else st.text_input(
                            input_label, value="", type="password",key=value)
    
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
                        filename=connection_name, json_data=json_data) if test_passed else False
                    if stored:
                        st.success('Connection created!', icon="✅")


def on_button_click(button_name):
    """Set session variable 'clicked_button'. Used in connection and pipeline cards.

    Args:
        button_name (string): Name of the button clicked.
    """
    st.session_state.clicked_button = button_name


def create_button_columns(names):
    """
    Create columns of buttons.

    Args:
        names (list): A list of button names.

    """
    # Calculate the number of columns
    num_columns = 6
    # Calculate the total number of names
    num_names = len(names)
    # Calculate the number of rows required
    num_rows = (num_names + num_columns - 1) // num_columns

    # Iterate over each row
    for row in range(num_rows):
        # Create the desired number of columns
        cols = st.columns(num_columns)
        # Calculate the start and end index for names in the current row
        start_index = row * num_columns
        end_index = min(start_index + num_columns, num_names)

        # Iterate over the names in the current row
        for i in range(start_index, end_index):
            cols[i % num_columns].image("local/images/icon1.png")
            if button_clicked := cols[i % num_columns].button(
                names[i], use_container_width=True
            ):
                on_button_click(names[i])
