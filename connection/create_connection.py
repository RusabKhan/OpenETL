# sourcery skip: avoid-builtin-shadow
import streamlit as st
from utils.form_utils import GenerateForm
from utils.cache import *
from utils.connector_utils import get_installed_connectors
from utils.enums import *
from console.console import get_logger

logging = get_logger()
# set_page_config(page_title="Create Connection", page_icon=None, initial_sidebar_state="expanded",
#                 layout="wide", menu_items={}, page_style_state_variable="connection_create_connection")

# 


global type_, engine, gen
page = st.container()
type_ = None
engine = None
gen = None

col1, col2 = st.columns([1, 1])
database_sources = get_installed_connectors(ConnectionType.DATABASE)
api_engines = get_installed_connectors(ConnectionType.API)

type_values = ("Database", "API")

type_ = None

with col1:
    type_ = st.selectbox(
        "Select connection type",
        type_values
    )

with col2:
    msg = "Select Database" if type_ == "Database" else "Select API"
    vals = database_sources if type_ == "Database" else api_engines

    engine = st.selectbox(
        msg,
        vals
    )

if type_ == "Database":
    gen = GenerateForm(ConnectionType.DATABASE, engine=engine)


elif type_ == "API":
    gen = GenerateForm(ConnectionType.API, engine=engine)
