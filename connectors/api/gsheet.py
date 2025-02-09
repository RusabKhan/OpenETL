from utils.database_utils import DatabaseUtils
from utils.main_api_class import API
from utils.enums import *
from urllib.parse import urlencode, urlparse
import sys
import os
import pandas as pd


sys.path.append(os.getenv('OPENETL_HOME'))


class Connector(API):

    def __init__(self):
        """
        Initialize a Connector instance with default configuration settings for interacting with Google Sheets and Google Drive APIs.
        
        This constructor initializes instance attributes with default values required for API communication:
          - spreadsheet_id (None): Placeholder for the Google Sheets spreadsheet ID.
          - logo (str): URL for the Google Cloud logo.
          - base_url (str): Base URL for all Google API endpoints.
          - tables (dict): Mapping of operation keys to API endpoints:
              • "get_sheets": Endpoint for accessing Google Sheets.
              • "get_drive_files": Endpoint for accessing Google Drive files.
          - pagination (dict): Settings for API pagination (e.g., "pageSize": 100).
          - limit (dict): Limit settings for API queries (e.g., "limit": 100).
          - connection_type (ConnectionType): Indicates that the connection type is API.
          - api (str): Identifier for the API (set to "google").
          - connection_name (str): Human-readable name for the connection (set to "google").
          - schema (str) and database (str): Default values set to "public".
          - authentication_details (dict): Contains default authentication parameters for service accounts,
              including "spreadsheet_link" and "credentials_json" placeholders.
          - auth_url (str) and token_url (str): URLs used for OAuth2 authentication flows.
          - main_response_key (str): Key ("values") used to extract the primary data from API responses.
          - required_libs (list): Libraries required for interacting with Google APIs.
        
        Calls the superclass initializer to ensure proper setup and inheritance.
        """
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
            "spreadsheet_link": "",
            "credentials_json": ""}
        }
        self.auth_url = "https://accounts.google.com/o/oauth2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"

        self.main_response_key = "values"
        self.required_libs = ["google-api-python-client", "google-auth-httplib2", "google-auth-oauthlib"]
        super().__init__()

    def connect_to_api(self, auth_type=AuthType.SERVICE_ACCOUNT, **auth_params) -> bool:
        """
        Establish a connection to the Google Sheets API using service account credentials.
        
        This method extracts the spreadsheet ID from a provided spreadsheet link and validates the presence of a service account credentials JSON. It then creates a credentials object with the necessary scopes for accessing Google Sheets (both read/write and readonly) and Google Drive, and builds the corresponding API service object.
        
        Parameters:
            auth_type (AuthType): The authentication type to use. Defaults to AuthType.SERVICE_ACCOUNT.
            **auth_params: Additional authentication parameters, which must include:
                - credentials_json (dict): A dictionary containing service account credential information.
                - spreadsheet_link (str): The URL of the Google Sheet from which the spreadsheet ID will be extracted.
        
        Raises:
            ValueError: If the 'credentials_json' parameter is not provided.
        
        Returns:
            googleapiclient.discovery.Resource: An instance of the Google Sheets API service object.
            
        Example:
            service = connector.connect_to_api(
                credentials_json=service_account_info,
                spreadsheet_link="https://docs.google.com/spreadsheets/d/your_spreadsheet_id/edit"
            )
        """
        import googleapiclient.discovery
        from google.oauth2 import service_account
        credentials_json = auth_params.get("credentials_json")
        self.spreadsheet_id = self.extract_spreadsheet_id(auth_params.get("spreadsheet_link"))
        if not credentials_json:
            raise ValueError("No credentials JSON provided.")
        credentials = service_account.Credentials.from_service_account_info(
            credentials_json, scopes=["https://www.googleapis.com/auth/spreadsheets",
                                      "https://www.googleapis.com/auth/spreadsheets.readonly",
                                      "https://www.googleapis.com/auth/drive"]
        )
        return googleapiclient.discovery.build('sheets', 'v4', credentials=credentials)

    def fetch_data(self, api_session, table) -> pd.DataFrame:
        """
        Retrieve and yield paginated data from the specified table via the API session.
        
        This generator function constructs a paginated endpoint from the provided table name and retrieves data in pages using the active API session. It uses URL-encoded pagination and limit parameters to form the endpoint, then repeatedly calls the parent class's fetch_data method. For each response, it yields the value corresponding to the main response key (self.main_response_key). Pagination is handled by checking for a "nextPageToken" in the response; if present, the token is set for the next request, otherwise the loop terminates.
        
        Parameters:
            api_session (object): An active API session used to perform HTTP requests.
            table (str): The name or identifier of the table from which to fetch data.
        
        Yields:
            Any: The data extracted from the API response using the main response key, typically a pd.DataFrame or list representing a page of results.
        
        Example:
            for data_chunk in connector.fetch_data(api_session, 'Sheet1'):
                process(data_chunk)
        """
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
        """
        Construct a consolidated pandas DataFrame from collected API responses.
        
        This method delegates the DataFrame construction to the superclass implementation of return_final_df,
        aggregating and formatting the provided responses. It is typically used to combine data retrieved 
        from multiple API calls into a single DataFrame for further analysis.
        
        Parameters:
            responses (list or dict): A collection of API response objects. The responses should adhere 
                to the format expected by the parent class method.
        
        Returns:
            pd.DataFrame: A unified DataFrame constructed from the aggregated API responses.
        """
        return super().return_final_df(responses)

    def construct_endpoint(self, endpoint) -> str:
        """
        Construct and return the full API endpoint URL.
        
        This method delegates the URL construction to the parent class's implementation, appending the provided endpoint to the base API URL.
        
        Parameters:
            endpoint (str): The relative path or resource identifier to be appended to the base URL.
        
        Returns:
            str: The complete API endpoint URL.
        """
        return super().construct_endpoint(endpoint)

    def get_table_schema(self, api_session, table) -> dict:
        """
        Retrieve the schema details for the specified table.
        
        This method fetches the schema data by first calling the parent class's get_table_schema method using the provided API session and table name. It extracts the main response using the connector's main response key, converts the extracted data into a final DataFrame via the return_final_df method, and then processes this DataFrame with DatabaseUtils to generate detailed schema information.
        
        Parameters:
            api_session: An active API session used to communicate with the data source.
            table (str): The name of the table whose schema is to be retrieved.
        
        Returns:
            dict: A dictionary containing the detailed schema information for the specified table.
        """
        table_data = super().get_table_schema(
            api_session, table)[self.main_response_key]
        return DatabaseUtils().dataframe_details(self.return_final_df(table_data))

    def install_missing_libraries(self) -> bool:
        """
        Attempt to install any missing libraries required by the connector.
        
        This method delegates the process to the superclass implementation, which
        checks for and installs any libraries that are not already present.
        
        Returns:
            bool: True if all required libraries were successfully installed, False otherwise.
        """
        return super().install_missing_libraries()

    def test_connection(self, api_session) -> bool:
        """
        Test the connection to the Google Sheets API.
        
        This method attempts to verify connectivity by fetching spreadsheet data using the API session.
        It retrieves the spreadsheet using the stored spreadsheet_id and checks for a valid response.
        In case of a valid response, it prints a success message; otherwise, it prints an error message and returns False.
        
        Parameters:
            api_session: An object representing the Google Sheets API session. It must provide a
                         'spreadsheets()' method that supports the 'get' and 'execute' calls.
        
        Returns:
            bool: True if the spreadsheet data is successfully retrieved, False otherwise.
        
        Side Effects:
            Prints status messages to the console regarding connection success or failure.
        """
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


    def extract_spreadsheet_id(self, sheet_url):
        """
        Extract the spreadsheet ID from a Google Sheets URL.
        
        This method parses the provided URL to retrieve the spreadsheet ID, which is typically the fourth segment of the URL path.
        If the URL format is unexpected or an error occurs during parsing, the method prints an error message and returns None.
        
        Parameters:
            sheet_url (str): The complete URL of the Google Sheet.
        
        Returns:
            str or None: The extracted spreadsheet ID if parsing is successful; otherwise, None.
        """
        try:
            path = urlparse(sheet_url).path
            # Split the path and get the ID part (4th segment in the path)
            spreadsheet_id = path.split('/')[3]
            return spreadsheet_id
        except Exception as e:
            print(f"Error extracting spreadsheet ID: {e}")
            return None

    def get_metadata(self, *args, **kwargs) -> dict:
        """
        Retrieve metadata by delegating to the superclass's implementation.
        
        This method forwards any positional and keyword arguments to the superclass's get_metadata method
        and returns a dictionary containing metadata information.
        
        Parameters:
            *args: Variable length argument list to pass to the superclass method.
            **kwargs: Arbitrary keyword arguments to pass to the superclass method.
        
        Returns:
            dict: A dictionary containing metadata information.
        """
        return super().get_metadata()

    def list_drive_files(self, api_session, query="") -> list:
        # Example method for listing Google Drive files
        """
        List Google Drive files based on an optional query.
        
        This method uses the provided API session to retrieve files from Google Drive.
        It queries the API using the specified query string and handles pagination by
        checking for a 'nextPageToken', accumulating file entries until all pages have been fetched.
        In the event of an exception during the API call, an error message is printed and
        the files collected up to that point are returned.
        
        Parameters:
            api_session: The Google API session object for interacting with the Drive API.
            query (str, optional): A query string to filter the files. Defaults to an empty string.
        
        Returns:
            list: A list of dictionaries, where each dictionary represents a file with keys such as 'id' and 'name'.
        """
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
