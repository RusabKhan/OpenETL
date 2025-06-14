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
        Initialize a Connector instance for interacting with the HubSpot API.
        
        This constructor sets up the configuration required to connect to HubSpot by initializing various
        attributes such as the API logo, base URL, endpoint mappings for numerous HubSpot objects (e.g.,
        contacts, companies, deals, tickets, products, campaigns, and many CRM-related resources), pagination
        settings, and OAuth authentication details. The OAuth endpoints for authorization and token retrieval
        are also defined.
        
        Attributes:
            logo (str): URL of the HubSpot connector logo.
            base_url (str): Base URL for API requests.
            tables (dict): Dictionary mapping operation keys to relative endpoint paths for HubSpot resources.
            pagination (dict): Dictionary containing pagination parameters (e.g., 'after' key for cursor-based paging).
            limit (dict): Dictionary specifying the default record limit per API call.
            connection_type (ConnectionType): Indicator of the connection type (set to API).
            api (str): Identifier for the API ("hubspot").
            connection_name (str): Name of the connection ("hubspot").
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
        self.logo = "https://cdn.dataomnisolutions.com/main/connector_logos/hubspot-icon.svg"
        self.base_url = "https://api.hubapi.com/"
        self.tables = self.tables = {
            "get_all_contacts": "crm/v3/objects/contacts",
            "get_all_companies": "crm/v3/objects/companies",
            "get_all_deals": "crm/v3/objects/deals",
            "get_all_activities": "crm/v3/objects/engagements",
            "get_all_tickets": "crm/v3/objects/tickets",
            "get_all_products": "crm/v3/objects/products",
            "get_all_quotes": "crm/v3/objects/quotes",
            "get_all_line_items": "crm/v3/objects/line_items",
            "get_all_calls": "crm/v3/objects/calls",
            "get_all_emails": "crm/v3/objects/emails",
            "get_all_meetings": "crm/v3/objects/meetings",
            "get_all_notes": "crm/v3/objects/notes",
            "get_all_tasks": "crm/v3/objects/tasks",
            "get_all_feedback_submissions": "crm/v3/objects/feedback_submissions",
            "get_all_marketing_events": "marketing/v3/marketing-events/events",
            "get_all_campaigns": "marketing/v3/campaigns",
            "get_all_contact_lists": "contacts/v1/lists",
            "get_all_forms": "forms/v2/forms",
            "get_all_files": "files/v3/files",
            "get_all_email_events": "email/public/v1/events",
            "get_all_workflows": "automation/v3/workflows",
            "get_all_pipelines": "crm-pipelines/v1/pipelines",
            "get_all_properties": "properties/v1/contacts/properties",
            "get_all_property_groups": "properties/v1/contacts/groups",
            "get_all_owners": "crm/v3/owners",
            "get_all_users": "settings/v3/users",
            "get_all_roles": "settings/v3/roles",
            "get_all_teams": "settings/v3/teams",
            "get_all_audit_logs": "audit-logs/v3/logs",
            "get_all_integrations": "integrations/v1/installed-apps",
            "get_all_subscriptions": "subscriptions/v1/subscriptions",
            "get_all_transactional_emails": "transactional-email/v1/emails",
            "get_all_smtp_tokens": "smtp-tokens/v1/tokens",
            "get_all_webhooks": "webhooks/v3/webhooks",
            "get_all_crm_associations": "crm-associations/v1/associations",
            "get_all_crm_association_definitions": "crm-associations/v1/definitions",
            "get_all_crm_object_schemas": "crm/v3/schemas",
            "get_all_crm_object_types": "crm/v3/object-types",
            "get_all_crm_object_records": "crm/v3/objects",
            "get_all_crm_object_properties": "crm/v3/properties",
            "get_all_crm_object_property_groups": "crm/v3/properties/groups",
            "get_all_crm_object_associations": "crm/v3/associations",
            "get_all_crm_object_search": "crm/v3/objects/search",
            "get_all_crm_object_batch": "crm/v3/objects/batch",
            "get_all_crm_object_merge": "crm/v3/objects/merge",
            "get_all_crm_object_import": "crm/v3/objects/import",
            "get_all_crm_object_export": "crm/v3/objects/export",
            "get_all_crm_object_audit_logs": "crm/v3/objects/audit-logs",
            "get_all_crm_object_association_labels": "crm/v3/associations/labels",
            "get_all_crm_object_association_types": "crm/v3/associations/types",
            "get_all_crm_object_association_definitions": "crm/v3/associations/definitions",
            "get_all_crm_object_association_batch": "crm/v3/associations/batch",
            "get_all_crm_object_association_search": "crm/v3/associations/search",
            "get_all_crm_object_association_import": "crm/v3/associations/import",
            "get_all_crm_object_association_export": "crm/v3/associations/export",
            "get_all_crm_object_association_audit_logs": "crm/v3/associations/audit-logs",
            "get_all_crm_object_association_labels_batch": "crm/v3/associations/labels/batch",
            "get_all_crm_object_association_labels_search": "crm/v3/associations/labels/search",
            "get_all_crm_object_association_labels_import": "crm/v3/associations/labels/import",
            "get_all_crm_object_association_labels_export": "crm/v3/associations/labels/export",
            "get_all_crm_object_association_labels_audit_logs": "crm/v3/associations/labels/audit-logs",
            "get_all_crm_object_association_types_batch": "crm/v3/associations/types/batch",
            "get_all_crm_object_association_types_search": "crm/v3/associations/types/search",
            "get_all_crm_object_association_types_import": "crm/v3/associations/types/import",
            "get_all_crm_object_association_types_export": "crm/v3/associations/types/export",
            "get_all_crm_object_association_types_audit_logs": "crm/v3/associations/types/audit-logs",
            "get_all_crm_object_association_definitions_batch": "crm/v3/associations/definitions/batch",
            "get_all_crm_object_association_definitions_search": "crm/v3/associations/definitions/search",
            "get_all_crm_object_association_definitions_import": "crm/v3/associations/definitions/import",
            "get_all_crm_object_association_definitions_export": "crm/v3/associations/definitions/export",
            "get_all_crm_object_association_definitions_audit_logs": "crm/v3/associations/definitions/audit-logs",
            "get_all_crm_object_association_batch_batch": "crm/v3/associations/batch/batch",
            "get_all_crm_object_association_batch_search": "crm/v3/associations/batch/search",
            "get_all_crm_object_association_batch_import": "crm/v3/associations/batch/import",
            "get_all_crm_object_association_batch_export": "crm/v3/associations/batch/export",
            "get_all_crm_object_association_batch_audit_logs": "crm/v3/associations/batch/audit-logs",
            "get_all_crm_object_association_search_batch": "crm/v3/associations/search/batch",
            "get_all_crm_object_association_search_search": "crm/v3/associations/search/search",
            "get_all_crm_object_association_search_import": "crm/v3/associations/search/import",
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
        self.auth_url = "https://app.hubspot.com/oauth/authorize"
        self.token_url = "https://api.hubapi.com/oauth/v1/token"

        self.main_response_key = "results"
        self.required_libs = []
        super().__init__()


    def connect_to_api(self, auth_type=AuthType.BEARER, **auth_params) -> bool:
        """
        Establish a connection to the API using the specified authentication type and parameters.
        
        This method delegates the connection process to the parent class's implementation of connect_to_api,
        passing the authentication type and any additional authentication parameters provided.
        
        Parameters:
            auth_type (AuthType, optional): The authentication type to use (default is AuthType.BEARER).
            **auth_params: Arbitrary keyword arguments containing additional credentials or parameters required for authentication.
        
        Returns:
            bool: True if the connection was successfully established, False otherwise.
        """
        return super().connect_to_api(auth_type, **auth_params)

    def fetch_data(self, api_session, table) -> pd.DataFrame:
        arr = []
        endpoint = self.construct_endpoint(table)
        while True:
            pagination_query = urlencode(self.pagination)
            limit_query = urlencode(self.limit)
            paginated_endpoint = f"{endpoint}?{pagination_query}&{limit_query}"
            resp = super().fetch_data(api_session, paginated_endpoint, self.main_response_key)

            if "paging_next_after" in resp:
                self.pagination["after"] = resp["paging_next_after"]
                del resp["paging_next_after"]
                del resp["paging_next_link"]
            else:
                break

            yield resp

        

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

    def get_metadata(self,*args, **kwargs) -> dict:
        return super().get_metadata()
