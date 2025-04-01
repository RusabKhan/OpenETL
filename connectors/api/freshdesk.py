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
        """
        Initialize a Freshdesk Connector instance.
        
        This constructor sets up the connector with default configuration values required for interacting with the Freshdesk API. It initializes the base URL template (which will be dynamically updated using the domain from authentication details), a comprehensive dictionary of API endpoints for various Freshdesk resources (such as contacts, companies, agents, tickets, discussions, solutions, canned responses, and SLAs), pagination settings, and default query limits. Additionally, it configures connection metadata including the connection type, API name, connection name, schema, database, and OAuth URLs for authorization and token retrieval. The required libraries placeholder is also initialized before invoking the parent class's constructor.
        
        Attributes:
            logo (str): URL of the connector's logo.
            base_url (str): Base URL template for the Freshdesk API, to be formatted with the domain.
            tables (dict): Dictionary mapping Freshdesk API operations to their respective endpoints.
            pagination (dict): Dictionary to manage pagination details (e.g., nextPage).
            limit (dict): Default query limit, set to Freshdesk's limit of 100 records per query.
            connection_type (ConnectionType): Specifies the connection type (set to API).
            api (str): Identifier for the Freshdesk API.
            connection_name (str): Name of the connection.
            schema (str): Database schema used.
            database (str): Database name in use.
            authentication_details (dict): Contains authentication configuration for Basic authentication, including placeholders for username, password, and domain.
            auth_url (str): OAuth authorization URL template.
            token_url (str): OAuth token retrieval URL template.
            main_response_key: Placeholder for main response key (not explicitly used in Freshdesk integration).
            required_libs (list): List of additional libraries required (empty by default).
        """
        self.logo = "https://cdn.dataomnisolutions.com/main/connector_logos/freshdesk.png"
        self.base_url = "https://{domain}.freshdesk.com/"  # To be set dynamically using domain from auth_details
        self.tables = {
            "get_all_contacts": "/api/v2/contacts",
            "get_contact": "/api/v2/contacts/{contact_id}",
            "create_contact": "/api/v2/contacts",
            "update_contact": "/api/v2/contacts/{contact_id}",
            "delete_contact": "/api/v2/contacts/{contact_id}",
            "make_agent": "/api/v2/contacts/{contact_id}/make_agent",
            "merge_contacts": "/api/v2/contacts/merge",
            "restore_contact": "/api/v2/contacts/{contact_id}/restore",
            "send_invite": "/api/v2/contacts/{contact_id}/send_invite",
            "get_all_companies": "/api/v2/companies",
            "get_company": "/api/v2/companies/{company_id}",
            "create_company": "/api/v2/companies",
            "update_company": "/api/v2/companies/{company_id}",
            "delete_company": "/api/v2/companies/{company_id}",
            "get_all_agents": "/api/v2/agents",
            "get_agent": "/api/v2/agents/{agent_id}",
            "create_agent": "/api/v2/agents",
            "update_agent": "/api/v2/agents/{agent_id}",
            "delete_agent": "/api/v2/agents/{agent_id}",
            "get_all_tickets": "/api/v2/tickets",
            "get_ticket": "/api/v2/tickets/{ticket_id}",
            "create_ticket": "/api/v2/tickets",
            "update_ticket": "/api/v2/tickets/{ticket_id}",
            "delete_ticket": "/api/v2/tickets/{ticket_id}",
            "restore_ticket": "/api/v2/tickets/{ticket_id}/restore",
            "search_tickets": "/api/v2/search/tickets?query={query}",
            "get_all_conversations": "/api/v2/tickets/{ticket_id}/conversations",
            "get_conversation": "/api/v2/conversations/{conversation_id}",
            "create_reply": "/api/v2/tickets/{ticket_id}/reply",
            "create_note": "/api/v2/tickets/{ticket_id}/notes",
            "update_conversation": "/api/v2/conversations/{conversation_id}",
            "delete_conversation": "/api/v2/conversations/{conversation_id}",
            "get_all_time_entries": "/api/v2/tickets/{ticket_id}/time_entries",
            "get_time_entry": "/api/v2/time_entries/{time_entry_id}",
            "create_time_entry": "/api/v2/tickets/{ticket_id}/time_entries",
            "update_time_entry": "/api/v2/time_entries/{time_entry_id}",
            "delete_time_entry": "/api/v2/time_entries/{time_entry_id}",
            "get_all_ticket_fields": "/api/v2/ticket_fields",
            "get_all_roles": "/api/v2/roles",
            "get_role": "/api/v2/roles/{role_id}",
            "get_all_groups": "/api/v2/groups",
            "get_group": "/api/v2/groups/{group_id}",
            "create_group": "/api/v2/groups",
            "update_group": "/api/v2/groups/{group_id}",
            "delete_group": "/api/v2/groups/{group_id}",
            "get_all_products": "/api/v2/products",
            "get_product": "/api/v2/products/{product_id}",
            "create_product": "/api/v2/products",
            "update_product": "/api/v2/products/{product_id}",
            "delete_product": "/api/v2/products/{product_id}",
            "get_all_forums": "/api/v2/discussions/forums",
            "get_forum": "/api/v2/discussions/forums/{forum_id}",
            "create_forum": "/api/v2/discussions/forums",
            "update_forum": "/api/v2/discussions/forums/{forum_id}",
            "delete_forum": "/api/v2/discussions/forums/{forum_id}",
            "get_all_topics": "/api/v2/discussions/forums/{forum_id}/topics",
            "get_topic": "/api/v2/discussions/topics/{topic_id}",
            "create_topic": "/api/v2/discussions/forums/{forum_id}/topics",
            "update_topic": "/api/v2/discussions/topics/{topic_id}",
            "delete_topic": "/api/v2/discussions/topics/{topic_id}",
            "get_all_comments": "/api/v2/discussions/topics/{topic_id}/comments",
            "get_comment": "/api/v2/discussions/comments/{comment_id}",
            "create_comment": "/api/v2/discussions/topics/{topic_id}/comments",
            "update_comment": "/api/v2/discussions/comments/{comment_id}",
            "delete_comment": "/api/v2/discussions/comments/{comment_id}",
            "get_all_solution_categories": "/api/v2/solutions/categories",
            "get_solution_category": "/api/v2/solutions/categories/{category_id}",
            "create_solution_category": "/api/v2/solutions/categories",
            "update_solution_category": "/api/v2/solutions/categories/{category_id}",
            "delete_solution_category": "/api/v2/solutions/categories/{category_id}",
            "get_all_solution_folders": "/api/v2/solutions/categories/{category_id}/folders",
            "get_solution_folder": "/api/v2/solutions/folders/{folder_id}",
            "create_solution_folder": "/api/v2/solutions/categories/{category_id}/folders",
            "update_solution_folder": "/api/v2/solutions/folders/{folder_id}",
            "delete_solution_folder": "/api/v2/solutions/folders/{folder_id}",
            "get_all_solution_articles": "/api/v2/solutions/folders/{folder_id}/articles",
            "get_solution_article": "/api/v2/solutions/articles/{article_id}",
            "create_solution_article": "/api/v2/solutions/folders/{folder_id}/articles",
            "update_solution_article": "/api/v2/solutions/articles/{article_id}",
            "delete_solution_article": "/api/v2/solutions/articles/{article_id}",
            "get_all_canned_responses": "/api/v2/canned_responses",
            "get_canned_response": "/api/v2/canned_responses/{canned_response_id}",
            "create_canned_response": "/api/v2/canned_responses",
            "update_canned_response": "/api/v2/canned_responses/{canned_response_id}",
            "delete_canned_response": "/api/v2/canned_responses/{canned_response_id}",
            "get_all_slas": "/api/v2/slas",
            "get_sla": "/api/v2/slas/{sla_id}",
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
        super().__init__()

    def connect_to_api(self, auth_type=None, **auth_params) -> bool:
        domain = auth_params.get('domain')
        token = auth_params.get('username')

        if not domain or not token:
            raise ValueError("Domain and Username must be provided in authentication_details.")

        # Update base_url and auth URLs with the dynamic domain
        self.base_url = self.base_url.format(domain=domain)
        self.auth_url = self.auth_url.format(domain=domain)
        self.token_url = self.token_url.format(domain=domain)

        return super().connect_to_api(auth_type or AuthType.BASIC, **auth_params)

    def fetch_data(self, api_session, table) -> pd.DataFrame:
        arr = []
        endpoint = self.construct_endpoint(table)

        while True:
            paginated_endpoint = self.pagination["nextPage"] or endpoint
            resp = super().fetch_data(api_session, paginated_endpoint)

            if resp:
                arr.append(resp)

            # Check for pagination
            if resp.get("next_page"):
                self.pagination["nextPage"] = resp["next_page"]
            else:
                break

        return self.return_final_df(arr)

    def return_final_df(self, responses) -> pd.DataFrame:
        return super().return_final_df(responses)

    def construct_endpoint(self, endpoint) -> str:
        return super().construct_endpoint(endpoint)

    def get_table_schema(self, api_session, table) -> dict:
        table_data = super().get_table_schema(api_session, table)

        if not table_data:
            return {"error": "No data retrieved. Verify API credentials and endpoint."}

        return DatabaseUtils().dataframe_details(self.return_final_df(table_data))

    def get_table_schema(self, api_session, table) -> dict:
        table_data = super().get_table_schema(api_session, table)

        if not table_data:
            return {"error": "No data retrieved. Verify API credentials and endpoint."}

        return DatabaseUtils().dataframe_details(self.return_final_df(table_data))

    def install_missing_libraries(self) -> bool:
        return super().install_missing_libraries()

    def test_connection(self, api_session) -> bool:
        return super().test_connection(api_session)

    def get_metadata(self, *args, **kwargs) -> dict:
        return super().get_metadata()
