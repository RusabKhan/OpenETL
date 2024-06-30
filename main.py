import os

# Ensure OPENETL_HOME is set before any other operations
if "OPENETL_HOME" not in os.environ:
    script_directory = os.path.dirname(os.path.abspath(__file__))
    os.environ["OPENETL_HOME"] = script_directory

import streamlit as st

from utils import generic_utils as gu
from utils.local_connection_utils import create_con_directory
from dotenv import load_dotenv
import pandas as pd
from utils.database_utils import DatabaseUtils
from console.console import get_logger

logging = get_logger()

# Redirecting stdout to a stream


def set_session():
    if "selected_pipeline_pipeline_page" not in st.session_state:
        st.session_state.selected_pipeline_pipeline_page = ""
    if "clicked_button" not in st.session_state:
        st.session_state.clicked_button = ""

    if "pipeline_tab_val" not in st.session_state:
        st.session_state.pipeline_tab_val = 1

    if "source_type_index" not in st.session_state:
        st.session_state.source_type_index = 0
    if "source_selected_index" not in st.session_state:
        st.session_state.source_selected_index = 0
    if "source_selected_schema_index" not in st.session_state:
        st.session_state.source_selected_schema_index = 0
    if "source_selected_table_index" not in st.session_state:
        st.session_state.source_selected_table_index = 0

    if "target_type_index" not in st.session_state:
        st.session_state.target_type_index = 0
    if "target_selected_index" not in st.session_state:
        st.session_state.target_selected_index = 0
    if "target_selected_schema_index" not in st.session_state:
        st.session_state.target_selected_schema_index = 0
    if "target_selected_table_index" not in st.session_state:
        st.session_state.target_selected_table_index = 0

    if "integration_selected_dates" not in st.session_state:
        st.session_state.integration_selected_dates = []
    if "integration_spark_config" not in st.session_state:
        st.session_state.integration_spark_config = {}
    if "integration_hadoop_config" not in st.session_state:
        st.session_state.integration_hadoop_config = {}
    if "integration_mapping_config" not in st.session_state:
        st.session_state.integration_mapping_config = ""

    if "api_tab_val" not in st.session_state:
        st.session_state.api_tab_val = 1
    if "api_tab_data" not in st.session_state:
        st.session_state.api_tab_data = {}
    if "api_tab_selected_index_datatypes" not in st.session_state:
        st.session_state.api_tab_selected_index_datatypes = 0
    if "api_tab_selected_index_auth_types" not in st.session_state:
        st.session_state.api_tab_selected_index_auth_types = 0

    if "con_tab_selected_index_datatypes" not in st.session_state:
        st.session_state.con_tab_selected_index_datatypes = 0
    if "con_tab_selected_index_auth_types" not in st.session_state:
        st.session_state.con_tab_selected_index_auth_types = 0
    if "con_tab_selected_con_type_index" not in st.session_state:
        st.session_state.con_tab_selected_con_type_index = 0
    if "con_tab_selected_engine_index" not in st.session_state:
        st.session_state.con_tab_selected_engine_index = 0

    if "style_setting" not in st.session_state:
        st.session_state.style_setting = {}

    load_dotenv(dotenv_path='.env')

# STYLE VARIABLES
# if "connection_create_connection_style_set" not in st.session_state:
#     st.session_state.connection_create_connecction_style_set = False
# if "connection_connection_style_set" not in st.session_state:
#     st.session_state.connection_connection_style_set = False

# if "api_create_api_style_set" not in st.session_state:
#     st.session_state.api_create_api_style_set = False

# if "pipeline_pipeline_style_set" not in st.session_state:
#     st.session_state.pipeline_pipeline_style_set = False
# if "pipeline_create_pipeline_style_set" not in st.session_state:
#     st.session_state.pipeline_create_pipeline_style_set = False


def __init__():
    set_session()
    create_con_directory()
    DatabaseUtils(engine=os.getenv('OPENETL_DOCUMENT_ENGINE'),
                hostname=os.getenv('OPENETL_DOCUMENT_HOST'),
                port=os.getenv('OPENETL_DOCUMENT_PORT'),
                username=os.getenv('OPENETL_DOCUMENT_USER'),
                password=os.getenv('OPENETL_DOCUMENT_PASS'),
                database=os.getenv('OPENETL_DOCUMENT_DB')).create_document_table()
    st.set_page_config(layout="wide",page_icon="logo/favicon.png", page_title="OpenETL")
    st.markdown(
        """
        <style>
        .block-container.st-emotion-cache-1jicfl2.ea3mdgi5 {
        padding: 3rem 1rem 10rem;
        }

        .stDeployButton {
            visibility: hidden;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
    st.logo("logo/logo.png")


__init__()


current_page = st.navigation({
    "Home": [
        st.Page("Home.py", title="Home", default=True, icon=":material/home:"),],
    "Connections": [
        st.Page("connection/create_connection.py", title="Create a new connection",
                icon=":material/add:"),
        st.Page("connection/connection.py", title="Connections",
                icon=":material/list:")
    ],
    # Page("query_editor/query.py","Query Editor"),
    # Page("api/create_api.py", "Create API"),
    # Page("pipeline/pipelines.py", "My ETL"),
    "Pipelines": [
        st.Page("pipeline/create_pipelines.py", title="Create ETL",
                icon=":material/add:"),
        st.Page("console/console.py", title="Console",
                icon=":material/terminal:"),
            # Page("api/fetch_data.py","Fetch Data"),

    ]}
)


current_page.run()