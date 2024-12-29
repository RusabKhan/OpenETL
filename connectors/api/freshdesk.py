from utils.database_utils import DatabaseUtils
from utils.main_api_class import API
from utils.enums import *
from urllib.parse import urlencode
import sys
import os
import pandas as pd

sys.path.append(os.getenv('OPENETL_HOME'))


class Connector(API):

    def __init__(self):
        super().__init__()
        self.logo = "https://upload.wikimedia.org/wikipedia/commons/a/a4/Freshdesk_Logo.png"
        self.base_url = "https://{domain}.freshdesk.com/api/v2"  # To be set dynamically using domain from auth_details
        self.tables = {
            "get_all_contacts": "/contacts",
            "get_all_companies": "/companies",
            "get_all_agents": "/agents",
            "get_all_tickets": "/tickets",
        }
        self.pagination = {
            "nextPage": None
        }
        self.limit = {"limit": 100}  # Freshdesk default limit per query
        self.connection_type = ConnectionType.API
        self.api = "freshdesk"
        self.connection_name = "freshdesk"
        self.schema = "public"
        self.database = "public"
        self.authentication_details = {AuthType.BASIC: {
            "username": "",
            "password": "",
            "domain": ""  # Freshdesk domain will be stored here
        }}
        self.auth_url = "https://{domain}.freshdesk.com/oauth/authorize"
        self.token_url = "https://{domain}.freshdesk.com/oauth/token"

        self.main_response_key = None  # Freshdesk doesn't require this explicitly
        self.required_libs = []

    def connect_to_api(self, auth_type=AuthType.BEARER, **auth_params) -> bool:
        # Retrieve the domain and token from authentication_details
        domain = auth_params.get('domain')
        token = auth_params.get('username')

        if not domain or not token:
            raise ValueError("Domain and Username must be provided in authentication_details.")

        # Update base_url and auth URLs with the dynamic domain
        self.base_url = self.base_url.format(domain=domain)
        self.auth_url = self.auth_url.format(domain=domain)
        self.token_url = self.token_url.format(domain=domain)

        return super().connect_to_api(auth_type, **auth_params)

    def fetch_data(self, api_session, table) -> pd.DataFrame:
        arr = []
        endpoint = self.construct_endpoint(table)
        while True:
            paginated_endpoint = endpoint
            if self.pagination["nextPage"]:
                paginated_endpoint = self.pagination["nextPage"]
            resp = super().fetch_data(api_session, paginated_endpoint)
            yield resp

            # Pagination logic for Freshdesk
            if "next_page" in resp:
                self.pagination["nextPage"] = resp["next_page"]
            else:
                break

    def return_final_df(self, responses) -> pd.DataFrame:
        return super().return_final_df(responses)

    def construct_endpoint(self, endpoint) -> str:
        return super().construct_endpoint(endpoint)

    def get_table_schema(self, api_session, table) -> dict:
        # Freshdesk API doesn't return schema info like Salesforce does. This method can be customized further
        # to fetch schema-related details if needed.
        table_data = super().get_table_schema(api_session, table)
        if not table_data:
            return {"message": ["Table is empty. Connection Successful."]}
        return DatabaseUtils().dataframe_details(self.return_final_df(table_data))

    def install_missing_libraries(self) -> bool:
        return super().install_missing_libraries()

    def test_connection(self, api_session) -> bool:
        return super().test_connection(api_session)

    def get_metadata(self, *args, **kwargs) -> dict:
        return super().get_metadata()
