import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_option_menu import option_menu

from utils.local_connection_utils import read_all_connection_configs
from utils.form_utils import create_button_columns
from utils.generic_utils import set_page_config

from utils.style_utils import load_css

set_page_config(page_title="Connections", page_icon=None, initial_sidebar_state="expanded",
                layout="wide", menu_items={}, page_style_state_variable="connection_connection")
load_css()

Database = st.container()
API = st.container()


configs = read_all_connection_configs()
container_css = {
    "container": {"width": "25%", "margin": "0px !important", "font-size": "14px", "min-height": "30px", "white-space": "nowrap", "overflow": "hidden", "text-overflow": "ellipsis"}}


Database_selected = None
api_selected = None

side_col = st.columns(1)

col1, col2, col3, col4, col5, col6 = st.columns(6)


with Database:
    Database.header("Database")
    Database_names = [
        config['connection_name'] if "connection_name" in config else None
        for config in configs['database']
    ]
    create_button_columns(Database_names)


with API:
    API.header("API")
    API_names = [
        config['connection_name'] if "connection_name" in config else None
        for config in configs['api']
    ]
    create_button_columns(API_names)
