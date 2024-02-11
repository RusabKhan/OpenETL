import streamlit as st
import json
from utils.api_utils import parse_json, parse_xml, test
from streamlit_ace import st_ace
import extra_streamlit_components as stx
from utils.local_connection_utils import store_connection_config
from utils.generic_utils import set_page_config


set_page_config(page_title="Create API",page_icon=None,initial_sidebar_state="expanded",layout="wide",menu_items={})



global dump_data, con_data
dump_data = {
  "img": "",
  "base_url": "https://myapi/v1/endpoint",
  "authentication_details": {
    "basic": {
      "username_api_key": "username",
      "password_api_key": "password"
    },
    "oauth2": {
      "client_id_api_key": "client_id",
      "client_secret_api_key": "client_secret",
      "refresh_token_api_key": "refresh_token",
      "redirect_uri_api_key": "redirect_uri"
    },
    "bearer": {
      "token_api_key": "bearer_token"
    }
  },
  "tables": {
    "table1": "url1",
    "table2": "url2"
  }
}
con_data = {'auth_keys': []}


class Create_API:
    def __init__(self):
        self.data = None

    def file_uploader_design(self):
        # File upload
        auth_value = {}
        upload_file_col, rest_col = st.columns(2, gap="large")
        
        with upload_file_col:
            uploaded_file = st.file_uploader(
                "Upload JSON file", type=["json"],accept_multiple_files=False)
            

            st.download_button("Demo JSON", data=json.dumps(
                        dump_data, indent=4), file_name="demo_open-etl_con_details.json", mime="application/json")
        
        if uploaded_file:
            file_content = uploaded_file.getvalue().decode("utf-8")
            file_extension = uploaded_file.name.split(".")[-1]
            con_data = parse_json(file_content)
            st.session_state.api_tab_data = con_data['tables']

            main_col, side_col = st.columns([2, 3], gap="large")
            with main_col:
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    api_name = st.text_input("API Name", "my_api")
                with col2:
                    auth_types = list(con_data['auth_keys'])
                    authentication_type = st.selectbox(
                        "Authentication Type", auth_types, index=st.session_state.api_tab_selected_index_auth_types)
                    st.session_state.api_tab_selected_index_auth_types = auth_types.index(
                        authentication_type)
                st.json(st.session_state.api_tab_data, expanded=False)

            # with col3:
            with rest_col:
                untested = True
                st.header("Test Connection")
                for auth_type, auth_details in con_data["authentication_details"].items():
                    if auth_type.lower() == authentication_type.lower():
                        for key, value in auth_details.items():
                            if isinstance(value, str):
                                backup_key = key
                                key = key.replace("_"," ").capitalize()
                                input_label = f"{key}:" 
                                auth_value[backup_key] = st.text_input(input_label, value="", key=value) if "pass" not in input_label.lower() else st.text_input(
                                    input_label, value="", type="password",key=value)
                test_col, save_col = st.columns(2,gap="small")
                
                with test_col:
                    if st.button("Test Connection"):
                        auth_value['base_url'] = con_data['base_url']
                        resp = test(con_type=authentication_type.lower(), data=auth_value) 
                        if resp["status_code"] == 200:
                            st.success("Connection Successful")
                            untested = False
                        else:
                            st.error(resp)
                con_name = st.text_input("Connection Name", "my_api",disabled=untested)

                with save_col:
                    if st.button("Save Connection", disabled=untested):
                        del con_data['auth_keys']
                        con_data['connection_type'] = 'api'
                        con_data['api'] = api_name
                        con_data['connection_name'] = con_name
                        store_connection_config(
                            filename=api_name, json_data=con_data,is_api=True, connection_name=con_name)
                        
                    # test(authentication_type, con_data)

    def submit_data_for_processing(self, data=None, is_json=True):
        st.write(data)


global val, create_api
create_api = Create_API()



def main():

    create_api.file_uploader_design()


main()
