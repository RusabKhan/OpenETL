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
        self.logo = "https://cdn.dataomnisolutions.com/main/connector_logos/639decbfa51e772ab2070c32_salesforce.svg"
        self.base_url = "https://your_instance.salesforce.com/services/data/vXX.X"  # Replace 'your_instance' and 'vXX.X' with your specific Salesforce instance and API version
        self.tables = {
            "get_all_contacts": "/sobjects/Contact",
            "get_all_accounts": "/sobjects/Account",
            "get_all_opportunities": "/sobjects/Opportunity",
            "get_all_leads": "/sobjects/Lead"
        }
        self.pagination = {
            "nextRecordsUrl": None
        }
        self.limit = {"limit": 2000}  # Salesforce default is up to 2000 records per query
        self.connection_type = ConnectionType.API
        self.api = "salesforce"
        self.connection_name = "salesforce"
        self.schema = "public"
        self.database = "public"
        self.authentication_details = {AuthType.BEARER: {
            "token": ""}
        }
        self.auth_url = "https://login.salesforce.com/services/oauth2/authorize"
        self.token_url = "https://login.salesforce.com/services/oauth2/token"

        self.main_response_key = "records"
        self.required_libs = []

    def connect_to_api(self, auth_type=AuthType.BEARER, **auth_params) -> bool:
        return super().connect_to_api(auth_type, **auth_params)

    def fetch_data(self, api_session, table) -> pd.DataFrame:
        arr = []
        endpoint = self.construct_endpoint(table)
        while True:
            paginated_endpoint = endpoint
            if self.pagination["nextRecordsUrl"]:
                paginated_endpoint = self.pagination["nextRecordsUrl"]
            resp = super().fetch_data(api_session, paginated_endpoint)
            yield resp[self.main_response_key]

            if "nextRecordsUrl" in resp:
                self.pagination["nextRecordsUrl"] = resp["nextRecordsUrl"]
            else:
                break

    def return_final_df(self, responses) -> pd.DataFrame:
        return super().return_final_df(responses)

    def construct_endpoint(self, endpoint) -> str:
        return super().construct_endpoint(endpoint)

    def get_table_schema(self, api_session, table) -> dict:
        table_data = super().get_table_schema(
            api_session, table)[self.main_response_key]
        return DatabaseUtils().dataframe_details(self.return_final_df(table_data))

    def install_missing_libraries(self) -> bool:
        return super().install_missing_libraries()

    def test_connection(self, api_session) -> bool:
        return super().test_connection(api_session)

    def get_metadata(self, *args, **kwargs) -> dict:
        return super().get_metadata()
