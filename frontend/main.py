import os

# Ensure OPENETL_HOME is set before any other operations
if "OPENETL_HOME" not in os.environ:
    script_directory = os.path.dirname(os.path.abspath(__file__))
    os.environ["OPENETL_HOME"] = script_directory

import streamlit as st

if "style_setting_set" not in st.session_state:
    st.set_page_config(layout="wide",page_icon="utils/logo/favicon.png", page_title="OpenETL")
    st.session_state.style_setting_set = True




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
        
    if "dashboard_tab_data" not in st.session_state:
        st.session_state.dashboard_tab_data = {}
    if "dashboard_thread_started" not in st.session_state:
        st.session_state.dashboard_thread_started = False


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
    #create_con_directory()
    st.markdown(
        """
        <style>
        .block-container.st-emotion-cache-1jicfl2.ea3mdgi5 {
        padding: 3rem 1rem 10rem;
        }
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stAppDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
        
        .stStatusWidget {
            display: none;
            visibility: hidden;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
    st.logo("utils/logo/logo.png")

try:
    __init__()
except Exception as e:
    pass


current_page = st.navigation({
    "Home": [
        st.Page("home.py", title="Home", default=True, icon=":material/home:"),],
    "Connections": [
        st.Page("app/connection/create_connection.py", title="Create connection",
                icon=":material/add:"),
        st.Page("app/connection/connection.py", title="Connections",
                icon=":material/list:")
    ],
    # Page("query_editor/query.py","Query Editor"),
    # Page("api/create_api.py", "Create API"),
    # Page("pipeline/pipelines.py", "My ETL"),
    "Pipelines": [
        st.Page("app/pipeline/create_pipelines.py", title="Create ETL",
                icon=":material/add:"),
            # Page("api/fetch_data.py","Fetch Data"),

    ]}
)


current_page.run()