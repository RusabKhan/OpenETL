from openetl_utils.main_api_class import API
from openetl_utils.enums import *
import sys
import os
import json
import pandas as pd

sys.path.append(os.getenv('OPENETL_HOME'))


class Connector(API):

    def __init__(self):
        """
        Initialize a Connector instance for interacting with the Monday.com API.

        This constructor sets up the configuration required to connect to Monday.com by initializing
        various attributes such as the API logo, base URL, GraphQL queries for different Monday.com
        objects (e.g., boards, items, users, workspaces, teams, updates, etc.), pagination settings,
        and OAuth authentication details. The OAuth endpoints for authorization and token retrieval
        are also defined.

        Monday.com uses a GraphQL API architecture with a single endpoint (https://api.monday.com/v2).
        All queries are sent as POST requests with the query included in the request body.

        Attributes:
            logo (str): URL of the Monday.com connector logo.
            base_url (str): Base URL for API requests (GraphQL endpoint).
            tables (dict): Dictionary mapping operation keys to GraphQL query templates for Monday.com resources.
            pagination (dict): Dictionary containing pagination parameters (cursor-based pagination for items_page).
            limit (dict): Dictionary specifying the default record limit per API call.
            connection_type (ConnectionType): Indicator of the connection type (set to API).
            api (str): Identifier for the API ("monday").
            connection_name (str): Name of the connection ("monday").
            schema (str): Database schema used ("public").
            database (str): Database name used ("public").
            authentication_details (dict): Authentication configuration for Bearer token (initialized with an empty token).
            auth_url (str): URL for initiating OAuth authorization.
            token_url (str): URL for obtaining OAuth tokens.
            main_response_key (str): Key used to extract the main response data from API responses.
            required_libs (list): List of additional required libraries (empty by default).

        Note:
            The parent class initializer is called at the end of this method to complete the initialization.
        """
        self.logo = "https://cdn.dataomnisolutions.com/main/connector_logos/monday-icon.svg"
        self.base_url = "https://api.monday.com/v2"

        # Monday.com uses GraphQL, so we define GraphQL queries as table definitions
        # Each "table" is actually a GraphQL query that will be sent to the single endpoint
        self.tables = {
            # Core objects
            "get_all_boards": """
                query ($limit: Int, $page: Int) {
                    boards(limit: $limit, page: $page) {
                        id
                        name
                        description
                        state
                        board_kind
                        permissions
                        created_at
                        updated_at
                        creator {
                            id
                            name
                            email
                        }
                        owner {
                            id
                            name
                            email
                        }
                    }
                }
            """,

            "get_all_items": """
                query ($board_ids: [ID!], $limit: Int, $cursor: String) {
                    boards(ids: $board_ids) {
                        items_page(limit: $limit, cursor: $cursor) {
                            cursor
                            items {
                                id
                                name
                                created_at
                                updated_at
                                state
                                creator {
                                    id
                                    name
                                    email
                                }
                                column_values {
                                    id
                                    text
                                    value
                                }
                            }
                        }
                    }
                }
            """,

            "get_all_users": """
                query ($limit: Int, $page: Int) {
                    users(limit: $limit, page: $page) {
                        id
                        name
                        email
                        title
                        phone
                        location
                        time_zone_identifier
                        created_at
                        enabled
                        is_admin
                        is_guest
                        is_pending
                        is_view_only
                        photo_thumb
                        photo_original
                    }
                }
            """,

            "get_all_workspaces": """
                query ($limit: Int, $page: Int) {
                    workspaces(limit: $limit, page: $page) {
                        id
                        name
                        kind
                        description
                        created_at
                    }
                }
            """,

            "get_all_teams": """
                query ($limit: Int, $page: Int) {
                    teams(limit: $limit, page: $page) {
                        id
                        name
                        picture_url
                        users {
                            id
                            name
                            email
                        }
                    }
                }
            """,

            "get_all_updates": """
                query ($limit: Int, $page: Int) {
                    updates(limit: $limit, page: $page) {
                        id
                        body
                        text_body
                        created_at
                        updated_at
                        creator {
                            id
                            name
                            email
                        }
                        item_id
                    }
                }
            """,

            "get_all_tags": """
                query ($limit: Int, $page: Int) {
                    tags(limit: $limit, page: $page) {
                        id
                        name
                        color
                    }
                }
            """,

            "get_all_groups": """
                query ($board_ids: [ID!]) {
                    boards(ids: $board_ids) {
                        id
                        groups {
                            id
                            title
                            color
                            position
                            archived
                        }
                    }
                }
            """,

            "get_all_columns": """
                query ($board_ids: [ID!]) {
                    boards(ids: $board_ids) {
                        id
                        columns {
                            id
                            title
                            type
                            description
                            archived
                            settings_str
                        }
                    }
                }
            """,

            "get_all_activities": """
                query ($board_ids: [ID!], $limit: Int, $page: Int) {
                    boards(ids: $board_ids) {
                        activity_logs(limit: $limit, page: $page) {
                            id
                            event
                            data
                            created_at
                            user {
                                id
                                name
                                email
                            }
                        }
                    }
                }
            """,

            "get_all_notifications": """
                query ($limit: Int, $page: Int) {
                    notifications(limit: $limit, page: $page) {
                        id
                        text
                        created_at
                    }
                }
            """,

            "get_all_webhooks": """
                query ($board_id: ID!) {
                    webhooks(board_id: $board_id) {
                        id
                        board_id
                        event
                        config
                    }
                }
            """,

            "get_account_info": """
                query {
                    account {
                        id
                        name
                        slug
                        tier
                        plan {
                            max_users
                            period
                            tier
                            version
                        }
                    }
                }
            """,

            "get_me": """
                query {
                    me {
                        id
                        name
                        email
                        title
                        phone
                        location
                        time_zone_identifier
                        created_at
                        enabled
                        is_admin
                        is_guest
                        is_pending
                        is_view_only
                    }
                }
            """,
        }

        # For GraphQL cursor-based pagination
        self.pagination = {
            "cursor": None
        }

        self.limit = {"limit": 100}
        self.page = {"page": 1}

        self.connection_type = ConnectionType.API
        self.api = "monday"
        self.connection_name = "monday"
        self.schema = "public"
        self.database = "public"

        # Monday.com uses Bearer token authentication
        self.authentication_details = {
            AuthType.BEARER: {
                "token": ""
            }
        }

        # OAuth endpoints
        self.auth_url = "https://auth.monday.com/oauth2/authorize"
        self.token_url = "https://auth.monday.com/oauth2/token"

        # GraphQL responses are wrapped in a "data" key
        self.main_response_key = "data"

        self.required_libs = []

        super().__init__()

    def connect_to_api(self, auth_type=AuthType.BEARER, **auth_params) -> bool:
        """
        Establish a connection to the API using the specified authentication type and parameters.

        Monday.com supports multiple authentication methods:
        1. Bearer Token (API Token) - Simple authentication with a personal or app API token
        2. OAuth 2.0 - For apps that need to access data on behalf of users

        Parameters:
            auth_type (AuthType, optional): The authentication type to use (default is AuthType.BEARER).
            **auth_params: Arbitrary keyword arguments containing additional credentials or parameters
                          required for authentication.

        Returns:
            bool: True if the connection was successfully established, False otherwise.
        """
        return super().connect_to_api(auth_type, **auth_params)

    def fetch_data(self, api_session, table) -> pd.DataFrame:
        """
        Fetch data from Monday.com API using GraphQL queries.

        This method handles the GraphQL-specific request structure:
        - Constructs POST requests with GraphQL queries in the body
        - Handles cursor-based pagination for items_page queries
        - Handles page-based pagination for other queries
        - Yields response data for each page/cursor

        Parameters:
            api_session: The authenticated API session object.
            table (str): The table/query identifier to fetch data from.

        Yields:
            dict: Response data containing the fetched records.
        """
        query = self.tables.get(table)

        if not query:
            raise ValueError(f"Unknown table: {table}")

        # Prepare the GraphQL request body
        endpoint = self.base_url

        # Handle pagination based on query type
        if "items_page" in query:
            # Cursor-based pagination for items_page
            while True:
                variables = {
                    "limit": self.limit.get("limit", 100),
                    "cursor": self.pagination.get("cursor")
                }

                request_body = {
                    "query": query,
                    "variables": variables
                }

                # Make POST request with GraphQL query
                resp = self._make_graphql_request(api_session, endpoint, request_body)
                yield resp

                # Check for next cursor
                if "boards" in resp and len(resp["boards"]) > 0:
                    items_page = resp["boards"][0].get("items_page", {})
                    cursor = items_page.get("cursor")

                    if cursor and items_page.get("items"):
                        self.pagination["cursor"] = cursor
                    else:
                        break
                else:
                    break
        else:
            # Page-based pagination for other queries
            while True:
                variables = {
                    "limit": self.limit.get("limit", 100),
                    "page": self.page.get("page", 1)
                }

                request_body = {
                    "query": query,
                    "variables": variables
                }

                # Make POST request with GraphQL query
                resp = self._make_graphql_request(api_session, endpoint, request_body)
                yield resp

                # Check if there are more pages
                # In Monday.com, if the response has fewer items than limit, we've reached the end
                response_key = self._get_response_key_from_query(query)
                if response_key in resp:
                    items = resp[response_key]
                    if len(items) < self.limit.get("limit", 100):
                        break
                    self.page["page"] += 1
                else:
                    break

    def _make_graphql_request(self, api_session, endpoint, request_body):
        """
        Make a GraphQL POST request to Monday.com API.

        Parameters:
            api_session: The authenticated API session object.
            endpoint (str): The GraphQL endpoint URL.
            request_body (dict): The request body containing the query and variables.

        Returns:
            dict: The response data from the API.
        """
        response = api_session.post(endpoint, json=request_body)
        response.raise_for_status()

        json_response = response.json()

        # Monday.com returns data in a "data" wrapper
        if "data" in json_response:
            return json_response["data"]
        elif "errors" in json_response:
            raise Exception(f"GraphQL Error: {json_response['errors']}")
        else:
            return json_response

    def _get_response_key_from_query(self, query):
        """
        Extract the response key from a GraphQL query.

        Parameters:
            query (str): The GraphQL query string.

        Returns:
            str: The primary response key (e.g., "boards", "users", "workspaces").
        """
        # Simple parser to extract the main query field
        query_clean = query.strip().replace("\n", " ")

        if "boards" in query_clean:
            return "boards"
        elif "users" in query_clean:
            return "users"
        elif "workspaces" in query_clean:
            return "workspaces"
        elif "teams" in query_clean:
            return "teams"
        elif "updates" in query_clean:
            return "updates"
        elif "tags" in query_clean:
            return "tags"
        elif "notifications" in query_clean:
            return "notifications"
        elif "webhooks" in query_clean:
            return "webhooks"
        elif "account" in query_clean:
            return "account"
        elif "me" in query_clean:
            return "me"

        return "data"

    def return_final_df(self, responses) -> pd.DataFrame:
        """
        Convert the API responses into a pandas DataFrame.

        Parameters:
            responses: Iterator of response dictionaries from the API.

        Returns:
            pd.DataFrame: A DataFrame containing all fetched records.
        """
        return super().return_final_df(responses)

    def construct_endpoint(self, endpoint) -> str:
        """
        Construct the full endpoint URL.

        For Monday.com, this always returns the base GraphQL endpoint since all
        queries go through the same endpoint with different query bodies.

        Parameters:
            endpoint (str): The endpoint identifier (table name).

        Returns:
            str: The full endpoint URL.
        """
        return self.base_url

    def get_table_schema(self, api_session, table) -> dict:
        """
        Get the schema for a specific table.

        Parameters:
            api_session: The authenticated API session.
            table (str): The table name.

        Returns:
            dict: The table schema information.
        """
        return super().get_table_schema(api_session, table)

    def install_missing_libraries(self) -> bool:
        """
        Install any missing required libraries.

        Returns:
            bool: True if installation was successful, False otherwise.
        """
        return super().install_missing_libraries()

    def test_connection(self, api_session) -> bool:
        """
        Test the API connection by making a simple query.

        This method tests the connection by querying the current user's information
        using the "me" query.

        Parameters:
            api_session: The authenticated API session.

        Returns:
            bool: True if the connection test was successful, False otherwise.
        """
        try:
            query = self.tables["get_me"]
            request_body = {
                "query": query
            }

            response = self._make_graphql_request(api_session, self.base_url, request_body)

            # If we get a valid response with "me" data, connection is successful
            return "me" in response and response["me"] is not None
        except Exception as e:
            print(f"Connection test failed: {str(e)}")
            return False

    def get_metadata(self, *args, **kwargs) -> dict:
        """
        Get metadata about the connector.

        Returns:
            dict: Metadata information about the connector.
        """
        return super().get_metadata()