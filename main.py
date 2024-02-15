import streamlit as st
from st_pages import Page, Section, show_pages, add_page_title, hide_pages
import utils.generic_utils as gu
from utils.local_connection_utils import create_con_directory
from utils.style_utils import load_css

gu.set_page_config(page_title="AppX",page_icon=None,initial_sidebar_state="expanded",layout="wide",menu_items={})


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


def __init__():
    set_session()
    create_con_directory()
    load_css()



__init__()



show_pages(
    [
        Page("main.py", "Home"),
        Page("connection/create_connection.py","Create a new connection"),
        Page("connection/connection.py", "Connections"),
        #Page("query_editor/query.py","Query Editor"),  
        Page("api/create_api.py","Create API"),
        Page("pipeline/pipelines.py","My ETL"),      
        Page("pipeline/create_pipelines.py","Create ETL"),
        #Page("api/fetch_data.py","Fetch Data"),

    ]
)

