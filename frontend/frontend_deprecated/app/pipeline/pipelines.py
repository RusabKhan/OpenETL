import streamlit as st

from utils.deprecated.api_utils import send_request
from utils.enums import APIMethod
from utils.local_connection_utils import read_pipeline_detals
from utils.deprecated.form_utils import create_button_columns





Pipelines = st.container()
Java = st.container()

configs = send_request('get_pipeline_data', method=APIMethod.GET, timeout=10)


if st.session_state.clicked_button in configs:
    st.session_state.selected_pipeline_pipeline_page = st.session_state.clicked_button
else:
    st.session_state.selected_pipeline_pipeline_page = configs[0] if len(
        configs) > 0 else {}


def kpi_generator(col, title, metric):
    with col:
        st.metric(title, metric)


side_col = st.columns(1)

col1, col2, col3, col4, col5, col6 = st.columns(6)

details = {}

with Pipelines:
    Pipelines.header("Pipelines")
    create_button_columns(configs)

col1, col2, col3, col4, col5 = st.columns(5)

if len(configs) > 0:
    arr = []
    details = read_pipeline_detals(
        st.session_state.selected_pipeline_pipeline_page)
    
    arr = list(details.keys())
        

    select_run_date = st.selectbox("Select Run Date", options=arr)
    run_details = details[select_run_date]
    

    
    kpi_generator(col1, "Rows Read", run_details["rows_read"])
    kpi_generator(col2, "Rows Write", run_details["rows_write"])
    kpi_generator(col3, "Start Time", run_details["start_time"])
    kpi_generator(col4, "End Time", run_details["end_time"])
    kpi_generator(col5, "Status", run_details["status"])
