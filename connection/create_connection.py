# sourcery skip: avoid-builtin-shadow
import streamlit as st
from utils.form_utils import GenerateForm
from local.cache import *
from utils.style_utils import load_css
from utils.local_connection_utils import read_all_apis
from utils.generic_utils import set_page_config

set_page_config(page_title="Create Connection", page_icon=None, initial_sidebar_state="expanded",
                layout="wide", menu_items={}, page_style_state_variable="connection_create_connection")

load_css()


global type_, engine, gen
page = st.container()
type_ = None
engine = None
gen = None

col1, col2 = st.columns([1, 1])
sqlalchemy_sources = tuple(sqlalchemy_database_engines.keys())
api_engines = read_all_apis()

type_values = ("Database", "API")

type_ = None

with col1:
    type_ = st.selectbox(
        "Select connection type",
        type_values
    )

with col2:
    msg = "Select Database" if type_ == "Database" else "Select API"
    vals = sqlalchemy_sources if type_ == "Database" else api_engines

    engine = st.selectbox(
        msg,
        vals
    )

if type_ == "Database":
    gen = GenerateForm("database", engine=engine)


elif type_ == "API":
    gen = GenerateForm("api", engine=engine)
