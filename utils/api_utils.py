import json
import xml.etree.ElementTree as ET
import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
from streamlit_oauth import OAuth2Component
from .local_connection_utils import api_directory
import pandas as pd
from . enums import *


def parse_json(json_content):
    try:
        data = json.loads(json_content)
        data["auth_keys"] = data["authentication_details"].keys()
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


def check_basic_auth(data):
    url = data["base_url"]
    data.pop("base_url")

    try:
        # Make a GET request to the API endpoint with Basic Authentication
        response = requests.get(url, auth=HTTPBasicAuth(**data))

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            print('API request successful!')
            print('Response:')
            return response.json()  # Assuming the response is in JSON format
        else:
            print(
                f'API request failed with status code {response.status_code}')
            print('Response:')
            # Print response content for debugging
            return response.text, response.status_code
    except Exception as e:
        return f'An error occurred: {e}'


def check_bearer_token(data):
    url = data["base_url"]
    data.pop("base_url")
    bearer_token = list(data.values())[0]

    # Headers with Bearer token
    headers = {
        'Authorization': f'Bearer {bearer_token}'
    }

    tables = []
    for key, value in st.session_state.api_tab_data.items():
        tables.append(value)

    try:
        # Make a GET request to the API endpoint with Bearer token
        response = requests.get(f"{url}/{tables[0]}", headers=headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            print('API request successful!')
            print('Response:')
            # Assuming the response is in JSON format
            return {"data": response.json(), "status_code": response.status_code}
        else:
            print(
                f'API request failed with status code {response.status_code}')
            print('Response:')
            return {"data": response.text, "status_code": response.status_code}
            # Print response content for debugging
    except Exception as e:
        print(f'An error occurred: {e}')


def check_oauth2(data):
    oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_URL,
                             TOKEN_URL, REFRESH_TOKEN_URL, REVOKE_TOKEN_URL)
    # Check if token exists in session state
    if 'token' not in st.session_state:
        # If not, show authorize button
        result = oauth2.authorize_button("Authorize", REDIRECT_URI, SCOPE)
        if result and 'token' in result:
            # If authorization successful, save token in session state
            st.session_state.token = result.get('token')
            st.experimental_rerun()
    else:
        # If token exists in session state, show the token
        token = st.session_state['token']
        st.json(token)
        if st.button("Refresh Token"):
            # If refresh token button is clicked, refresh the token
            token = oauth2.refresh_token(token)
            st.session_state.token = token
            st.experimental_rerun()


def test(con_type, data):
    st.write(f"{con_type} connection: Testing against 1st table.")
    if con_type.lower() == AuthType.BASIC.value:
        return check_basic_auth(data=data)
    elif con_type.lower() == AuthType.OAUTH2.value:
        return check_oauth2(data=data)
    elif con_type.lower() == AuthType.BEARER.value:
        return check_bearer_token(data=data)


def read_api_tables(api_name):
    tables = None
    with open(f"{api_directory}/{api_name}.json") as f:
        data = json.load(f)['tables'].keys()
        tables = [i for i in data]
    return tables


def read_api_tables_url(api_name, tablename):
    tables = None
    url = None
    with open(f"{api_directory}/{api_name}.json") as f:
        data = json.load(f)
        url = f"{data['base_url']}/{data['tables'][tablename]}"
    return url


def get_data_from_api(table, api,auth_type, token=None, username=None, password=None):
    """
    Retrieve data from an API using Basic Auth or Bearer token.

    Args:
        table (str): The URL of the API endpoint.
        auth_type (str): The authentication type to be used. Either 'basic' or 'bearer'.
        token (str, optional): The Bearer token for authentication. Required if auth_type is 'bearer'.
        username (str, optional): The username for Basic Auth. Required if auth_type is 'basic'.
        password (str, optional): The password for Basic Auth. Required if auth_type is 'basic'.

    Returns:
        dict: The JSON response from the API.
    """
    headers = {}
    if auth_type == AuthType.BEARER.value:
        headers['Authorization'] = f'Bearer {token}'
    elif auth_type == AuthType.BASIC.value:
        headers['Authorization'] = requests.auth.HTTPBasicAuth(
            username, password)

    response = requests.get(table, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(
            f"Failed to retrieve data from {table}. Status code: {response.status_code}")
        return None


def flatten_data(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out


def get_data(table, api, auth_type, token=None, username=None, password=None):
    table = read_api_tables_url(api, table)
    data = get_data_from_api(table,api, auth_type, token, username, password)
    flattened = flatten_data(data)
    return pd.DataFrame.from_dict(flattened,orient='index')
