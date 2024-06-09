import os

# Ensure OPENETL_HOME is set before any other operations
if "OPENETL_HOME" not in os.environ:
    script_directory = os.path.dirname(os.path.abspath(__file__))
    os.environ["OPENETL_HOME"] = script_directory

import streamlit as st
from st_pages import Page, Section, show_pages, add_page_title, hide_pages

from utils import generic_utils as gu
from utils.local_connection_utils import create_con_directory
from dotenv import load_dotenv
import pandas as pd
from utils.database_utils import DatabaseUtils

gu.set_page_config(page_title="OpenETL", page_icon=None, initial_sidebar_state="expanded",
                   layout="wide", menu_items={}, page_style_state_variable="home")


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
    


col1, col2, col3, col4 = st.columns(4)

# sample data
data = {
    "Pipeline name": ["Pipeline A", "Pipeline B", "Pipeline C"],
    "Pipeline status": ["Running", "Completed", "Failed"],
    "Last run": ["2024-06-01 14:00", "2024-06-02 15:00", "2024-06-03 16:00"],
    "Scheduled run": ["2024-06-05 14:00", "2024-06-06 15:00", "2024-06-07 16:00"],
}

df = pd.DataFrame(data)

# Sample metrics for the blocks
total_api_connections = 5
total_db_connections = 10
total_pipelines = 3
total_rows_migrated = 100000

with col1:
    st.metric(label="Total API Connections", value=total_api_connections)

with col2:
    st.metric(label="Total DB Connections", value=total_db_connections)

with col3:
    st.metric(label="Total Pipelines", value=total_pipelines)

with col4:
    st.metric(label="Total Rows Migrated", value=total_rows_migrated)

st.markdown("---")  # Divider

# Displaying the dataframe below the metrics
st.subheader("Pipeline Details")
with st.container():
    st.dataframe(df, use_container_width=True, height=300,hide_index=True)


__init__()


show_pages(
    [
        Page("main.py", "Home"),
        Page("connection/create_connection.py", "Create a new connection"),
        Page("connection/connection.py", "Connections"),
        # Page("query_editor/query.py","Query Editor"),
        #Page("api/create_api.py", "Create API"),
        #Page("pipeline/pipelines.py", "My ETL"),
        Page("pipeline/create_pipelines.py", "Create ETL"),
        # Page("api/fetch_data.py","Fetch Data"),

    ]
)
