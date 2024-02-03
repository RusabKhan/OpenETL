import streamlit as st
import json
import xml.etree.ElementTree as ET
from utils.api_utils import parse_json, parse_xml
from streamlit_ace import st_ace
import extra_streamlit_components as stx

st.set_page_config(page_title="Create API", page_icon=None,
                           initial_sidebar_state="expanded", layout="wide", menu_items={})

tab_items = [
    stx.TabBarItemData(id=1, title="Add API",
                       description="Create A Source"),
    stx.TabBarItemData(id=2, title="Test", description="Test Your Connection"),
]

global val
val = stx.tab_bar(
    data=tab_items, default=st.session_state.api_tab_val, return_type=int)

st.markdown(
    """
    <style>
    .css-z5fcl4 {
        padding-top: 3rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


class Create_API:
    def __init__(self):
        self.data = None

    def file_uploader_design(self):
        # File upload
        uploaded_file = st.file_uploader(
            "Upload JSON or XML file", type=["json", "xml"])

        if uploaded_file:
            file_content = uploaded_file.getvalue().decode("utf-8")

            # Determine file type
            file_extension = uploaded_file.name.split(".")[-1]

            # Parse based on file type
            if file_extension == "json":
                self.data = parse_json(file_content)
            elif file_extension == "xml":
                self.data = parse_xml(file_content)
            else:
                st.error("Unsupported file format")
                return


    def manual_design(self):

        col1, col2, col3 = st.columns([1,2,2])
        
        xml_or_json = None
        with col1:
            xml_or_json = st.radio("Choose input format", ("JSON", "XML"))
            val = "{\"table\": \"endpoint\"}" if xml_or_json == "JSON" else "<table>endpoint</table>"
        with col2:
            api_name = st.text_input("API Name", "my_api")
        with col3:
            authentication_type = st.selectbox(
                "Authentication Type", ("Basic", "OAuth2"))

            # Manual input
        input_table = st_ace(val, height=350,
                             language=xml_or_json.lower(), theme='twilight', wrap=True, auto_update=False)

        print(input_table)

        if xml_or_json == "XML":
            self.data = parse_xml(input_table) if input_table else None
        else:
            self.data = parse_json(input_table)if input_table else None


    def next_back_buttons(self):
        slide_col1, slide_col2 = st.columns([4, 1])

        with slide_col2:
            sub_col1, sub_col2 = st.columns(2, gap="small")
            with sub_col1:
                if st.button("Back") and int(val) > 1:
                    st.session_state.api_tab_val = val-1
                    st.experimental_rerun()
            with sub_col2:
                if st.button("Next") and int(val) < len(tab_items):
                    st.session_state.api_tab_val = val+1
                    st.experimental_rerun()
    
    
    def submit_data_for_processing(self,data,is_json=True):
        st.write(self.data)
    




def main():
    
    create_api = Create_API()

    if val == 1:
        with st.expander("Upload Tables From File",expanded=True):
            create_api.file_uploader_design()
            
        with st.expander("Add Tables Manually"):
            create_api.manual_design()
            
    if val == 2:
        create_api.submit_data_for_processing(create_api.data)
        
    
    create_api.next_back_buttons()
    
main()