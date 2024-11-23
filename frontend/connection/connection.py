import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_option_menu import option_menu

from utils.api_utils import send_request
from utils.local_connection_utils import read_all_connection_configs
from utils.form_utils import create_button_columns
from utils.connector_utils import get_created_connections
from utils.enums import *




Database = st.container()
API = st.container()


database_configs = send_request('http://localhost:5009/connector/get_created_connections',
                                method=APIMethod.POST,
                                timeout=10,
                                json={"connector_type": ConnectionType.DATABASE.value, "connector_name": None})
api_configs = send_request('http://localhost:5009/connector/get_created_connections',
                                method=APIMethod.POST,
                                timeout=10,
                                json={"connector_type": ConnectionType.API.value, "connector_name": None})


Database_selected = None
api_selected = None

side_col = st.columns(1)

col1, col2, col3, col4, col5, col6 = st.columns(6)


with Database:
    Database.header("Database")
    create_button_columns(database_configs,ConnectionType.DATABASE.value)


with API:
    API.header("API")
    create_button_columns(api_configs,ConnectionType.API.value)
