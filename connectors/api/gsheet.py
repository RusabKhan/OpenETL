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
        self.spreadsheet_id = None
        self.logo = "https://upload.wikimedia.org/wikipedia/commons/5/51/Google_Cloud_logo.svg"
        self.base_url = "https://www.googleapis.com"
        self.tables = {
            "get_sheets": "sheets/v4/spreadsheets",
            "get_drive_files": "drive/v3/files"
        }
        self.pagination = {
            "pageSize": 100
        }
        self.limit = {"limit": 100}
        self.connection_type = ConnectionType.API
        self.api = "google"
        self.connection_name = "google"
        self.schema = "public"
        self.database = "public"
        self.authentication_details = {AuthType.SERVICE_ACCOUNT: {
            "spreadsheet_id": "",
            "credentials_json": ""}
        }
        self.auth_url = "https://accounts.google.com/o/oauth2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"

        self.main_response_key = "values"
        self.required_libs = ["google-api-python-client", "google-auth-httplib2", "google-auth-oauthlib"]
        super().__init__()

    def connect_to_api(self, auth_type=AuthType.SERVICE_ACCOUNT, **auth_params) -> bool:
        import googleapiclient.discovery
        from google.oauth2 import service_account
        credentials_json = auth_params.get("credentials_json")
        self.spreadsheet_id = auth_params.get("spreadsheet_id")
        if not credentials_json:
            raise ValueError("No credentials JSON provided.")
        credentials = service_account.Credentials.from_service_account_info(
            credentials_json, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        )
        return googleapiclient.discovery.build('sheets', 'v4', credentials=credentials)

    def fetch_data(self, api_session, table) -> pd.DataFrame:
        arr = []
        endpoint = self.construct_endpoint(table)
        while True:
            pagination_query = urlencode(self.pagination)
            limit_query = urlencode(self.limit)
            paginated_endpoint = f"{endpoint}?{pagination_query}&{limit_query}"
            resp = super().fetch_data(api_session, paginated_endpoint)
            yield resp[self.main_response_key]

            # Handle pagination for Google Sheets or Google Drive API
            if "nextPageToken" in resp:
                self.pagination["pageToken"] = resp["nextPageToken"]
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
        try:
            # Test connection to Google Sheets API by fetching some spreadsheet data
            spreadsheet_id = self.spreadsheet_id
            result = api_session.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            if result:
                print("Test connection successful: Spreadsheets are accessible.")
                return True
            else:
                print("Test connection failed: No spreadsheets found.")
                return False
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False

    def get_metadata(self, *args, **kwargs) -> dict:
        return super().get_metadata()

    def list_drive_files(self, api_session, query="") -> list:
        # Example method for listing Google Drive files
        files = []
        try:
            results = api_session.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
            files.extend(results.get('files', []))

            while 'nextPageToken' in results:
                results = api_session.files().list(q=query, pageToken=results['nextPageToken'], fields="nextPageToken, files(id, name)").execute()
                files.extend(results.get('files', []))
        except Exception as e:
            print(f"Failed to list Google Drive files: {e}")
        return files
