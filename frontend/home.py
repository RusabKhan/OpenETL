import streamlit as st
import pandas as pd

from utils.api_utils import send_request
from streamlit_autorefresh import st_autorefresh

from utils.enums import APIMethod

# Set up logging


def format_keys(data):
    formatted_data = []
    for entry in data:
        formatted_entry = {
            key.replace('_', ' ').title(): value
            for key, value in entry.items()
        }
        formatted_data.append(formatted_entry)
    return formatted_data

# Function to fetch and display data
def set_dashboard_data():
    data = send_request('database/get_dashboard_data', method=APIMethod.GET, timeout=10)

    integrations_data = format_keys(data['integrations'])

    columns = list(integrations_data[0].keys())
    
    df = pd.DataFrame(data=integrations_data, columns=columns)
    # Sample metrics for the blocks
    total_api_connections = data['total_api_connections']
    total_db_connections = data['total_db_connections']
    total_pipelines = data['total_pipelines']
    total_rows_migrated = data['total_rows_migrated']

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total API Connections", value=total_api_connections)

    with col2:
        st.metric(label="Total DB Connections", value=total_db_connections)

    with col3:
        st.metric(label="Total Pipelines", value=total_pipelines)

    with col4:
        st.metric(label="Total Rows Migrated", value=total_rows_migrated)

    st.markdown("---")  # Divider

    # Display the dataframe
    st.subheader("Pipeline Details")
    with st.container():
        st.dataframe(df, use_container_width=True, height=300, hide_index=True)

# Auto-refresh every 20 seconds
st_autorefresh(interval=80*1000, key="data_refresh")

# Fetch and display data
set_dashboard_data()
