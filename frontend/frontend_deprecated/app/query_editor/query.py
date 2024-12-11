import streamlit as st
from utils.local_connection_utils import read_connection_configs
from utils.generic_utils import (
    extract_connections_db_or_api,
    fetch_metadata,
    execute,
    
)
import pandas as pd
#from pandas_profiling import ProfileReport
from streamlit_ace import st_ace


configs = read_connection_configs()

global options
options = []


connections = ""

global metadata
global df

metadata = {"schema": [], "tables": []}
query = ""


if "query_df" not in st.session_state:
    st.session_state["query_df"] = pd.DataFrame()


#query_tab, graph_tab = st.tabs(["Query", "Graph"])


def paginate_dataframe(df=st.session_state["query_df"], page_size=5, page_number=1):
    start = (page_number - 1) * page_size
    end = page_number * page_size
    return df.iloc[start:end]


df = None
paginated_ = pd.DataFrame()
page_number = 1
df_empty = True

#with query_tab:
col1, col2 = st.columns([4, 2])

#with st.container():
with col1:
    db_or_api = st.radio(
        "Choose type", ["Database", "API"], horizontal=True)
    options = extract_connections_db_or_api(db_or_api, configs)

    connections = st.selectbox(
        "Select connection to use", options=options)
    query = st_ace(
            placeholder="Write your SQL query here...",
            language="sql",
            theme="twilight",
            font_size=14,
            key="darkmode"
        )
    metadata = fetch_metadata(connections)

    prev_button_col, next_button_col = col1.columns(
        [4, 4]
    )
    
    if query:
        is_java = True if db_or_api == "Java" else False
        df = execute(connection=connections,
                        query=query, is_java=is_java)
        st.session_state["query_df"] = df
        paginated_ = paginate_dataframe(df)
        df_empty = False
    with prev_button_col:
        if st.button("Prev", disabled=df_empty):
            paginated_ = paginate_dataframe(
                page_number=page_number - 1)
            page_number -= 1 if page_number > 1 else page_number
    with next_button_col:
        if st.button("Next", disabled=df_empty):
            paginated_ = paginate_dataframe(
                page_number=page_number + 1)
            page_number += 1 if page_number < len(df) / \
                5 else page_number
    st.dataframe(paginated_)

with col2:
    st.write("Table Metadata")
    for data in metadata["schema"]:
        html_list = '<ul style="overflow-y:scroll;overflow-x:hidden;font-size:6px;max-height:300px">\n'
        with st.expander(data):
            lst = metadata["tables"][metadata["schema"].index(data)]
            for item in lst:
                html_list += f' <li style="font-size:15px">{item}</li>\n'
            html_list += "</ul>"
            st.markdown(html_list, unsafe_allow_html=True)


# with graph_tab:
#     if st.button("Download profile report"):
#         df = st.session_state["query_df"]
#         profile = ProfileReport(df, progress_bar=True)
#         profile.to_file(f".local/profile_reports/{datetime.now()}.html")
#     choice = st.selectbox("Chart type", ["Bar", "Line", "Area"])
#     df = st.session_state["query_df"]
#     if st.button("Create chart"):
#         if choice == "Bar":
#             st.bar_chart(df)
#         elif choice == "Line":
#             st.line_chart(df)
#         elif choice == "Area":
#             st.area_chart(df)
