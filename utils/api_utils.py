import json
import xml.etree.ElementTree as ET
import streamlit as st



def parse_json(json_content):
    try:
        data = json.loads(json_content)
        return data
    except json.JSONDecodeError:
        st.error("Invalid JSON format")
        return None

def parse_xml(xml_content):
    try:
        root = ET.fromstring(xml_content)
        data = {
            "source_name": root.find("source_name").text,
            "authentication": root.find("authentication").text,
            "tables": {elem.tag: elem.text for elem in root.find("tables").iter()}
        }
        return data
    except ET.ParseError:
        st.error("Invalid XML format")
        return None


def test():
    if authentication_type == "OAuth2":
        client_id = st.text_input("Client ID", "your_client_id")
        client_secret = st.text_input("Client Secret", "your_client_secret")
        redirect_url = st.text_input("Redirect URL", "your_redirect_url")
    else:
        username = st.text_input("Username", "your_username")
        password = st.text_input("Password", "your_password", type="password")
    submit = st.button("Test")