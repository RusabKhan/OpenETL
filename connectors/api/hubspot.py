
from utils.database_utils import DatabaseUtils
from utils.main_api_class import API
from utils.enums import *
from urllib.parse import urlencode
import sys
import os


sys.path.append(os.getenv('OPENETL_HOME'))


class Connector(API):

    def __init__(self):
        super().__init__()
        self.logo = "https://en.m.wikipedia.org/wiki/File:HubSpot_Logo.svg"
        self.base_url = "https://api.hubapi.com/crm/v3"
        self.tables = {
            "get_all_contacts": "objects/contacts",
            "get_all_companies": "objects/companies",
            "get_all_deals": "objects/deals",
            "get_all_activities": "objects/engagements"
        }
        self.pagination = {
            "after": 0
        }
        self.limit = {"limit": 100}
        self.connection_type = ConnectionType.API
        self.api = "hubspot"
        self.connection_name = "hubspot"
        self.schema = "public"
        self.database = "public"
        self.authentication_details = {AuthType.BEARER: {
            "token": ""}
        }
        self.main_response_key = "results"
        self.required_libs = []

    def connect_to_api(self, auth_type=AuthType.BEARER, **auth_params):
        return super().connect_to_api(auth_type, **auth_params)

    def fetch_data(self, api_session, table):
        arr = []
        endpoint = self.construct_endpoint(table)
        while True:
            pagination_query = urlencode(self.pagination)
            limit_query = urlencode(self.limit)
            paginated_endpoint = f"{endpoint}?{pagination_query}&{limit_query}"
            resp = super().fetch_data(api_session, paginated_endpoint)
            arr.append(resp[self.main_response_key])
            if "paging" in resp and "next" in resp["paging"]:
                self.pagination["after"] = resp["paging"]["next"]["after"]
            else:
                break
        return self.return_final_df(arr)

    def return_final_df(self, responses):
        return super().return_final_df(responses)

    def construct_endpoint(self, endpoint):
        return super().construct_endpoint(endpoint)

    def get_table_schema(self, api_session, table):
        table_data = super().get_table_schema(
            api_session, table)[self.main_response_key]
        return SchemaUtils().dataframe_details(self.return_final_df(table_data))

    def install_missing_libraries(self):
        return super().install_missing_libraries()

    def test_connection(self, api_session):
        return super().test_connection(api_session)