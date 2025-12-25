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
        Initialize a Business Central 365 Connector instance for interacting with the Microsoft Dynamics 365 Business Central API.

        This constructor sets up the configuration required to connect to Business Central by initializing various
        attributes such as the API logo, base URL template, endpoint mappings for numerous Business Central resources
        (e.g., customers, vendors, items, sales orders, purchase orders, invoices, and other financial/operational data),
        pagination settings, and OAuth authentication details. The OAuth endpoints for authorization and token retrieval
        are also defined.

        Attributes:
            logo (str): URL of the Business Central connector logo.
            base_url (str): Base URL template for API requests (to be formatted with environment and company).
            tables (dict): Dictionary mapping operation keys to relative endpoint paths for Business Central resources.
            pagination (dict): Dictionary containing pagination parameters using OData $skip token.
            limit (dict): Dictionary specifying the default record limit per API call using OData $top.
            connection_type (ConnectionType): Indicator of the connection type (set to API).
            api (str): Identifier for the API ("business_central").
            connection_name (str): Name of the connection ("business_central").
            schema (str): Database schema used ("public").
            database (str): Database name used ("public").
            authentication_details (dict): Authentication configuration for Bearer token with environment and company placeholders.
            auth_url (str): URL for initiating OAuth authorization.
            token_url (str): URL for obtaining OAuth tokens.
            main_response_key (str): Key used to extract the main response data from API responses.
            required_libs (list): List of additional required libraries (empty by default).

        Note:
            The parent class initializer is called at the end of this method to complete the initialization.
            The base_url will be dynamically formatted with the environment (e.g., 'production', 'sandbox') and
            company ID from the authentication details.
        """
        self.logo = "https://cdn.dataomnisolutions.com/main/connector_logos/dynamics-365-business-central.svg"
        self.base_url = "https://api.businesscentral.dynamics.com/v2.0/{environment}/api/v2.0/companies({company_id})/"
        self.tables = {
            # Customer Management
            "get_all_customers": "customers",
            "get_customer": "customers({customer_id})",
            "create_customer": "customers",
            "update_customer": "customers({customer_id})",
            "delete_customer": "customers({customer_id})",

            # Vendor Management
            "get_all_vendors": "vendors",
            "get_vendor": "vendors({vendor_id})",
            "create_vendor": "vendors",
            "update_vendor": "vendors({vendor_id})",
            "delete_vendor": "vendors({vendor_id})",

            # Items/Products
            "get_all_items": "items",
            "get_item": "items({item_id})",
            "create_item": "items",
            "update_item": "items({item_id})",
            "delete_item": "items({item_id})",

            # Item Categories
            "get_all_item_categories": "itemCategories",
            "get_item_category": "itemCategories({category_id})",
            "create_item_category": "itemCategories",
            "update_item_category": "itemCategories({category_id})",

            # Sales Documents
            "get_all_sales_quotes": "salesQuotes",
            "get_sales_quote": "salesQuotes({quote_id})",
            "create_sales_quote": "salesQuotes",
            "update_sales_quote": "salesQuotes({quote_id})",
            "delete_sales_quote": "salesQuotes({quote_id})",

            "get_all_sales_orders": "salesOrders",
            "get_sales_order": "salesOrders({order_id})",
            "create_sales_order": "salesOrders",
            "update_sales_order": "salesOrders({order_id})",
            "delete_sales_order": "salesOrders({order_id})",

            "get_all_sales_invoices": "salesInvoices",
            "get_sales_invoice": "salesInvoices({invoice_id})",
            "create_sales_invoice": "salesInvoices",
            "update_sales_invoice": "salesInvoices({invoice_id})",
            "post_sales_invoice": "salesInvoices({invoice_id})/Microsoft.NAV.post",

            "get_all_sales_credit_memos": "salesCreditMemos",
            "get_sales_credit_memo": "salesCreditMemos({credit_memo_id})",
            "create_sales_credit_memo": "salesCreditMemos",
            "update_sales_credit_memo": "salesCreditMemos({credit_memo_id})",

            # Sales Lines
            "get_all_sales_quote_lines": "salesQuoteLines",
            "get_sales_quote_line": "salesQuoteLines({line_id})",
            "create_sales_quote_line": "salesQuoteLines",
            "update_sales_quote_line": "salesQuoteLines({line_id})",

            "get_all_sales_order_lines": "salesOrderLines",
            "get_sales_order_line": "salesOrderLines({line_id})",
            "create_sales_order_line": "salesOrderLines",
            "update_sales_order_line": "salesOrderLines({line_id})",

            "get_all_sales_invoice_lines": "salesInvoiceLines",
            "get_sales_invoice_line": "salesInvoiceLines({line_id})",
            "create_sales_invoice_line": "salesInvoiceLines",
            "update_sales_invoice_line": "salesInvoiceLines({line_id})",

            # Purchase Documents
            "get_all_purchase_invoices": "purchaseInvoices",
            "get_purchase_invoice": "purchaseInvoices({invoice_id})",
            "create_purchase_invoice": "purchaseInvoices",
            "update_purchase_invoice": "purchaseInvoices({invoice_id})",
            "post_purchase_invoice": "purchaseInvoices({invoice_id})/Microsoft.NAV.post",

            "get_all_purchase_orders": "purchaseOrders",
            "get_purchase_order": "purchaseOrders({order_id})",
            "create_purchase_order": "purchaseOrders",
            "update_purchase_order": "purchaseOrders({order_id})",

            # Purchase Lines
            "get_all_purchase_invoice_lines": "purchaseInvoiceLines",
            "get_purchase_invoice_line": "purchaseInvoiceLines({line_id})",
            "create_purchase_invoice_line": "purchaseInvoiceLines",
            "update_purchase_invoice_line": "purchaseInvoiceLines({line_id})",

            "get_all_purchase_order_lines": "purchaseOrderLines",
            "get_purchase_order_line": "purchaseOrderLines({line_id})",
            "create_purchase_order_line": "purchaseOrderLines",
            "update_purchase_order_line": "purchaseOrderLines({line_id})",

            # General Ledger
            "get_all_accounts": "accounts",
            "get_account": "accounts({account_id})",

            "get_all_journal_lines": "journalLines",
            "get_journal_line": "journalLines({line_id})",
            "create_journal_line": "journalLines",
            "update_journal_line": "journalLines({line_id})",

            "get_all_journals": "journals",
            "get_journal": "journals({journal_id})",

            # Financial Management
            "get_all_aged_accounts_payable": "agedAccountsPayable",
            "get_all_aged_accounts_receivable": "agedAccountsReceivable",

            "get_all_balance_sheet": "balanceSheet",
            "get_all_income_statement": "incomeStatement",
            "get_all_cash_flow_statement": "cashFlowStatement",
            "get_all_retained_earnings_statement": "retainedEarningsStatement",
            "get_all_trial_balance": "trialBalance",

            # Tax
            "get_all_tax_areas": "taxAreas",
            "get_tax_area": "taxAreas({tax_area_id})",

            "get_all_tax_groups": "taxGroups",
            "get_tax_group": "taxGroups({tax_group_id})",

            # Payments
            "get_all_payment_methods": "paymentMethods",
            "get_payment_method": "paymentMethods({method_id})",

            "get_all_payment_terms": "paymentTerms",
            "get_payment_term": "paymentTerms({term_id})",
            "create_payment_term": "paymentTerms",
            "update_payment_term": "paymentTerms({term_id})",

            "get_all_customer_payments": "customerPayments",
            "get_customer_payment": "customerPayments({payment_id})",
            "create_customer_payment": "customerPayments",
            "update_customer_payment": "customerPayments({payment_id})",

            # Dimensions
            "get_all_dimensions": "dimensions",
            "get_dimension": "dimensions({dimension_id})",

            "get_all_dimension_values": "dimensionValues",
            "get_dimension_value": "dimensionValues({value_id})",

            # Employees
            "get_all_employees": "employees",
            "get_employee": "employees({employee_id})",
            "create_employee": "employees",
            "update_employee": "employees({employee_id})",

            # Time Sheets
            "get_all_time_registration_entries": "timeRegistrationEntries",
            "get_time_registration_entry": "timeRegistrationEntries({entry_id})",
            "create_time_registration_entry": "timeRegistrationEntries",

            # Projects
            "get_all_projects": "projects",
            "get_project": "projects({project_id})",
            "create_project": "projects",
            "update_project": "projects({project_id})",

            # Units of Measure
            "get_all_units_of_measure": "unitsOfMeasure",
            "get_unit_of_measure": "unitsOfMeasure({unit_id})",
            "create_unit_of_measure": "unitsOfMeasure",
            "update_unit_of_measure": "unitsOfMeasure({unit_id})",

            # Shipment Methods
            "get_all_shipment_methods": "shipmentMethods",
            "get_shipment_method": "shipmentMethods({method_id})",

            # Countries/Regions
            "get_all_countries_regions": "countriesRegions",
            "get_country_region": "countriesRegions({region_id})",

            # Currencies
            "get_all_currencies": "currencies",
            "get_currency": "currencies({currency_id})",

            # Company Information
            "get_all_company_information": "companyInformation",
            "get_company_information": "companyInformation({info_id})",
            "update_company_information": "companyInformation({info_id})",

            # Bank Accounts
            "get_all_bank_accounts": "bankAccounts",
            "get_bank_account": "bankAccounts({account_id})",
            "create_bank_account": "bankAccounts",
            "update_bank_account": "bankAccounts({account_id})",
        }

        self.pagination = {
            "$skip": 0
        }
        self.limit = {"$top": 100}
        self.connection_type = ConnectionType.API
        self.api = "business_central"
        self.connection_name = "business_central"
        self.schema = "public"
        self.database = "public"
        self.authentication_details = {AuthType.BEARER: {
            "token": "",
            "environment": "",  # e.g., 'production' or 'sandbox'
            "company_id": ""  # Company GUID
        }}
        self.auth_url = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
        self.token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"

        self.main_response_key = "value"
        self.required_libs = []
        super().__init__()

    def connect_to_api(self, auth_type=AuthType.BEARER, **auth_params) -> bool:
        """
        Establish a connection to the Business Central API using the specified authentication type and parameters.

        This method updates the base_url with the environment and company_id from auth_params, then delegates
        the connection process to the parent class's implementation of connect_to_api, passing the authentication
        type and any additional authentication parameters provided.

        Parameters:
            auth_type (AuthType, optional): The authentication type to use (default is AuthType.BEARER).
            **auth_params: Arbitrary keyword arguments containing additional credentials or parameters required
                          for authentication, including 'environment' and 'company_id'.

        Returns:
            bool: True if the connection was successfully established, False otherwise.
        """
        environment = auth_params.get('environment', 'production')
        company_id = auth_params.get('company_id', '')

        if not company_id:
            raise ValueError("company_id must be provided in authentication parameters")

        # Update base_url with environment and company_id
        self.base_url = self.base_url.format(environment=environment, company_id=company_id)

        return super().connect_to_api(auth_type, **auth_params)

    def fetch_data(self, api_session, table) -> pd.DataFrame:
        """
        Fetch data from Business Central API with OData pagination support.

        This method constructs paginated requests using OData query parameters ($skip and $top)
        and yields results until all data is retrieved. It handles the 'value' response key
        and '@odata.nextLink' for pagination.

        Parameters:
            api_session: The authenticated API session object.
            table (str): The table/endpoint identifier from the tables dictionary.

        Yields:
            dict: Response data containing records and pagination information.
        """
        endpoint = self.construct_endpoint(table)
        skip = 0
        top = self.limit.get("$top", 100)

        while True:
            # Construct paginated endpoint with OData parameters
            separator = '&' if '?' in endpoint else '?'
            paginated_endpoint = f"{endpoint}{separator}$skip={skip}&$top={top}"

            resp = super().fetch_data(api_session, paginated_endpoint, self.main_response_key)
            yield resp

            # Check for OData nextLink or if we got fewer records than requested
            if "@odata.nextLink" in resp:
                skip += top
            elif "value" in resp and len(resp["value"]) < top:
                # Got fewer records than limit, we're done
                break
            elif "value" not in resp or len(resp["value"]) == 0:
                # No more data
                break
            else:
                skip += top

    def return_final_df(self, responses) -> pd.DataFrame:
        """
        Convert API responses to a pandas DataFrame.

        Parameters:
            responses (list): List of response dictionaries from the API.

        Returns:
            pd.DataFrame: Normalized DataFrame containing all fetched records.
        """
        return super().return_final_df(responses)

    def construct_endpoint(self, endpoint) -> str:
        """
        Construct the complete endpoint URL from the endpoint key.

        Parameters:
            endpoint (str): The endpoint key from the tables dictionary.

        Returns:
            str: The complete endpoint URL.
        """
        return super().construct_endpoint(endpoint)

    def get_table_schema(self, api_session, table) -> dict:
        """
        Retrieve the schema information for a specific table/entity.

        Parameters:
            api_session: The authenticated API session object.
            table (str): The table/endpoint identifier.

        Returns:
            dict: Schema information for the specified table.
        """
        return super().get_table_schema(api_session, table)

    def install_missing_libraries(self) -> bool:
        """
        Install any missing required libraries.

        Returns:
            bool: True if all libraries are installed successfully, False otherwise.
        """
        return super().install_missing_libraries()

    def test_connection(self, api_session) -> bool:
        """
        Test the connection to the Business Central API.

        Parameters:
            api_session: The authenticated API session object.

        Returns:
            bool: True if the connection test is successful, False otherwise.
        """
        return super().test_connection(api_session)

    def get_metadata(self, *args, **kwargs) -> dict:
        """
        Retrieve metadata about available endpoints and resources.

        Returns:
            dict: Dictionary containing metadata about the Business Central API endpoints.
        """
        return super().get_metadata()