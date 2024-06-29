import streamlit as st
import pandas as pd
from console.console import get_logger

logging = get_logger()

col1, col2, col3, col4 = st.columns(4)

# sample data
data = {
    "Pipeline name": ["Pipeline A", "Pipeline B", "Pipeline C"],
    "Pipeline status": ["Running", "Completed", "Failed"],
    "Last run": ["2024-06-01 14:00", "2024-06-02 15:00", "2024-06-03 16:00"],
    "Scheduled run": ["2024-06-05 14:00", "2024-06-06 15:00", "2024-06-07 16:00"],
}

df = pd.DataFrame(data)

# Sample metrics for the blocks
total_api_connections = 5
total_db_connections = 10
total_pipelines = 3
total_rows_migrated = 100000

with col1:
    st.metric(label="Total API Connections", value=total_api_connections)

with col2:
    st.metric(label="Total DB Connections", value=total_db_connections)

with col3:
    st.metric(label="Total Pipelines", value=total_pipelines)

with col4:
    st.metric(label="Total Rows Migrated", value=total_rows_migrated)

st.markdown("---")  # Divider

# Displaying the dataframe below the metrics
st.subheader("Pipeline Details")
with st.container():
    st.dataframe(df, use_container_width=True, height=300, hide_index=True)

