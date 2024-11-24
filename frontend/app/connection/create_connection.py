# sourcery skip: avoid-builtin-shadow
import streamlit as st

from utils.api_utils import send_request
from utils.form_utils import GenerateForm
from utils.enums import ConnectionType, APIMethod

global type_, engine, gen
page = st.container()
type_ = None
engine = None
gen = None

col1, col2 = st.columns([1, 1])
main_set_engines = send_request('connector/get_installed_connectors/',
                                method=APIMethod.GET, timeout=10)

database_engines = main_set_engines['database']
api_engines = main_set_engines['api']

type_values = ("Database", "API")

type_ = None

with col1:
    type_ = st.selectbox(
        "Select connection type",
        type_values
    )

with col2:
    msg = "Select Database" if type_ == "Database" else "Select API"
    vals = database_engines if type_ == "Database" else api_engines

    engine = st.selectbox(
        msg,
        vals
    )

if type_ == "Database":
    gen = GenerateForm(ConnectionType.DATABASE, engine=engine)


elif type_ == "API":
    gen = GenerateForm(ConnectionType.API, engine=engine)
