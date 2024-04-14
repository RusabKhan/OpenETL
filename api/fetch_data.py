import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_option_menu import option_menu

from utils.local_connection_utils import read_connection_configs
from utils.form_utils import create_button_columns
from utils.generic_utils import set_page_config
from utils.api_utils import get_data
from utils.enums import *


configs = read_connection_configs()


API_names = [
    config['connection_name'] if "connection_name" in config else None
    for config in configs['api']
]
create_button_columns(API_names)

df = get_data("get_all_contacts","hubspot",AuthType.BEARER )
st.data_editor(df)