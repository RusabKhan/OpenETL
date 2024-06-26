
import json
import requests
from .local_connection_utils import api_directory
import pandas as pd
from . enums import *
import re
from collections import abc
from utils.generic_utils import install_libraries


class API:

    logo = ""
    base_url = ""
    tables = {
    }
    pagination = {
    }
    limit = {"limit": 100}
    connection_type = ConnectionType.API
    api = ""
    connection_name = ""
    supported_auths = [AuthType.BEARER, AuthType.OAUTH2, AuthType.BASIC]
    schema = "public"
    database = "public"
    authentication_details = {
    }

    def __init__(self):

        self.logo = ""
        self.base_url = ""
        self.tables = {
        }
        self.pagination = {
        }
        self.limit = {"limit": 100}
        self.connection_type = ConnectionType.API
        self.api = ""
        self.connection_name = ""
        self.supported_auths = [AuthType.BEARER,
                                AuthType.OAUTH2, AuthType.BASIC]
        self.schema = "public"
        self.database = "public"
        self.authentication_details = {
        }
        self.main_response_key = ""
        self.required_libs = [""]

    def connect_to_api(self, auth_type=AuthType.BASIC, **auth_params):
        """
        Connects to a REST API using the specified authentication mechanism.

        Args:
        - url (str): The URL of the REST API.
        - auth_type (str): The type of authentication mechanism to use ('oauth', 'bearer', 'basic', etc.).
        - **auth_params: Additional parameters required for authentication (e.g., username, password, token).

        Returns:
        - requests.Session: A session object with the authentication configured.
        """
        url = self.base_url
        session = requests.Session()

        if auth_type == AuthType.OAUTH2:
            pass  # Placeholder for OAuth implementation

        elif auth_type == AuthType.BEARER:
            token = auth_params.get('token')
            session.headers['Authorization'] = f'Bearer {token}'

        elif auth_type == AuthType.BASIC:
            username = auth_params.get('username')
            password = auth_params.get('password')
            session.auth = (username, password)
        else:
            pass  # Placeholder for other authentication mechanisms

        return session

    def fetch_data(self, api_session, table):
        """
        Fetches data from the API using the provided session object.

        Args:
        - api_session (requests.Session): The session object with authentication configured.
        - endpoint (str): The endpoint to fetch data from.

        Returns:
        - dict: The JSON response containing the fetched data.
        """
        response = api_session.get(table)
        response.raise_for_status()  # Raise an exception for any HTTP errors
        return response.json()

    def return_final_df(self, responses):
        final_arr = []
        for resp in responses:
            if isinstance(resp, list):
                final_arr.append(pd.json_normalize(resp))
            else:
                final_arr.append(self.create_df(resp))
        df = pd.concat(final_arr)
        return df

    def create_df(self, resp):
        parent_key = resp.keys()
        arr = []
        for key in parent_key:
            real_response = resp[key]
            if isinstance(real_response, dict) or isinstance(real_response, list):
                arr.append(pd.json_normalize(real_response))
            else:
                arr.append(pd.DataFrame([real_response], columns=[key]))

        df = pd.concat(arr)
        for col in df.select_dtypes(include='object').columns:
            df[col] = df[col].astype(str)

        return df

    def construct_endpoint(self, endpoint):
        endpoint = self.tables.get(endpoint)
        endpoint = f"{self.base_url}/{endpoint}"
        return endpoint

    def get_table_schema(self, api_session, table_name):
        """Retrieve the schema details of a table.

        Args:
            table_name (str): The name of the table to get the schema for.

        Returns:
            dict: A dictionary containing the schema details of the table.
        """
        endpoint = self.construct_endpoint(table_name)
        resp = api_session.get(url=endpoint)
        if resp.status_code == 200:
            table_data = resp.json()
            return table_data
        else:
            raise Exception(f"Failed to retrieve table schema. Status code: {resp.status_code}. Message: {resp.text}")

    def install_missing_libraries(self):
        if len(self.required_libs) > 0:
            return install_libraries(self.required_libs)

    def test_connection(self, api_session):
        for table in self.tables:
            try:
                if self.get_table_schema(api_session, table):
                    return True
            except Exception as e:
                return False
