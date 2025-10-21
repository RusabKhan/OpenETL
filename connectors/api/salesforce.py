from openetl_utils.database_utils import DatabaseUtils
from openetl_utils.main_api_class import API
from openetl_utils.enums import *
from urllib.parse import urlencode
import sys
import os
import pandas as pd

sys.path.append(os.getenv('OPENETL_HOME'))


class Connector(API):

    def __init__(self):
        """
        Initialize a Connector instance for interacting with the Salesforce API.

        This constructor sets up the configuration required to connect to Salesforce by initializing various
        attributes such as the API logo, base URL, endpoint mappings for numerous Salesforce objects (e.g.,
        accounts, contacts, opportunities, leads, cases, and other CRM-related resources), pagination
        settings, and OAuth authentication details. The OAuth endpoints for authorization and token retrieval
        are also defined.

        Attributes:
            logo (str): URL of the Salesforce connector logo.
            base_url (str): Base URL for API requests (instance-specific).
            tables (dict): Dictionary mapping operation keys to relative endpoint paths for Salesforce resources.
            pagination (dict): Dictionary containing pagination parameters (e.g., 'offset' key for cursor-based paging).
            limit (dict): Dictionary specifying the default record limit per API call.
            connection_type (ConnectionType): Indicator of the connection type (set to API).
            api (str): Identifier for the API ("salesforce").
            connection_name (str): Name of the connection ("salesforce").
            schema (str): Database schema used ("salesforce").
            database (str): Database name used ("salesforce").
            instance_url (str): Salesforce instance URL (to be set during connection).
            authentication_details (dict): Authentication configuration for Bearer token (initialized with an empty token).
            auth_url (str): URL for initiating OAuth authorization.
            token_url (str): URL for obtaining OAuth tokens.
            main_response_key (str): Key used to extract the main response data from API responses.
            required_libs (list): List of additional required libraries (empty by default).

        Note:
            The parent class initializer is called at the end of this method to complete the initialization.
        """
        self.logo = "https://cdn.dataomnisolutions.com/main/connector_logos/salesforce-icon.svg"
        self.base_url = "https://{instance_url}/services/data/v57.0"
        self.instance_url = None
        self.tables = {
            # Core CRM Objects
            "get_all_accounts": "/sobjects/Account",
            "get_all_contacts": "/sobjects/Contact",
            "get_all_opportunities": "/sobjects/Opportunity",
            "get_all_leads": "/sobjects/Lead",
            "get_all_cases": "/sobjects/Case",
            "get_all_tasks": "/sobjects/Task",
            "get_all_events": "/sobjects/Event",
            "get_all_campaigns": "/sobjects/Campaign",
            "get_all_campaign_members": "/sobjects/CampaignMember",
            "get_all_activities": "/sobjects/Activity",
            "get_all_notes": "/sobjects/Note",
            "get_all_attachments": "/sobjects/Attachment",
            "get_all_files": "/sobjects/ContentDocument",
            "get_all_document_links": "/sobjects/ContentDocumentLink",

            # Commerce Objects
            "get_all_orders": "/sobjects/Order",
            "get_all_order_items": "/sobjects/OrderItem",
            "get_all_price_books": "/sobjects/Pricebook2",
            "get_all_price_book_entries": "/sobjects/PricebookEntry",
            "get_all_quote_lines": "/sobjects/QuoteLineItem",
            "get_all_quotes": "/sobjects/Quote",
            "get_all_products": "/sobjects/Product2",

            # Contract Objects
            "get_all_contracts": "/sobjects/Contract",
            "get_all_contract_line_items": "/sobjects/ContractLineItem",

            # Account/Partner Objects
            "get_all_account_teams": "/sobjects/AccountTeamMember",
            "get_all_opportunity_teams": "/sobjects/OpportunityTeamMember",
            "get_all_account_relationships": "/sobjects/AccountContactRelation",

            # Service Objects
            "get_all_service_resources": "/sobjects/ServiceResource",
            "get_all_service_appointments": "/sobjects/ServiceAppointment",
            "get_all_service_territories": "/sobjects/ServiceTerritory",
            "get_all_service_team_members": "/sobjects/ServiceTeamMember",

            # Marketing Objects
            "get_all_marketing_actions": "/sobjects/MarketingAction",
            "get_all_engagement_scores": "/sobjects/EngagementScore",

            # Forecasting Objects
            "get_all_forecasts": "/sobjects/Forecast",
            "get_all_forecast_adjustments": "/sobjects/ForecastingAdjustment",

            # User and Setup Objects
            "get_all_users": "/sobjects/User",
            "get_all_user_roles": "/sobjects/UserRole",
            "get_all_user_team_members": "/sobjects/UserTeamMember",
            "get_all_organization_info": "/sobjects/Organization",
            "get_all_profiles": "/sobjects/Profile",
            "get_all_permission_sets": "/sobjects/PermissionSet",
            "get_all_custom_permissions": "/sobjects/CustomPermission",

            # Approval and Workflow Objects
            "get_all_approval_processes": "/sobjects/ProcessApproval",
            "get_all_approval_workflow": "/sobjects/ProcessInstance",
            "get_all_approval_steps": "/sobjects/ProcessInstanceStep",

            # Custom Objects (examples)
            "get_all_custom_object_1": "/sobjects/CustomObject__c",
            "get_all_custom_object_2": "/sobjects/CustomObject2__c",

            # Query Endpoint (for SOQL queries)
            "soql_query": "/query",

            # Search Endpoint
            "global_search": "/search/sobjects",

            # Metadata Endpoints
            "get_all_sobject_types": "/sobjects",
            "get_sobject_describe": "/sobjects/{sobject_type}/describe",
            "get_all_fields": "/sobjects/{sobject_type}/describe",
        }

        self.pagination = {
            "offset": 0
        }
        self.limit = {"limit": 2000}
        self.connection_type = ConnectionType.API
        self.api = "salesforce"
        self.connection_name = "salesforce"
        self.schema = "salesforce"
        self.database = "salesforce"
        self.authentication_details = {
            AuthType.OAUTH2: {
                "client_id": "",
                "client_secret": "",
                "token": ""
            }
        }
        self.auth_url = "https://login.salesforce.com/services/oauth2/authorize"
        self.token_url = "https://login.salesforce.com/services/oauth2/token"

        self.main_response_key = "records"
        self.required_libs = []
        super().__init__()

    def connect_to_api(self, auth_type=AuthType.OAUTH2, **auth_params) -> bool:
        """
        Establish a connection to the Salesforce API using OAuth2 authentication.

        This method handles Salesforce-specific OAuth2 authentication, including obtaining
        an access token and retrieving the instance URL. It then stores these credentials
        in the session for subsequent API calls.

        Parameters:
            auth_type (AuthType, optional): The authentication type to use (default is AuthType.OAUTH2).
            **auth_params: Arbitrary keyword arguments containing OAuth2 credentials:
                - client_id (str): The Salesforce connected app client ID
                - client_secret (str): The Salesforce connected app client secret
                - refresh_token (str): The OAuth2 refresh token
                - instance_url (str): The Salesforce instance URL (e.g., https://na1.salesforce.com)

        Returns:
            bool: True if the connection was successfully established, False otherwise.
        """
        try:
            if auth_type == AuthType.OAUTH2.value or auth_type == AuthType.OAUTH2:
                refresh_token = auth_params.get('refresh_token')
                client_id = auth_params.get('client_id')
                client_secret = auth_params.get('client_secret')
                instance_url = auth_params.get('instance_url')

                if not all([refresh_token, client_id, client_secret, instance_url]):
                    raise ValueError(
                        "Missing required OAuth2 parameters: client_id, client_secret, refresh_token, instance_url")

                self.instance_url = instance_url
                self.base_url = f"{instance_url}/services/data/v57.0"

                # Update authentication details
                self.authentication_details[AuthType.OAUTH2] = {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "token": refresh_token
                }

                return True
            else:
                raise NotImplementedError(f"Authentication type {auth_type} is not supported for Salesforce")
        except Exception as e:
            print(f"Error connecting to Salesforce API: {str(e)}")
            return False

    def fetch_data(self, api_session, table, query_params=None) -> pd.DataFrame:
        """
        Fetch data from a Salesforce object or execute a SOQL query with pagination support.

        Args:
            api_session (requests.Session): The authenticated session object.
            table (str): The table/sobject name or SOQL query.
            query_params (dict, optional): Additional query parameters for the API call.

        Yields:
            dict: Paginated response data from Salesforce.
        """
        endpoint = self.construct_endpoint(table)

        while True:
            pagination_query = urlencode(self.pagination)
            limit_query = urlencode(self.limit)

            full_endpoint = f"{endpoint}?{pagination_query}&{limit_query}"
            if query_params:
                full_endpoint += f"&{urlencode(query_params)}"

            resp = super().fetch_data(api_session, full_endpoint, self.main_response_key)
            yield resp

            # Check for next page
            if "nextRecordsUrl" in resp:
                self.pagination["offset"] += self.limit["limit"]
            else:
                break

    def return_final_df(self, responses) -> pd.DataFrame:
        """
        Convert paginated responses into a single pandas DataFrame.

        Args:
            responses (list): List of paginated response dictionaries.

        Returns:
            pd.DataFrame: Combined DataFrame from all responses.
        """
        return super().return_final_df(responses)

    def construct_endpoint(self, endpoint) -> str:
        """
        Construct the full API endpoint URL for a given Salesforce object or operation.

        Args:
            endpoint (str): The endpoint key or SOQL query.

        Returns:
            str: The complete endpoint URL.
        """
        if endpoint in self.tables:
            endpoint_path = self.tables.get(endpoint)
            endpoint = f"{self.base_url}{endpoint_path}"
        else:
            # Assume it's a SOQL query
            endpoint = f"{self.base_url}/query?q={endpoint}"

        return endpoint

    def get_table_schema(self, api_session, table) -> dict:
        """
        Retrieve the schema details of a Salesforce object.

        Args:
            api_session (requests.Session): The authenticated session object.
            table (str): The Salesforce object name.

        Returns:
            dict: A dictionary containing field details, relationships, and metadata for the object.
        """
        try:
            describe_endpoint = f"{self.base_url}/sobjects/{table}/describe"
            resp = api_session.get(url=describe_endpoint)
            resp.raise_for_status()

            table_data = resp.json()

            # Extract schema information
            schema_info = {
                "object_name": table_data.get("name"),
                "label": table_data.get("label"),
                "fields": []
            }

            # Process fields
            for field in table_data.get("fields", []):
                field_info = {
                    "name": field.get("name"),
                    "label": field.get("label"),
                    "type": field.get("type"),
                    "length": field.get("length"),
                    "precision": field.get("precision"),
                    "scale": field.get("scale"),
                    "required": not field.get("nillable", True),
                    "updateable": field.get("updateable"),
                    "createable": field.get("createable")
                }
                schema_info["fields"].append(field_info)

            return DatabaseUtils().dataframe_details(
                self.return_final_df(schema_info["fields"])
            )
        except Exception as e:
            raise Exception(f"Failed to retrieve schema for {table}. Error: {str(e)}")

    def install_missing_libraries(self) -> bool:
        """
        Check and install any missing required libraries.

        Returns:
            bool: True if libraries are installed successfully, False otherwise.
        """
        return super().install_missing_libraries()

    def test_connection(self, api_session) -> bool:
        """
        Test the connection to the Salesforce API.

        Args:
            api_session (requests.Session): The authenticated session object.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        try:
            # Try to fetch organization info
            test_endpoint = f"{self.base_url}/sobjects"
            resp = api_session.get(url=test_endpoint)
            return resp.status_code == 200
        except Exception as e:
            print(f"Connection test failed: {str(e)}")
            return False

    def get_metadata(self, *args, **kwargs) -> dict:
        """
        Get metadata for all available Salesforce objects and fields.

        Returns:
            dict: A dictionary containing schema information for the Salesforce database.
        """
        return super().get_metadata()