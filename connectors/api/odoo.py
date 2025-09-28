from openetl_utils.database_utils import DatabaseUtils
from openetl_utils.main_api_class import API
from openetl_utils.enums import *
from urllib.parse import urlencode
import sys
import os
import pandas as pd
import xmlrpc.client

sys.path.append(os.getenv('OPENETL_HOME'))


class Connector(API):

    def __init__(self):
        """
        Initialize an Odoo Connector instance.

        This constructor sets up the connector with default configuration values required for interacting with the Odoo API.
        It initializes the base URL template (which will be dynamically updated using the server URL from authentication details),
        a comprehensive dictionary of API endpoints for various Odoo resources including partners (contacts/customers),
        products, sales orders, purchase orders, invoices, inventory, users, companies, and more. The connector supports
        both XML-RPC (standard Odoo API) and REST API endpoints (if REST API module is installed).

        Attributes:
            logo (str): URL of the connector's logo.
            base_url (str): Base URL template for the Odoo server, to be formatted with the server URL.
            tables (dict): Dictionary mapping Odoo API operations to their respective endpoints.
            pagination (dict): Dictionary to manage pagination details (e.g., nextPage).
            limit (dict): Default query limit, set to 100 records per query.
            connection_type (ConnectionType): Specifies the connection type (set to API).
            api (str): Identifier for the Odoo API.
            connection_name (str): Name of the connection.
            schema (str): Database schema used.
            database (str): Database name in use.
            authentication_details (dict): Contains authentication configuration for Basic authentication, including
                                         placeholders for username, password, database, and server URL.
            auth_url (str): OAuth authorization URL template.
            token_url (str): OAuth token retrieval URL template.
            main_response_key: Placeholder for main response key.
            required_libs (list): List of additional libraries required.
        """
        self.logo = "https://cdn.dataomnisolutions.com/main/connector_logos/odoo.png"
        self.base_url = "{server_url}"  # To be set dynamically using server_url from auth_details
        self.tables = {
            # Partners (Contacts/Customers/Vendors) - res.partner
            "get_all_partners": "/api/v1/partners",
            "get_partner": "/api/v1/partners/{partner_id}",
            "create_partner": "/api/v1/partners",
            "update_partner": "/api/v1/partners/{partner_id}",
            "delete_partner": "/api/v1/partners/{partner_id}",
            "search_partners": "/api/v1/partners/search",

            # Products - product.product & product.template
            "get_all_products": "/api/v1/products",
            "get_product": "/api/v1/products/{product_id}",
            "create_product": "/api/v1/products",
            "update_product": "/api/v1/products/{product_id}",
            "delete_product": "/api/v1/products/{product_id}",
            "get_product_templates": "/api/v1/product/templates",
            "get_product_template": "/api/v1/product/templates/{template_id}",
            "create_product_template": "/api/v1/product/templates",
            "update_product_template": "/api/v1/product/templates/{template_id}",

            # Sales Orders - sale.order
            "get_all_sale_orders": "/api/v1/sale/orders",
            "get_sale_order": "/api/v1/sale/orders/{order_id}",
            "create_sale_order": "/api/v1/sale/orders",
            "update_sale_order": "/api/v1/sale/orders/{order_id}",
            "delete_sale_order": "/api/v1/sale/orders/{order_id}",
            "confirm_sale_order": "/api/v1/sale/orders/{order_id}/confirm",

            # Sale Order Lines - sale.order.line
            "get_sale_order_lines": "/api/v1/sale/order/lines",
            "get_sale_order_line": "/api/v1/sale/order/lines/{line_id}",
            "create_sale_order_line": "/api/v1/sale/order/lines",
            "update_sale_order_line": "/api/v1/sale/order/lines/{line_id}",

            # Purchase Orders - purchase.order
            "get_all_purchase_orders": "/api/v1/purchase/orders",
            "get_purchase_order": "/api/v1/purchase/orders/{order_id}",
            "create_purchase_order": "/api/v1/purchase/orders",
            "update_purchase_order": "/api/v1/purchase/orders/{order_id}",
            "delete_purchase_order": "/api/v1/purchase/orders/{order_id}",
            "confirm_purchase_order": "/api/v1/purchase/orders/{order_id}/confirm",

            # Purchase Order Lines - purchase.order.line
            "get_purchase_order_lines": "/api/v1/purchase/order/lines",
            "get_purchase_order_line": "/api/v1/purchase/order/lines/{line_id}",
            "create_purchase_order_line": "/api/v1/purchase/order/lines",
            "update_purchase_order_line": "/api/v1/purchase/order/lines/{line_id}",

            # Invoices - account.move (Customer & Vendor Bills)
            "get_all_invoices": "/api/v1/invoices",
            "get_invoice": "/api/v1/invoices/{invoice_id}",
            "create_invoice": "/api/v1/invoices",
            "update_invoice": "/api/v1/invoices/{invoice_id}",
            "delete_invoice": "/api/v1/invoices/{invoice_id}",
            "validate_invoice": "/api/v1/invoices/{invoice_id}/validate",
            "get_customer_invoices": "/api/v1/invoices/customer",
            "get_vendor_bills": "/api/v1/invoices/vendor",

            # Invoice Lines - account.move.line
            "get_invoice_lines": "/api/v1/invoice/lines",
            "get_invoice_line": "/api/v1/invoice/lines/{line_id}",

            # Inventory/Stock - stock.picking, stock.move
            "get_all_pickings": "/api/v1/stock/pickings",
            "get_picking": "/api/v1/stock/pickings/{picking_id}",
            "create_picking": "/api/v1/stock/pickings",
            "update_picking": "/api/v1/stock/pickings/{picking_id}",
            "validate_picking": "/api/v1/stock/pickings/{picking_id}/validate",
            "get_stock_moves": "/api/v1/stock/moves",
            "get_stock_move": "/api/v1/stock/moves/{move_id}",

            # Inventory Locations - stock.location
            "get_all_locations": "/api/v1/stock/locations",
            "get_location": "/api/v1/stock/locations/{location_id}",
            "create_location": "/api/v1/stock/locations",
            "update_location": "/api/v1/stock/locations/{location_id}",

            # Inventory Quants - stock.quant
            "get_stock_quants": "/api/v1/stock/quants",
            "get_stock_quant": "/api/v1/stock/quants/{quant_id}",

            # Users - res.users
            "get_all_users": "/api/v1/users",
            "get_user": "/api/v1/users/{user_id}",
            "create_user": "/api/v1/users",
            "update_user": "/api/v1/users/{user_id}",
            "delete_user": "/api/v1/users/{user_id}",

            # Companies - res.company
            "get_all_companies": "/api/v1/companies",
            "get_company": "/api/v1/companies/{company_id}",
            "create_company": "/api/v1/companies",
            "update_company": "/api/v1/companies/{company_id}",

            # HR Employees - hr.employee
            "get_all_employees": "/api/v1/employees",
            "get_employee": "/api/v1/employees/{employee_id}",
            "create_employee": "/api/v1/employees",
            "update_employee": "/api/v1/employees/{employee_id}",
            "delete_employee": "/api/v1/employees/{employee_id}",

            # Projects - project.project
            "get_all_projects": "/api/v1/projects",
            "get_project": "/api/v1/projects/{project_id}",
            "create_project": "/api/v1/projects",
            "update_project": "/api/v1/projects/{project_id}",
            "delete_project": "/api/v1/projects/{project_id}",

            # Project Tasks - project.task
            "get_all_tasks": "/api/v1/project/tasks",
            "get_task": "/api/v1/project/tasks/{task_id}",
            "create_task": "/api/v1/project/tasks",
            "update_task": "/api/v1/project/tasks/{task_id}",
            "delete_task": "/api/v1/project/tasks/{task_id}",

            # CRM Leads/Opportunities - crm.lead
            "get_all_leads": "/api/v1/crm/leads",
            "get_lead": "/api/v1/crm/leads/{lead_id}",
            "create_lead": "/api/v1/crm/leads",
            "update_lead": "/api/v1/crm/leads/{lead_id}",
            "delete_lead": "/api/v1/crm/leads/{lead_id}",
            "convert_lead": "/api/v1/crm/leads/{lead_id}/convert",

            # Calendar Events - calendar.event
            "get_all_events": "/api/v1/calendar/events",
            "get_event": "/api/v1/calendar/events/{event_id}",
            "create_event": "/api/v1/calendar/events",
            "update_event": "/api/v1/calendar/events/{event_id}",
            "delete_event": "/api/v1/calendar/events/{event_id}",

            # Manufacturing Orders - mrp.production (if MRP module is installed)
            "get_all_manufacturing_orders": "/api/v1/mrp/productions",
            "get_manufacturing_order": "/api/v1/mrp/productions/{production_id}",
            "create_manufacturing_order": "/api/v1/mrp/productions",
            "update_manufacturing_order": "/api/v1/mrp/productions/{production_id}",

            # Account Journal Entries - account.move (all types)
            "get_all_journal_entries": "/api/v1/account/moves",
            "get_journal_entry": "/api/v1/account/moves/{move_id}",

            # Payment Terms - account.payment.term
            "get_all_payment_terms": "/api/v1/account/payment/terms",
            "get_payment_term": "/api/v1/account/payment/terms/{term_id}",

            # Categories - product.category
            "get_all_product_categories": "/api/v1/product/categories",
            "get_product_category": "/api/v1/product/categories/{category_id}",
            "create_product_category": "/api/v1/product/categories",
            "update_product_category": "/api/v1/product/categories/{category_id}",

            # Taxes - account.tax
            "get_all_taxes": "/api/v1/account/taxes",
            "get_tax": "/api/v1/account/taxes/{tax_id}",

            # XML-RPC endpoints (standard Odoo API)
            "xmlrpc_common": "/xmlrpc/2/common",
            "xmlrpc_object": "/xmlrpc/2/object",
        }

        self.pagination = {
            "nextPage": None,
            "offset": 0
        }
        self.limit = {"limit": 100}  # Default limit per query
        self.connection_type = ConnectionType.API
        self.api = "odoo"
        self.connection_name = "odoo"
        self.schema = "public"
        self.database = "public"
        self.authentication_details = {AuthType.BASIC: {
            "username": "",  # Odoo username
            "password": "",  # Odoo password or API key
            "database": "",  # Odoo database name
            "server_url": ""  # Odoo server URL (e.g., https://mycompany.odoo.com)
        }}
        self.auth_url = "{server_url}/oauth2/authorize"
        self.token_url = "{server_url}/oauth2/token"

        self.main_response_key = None  # Odoo doesn't require this explicitly
        self.required_libs = []
        super().__init__()

    def connect_to_api(self, auth_type=None, **auth_params) -> bool:
        """
        Connects to Odoo API using the specified authentication mechanism.

        This method supports both REST API authentication and XML-RPC authentication.
        For REST API, it uses HTTP Basic Auth or Bearer tokens.
        For XML-RPC, it creates XML-RPC client connections and authenticates.

        Parameters:
            auth_type: The authentication type (defaults to BASIC)
            **auth_params: Authentication parameters including username, password, database, server_url

        Returns:
            bool: True if connection is successful, False otherwise
        """
        server_url = auth_params.get('server_url')
        database = auth_params.get('database')
        username = auth_params.get('username')
        password = auth_params.get('password')

        if not server_url or not database or not username or not password:
            raise ValueError("Server URL, Database, Username, and Password must be provided in authentication_details.")

        # Clean up server URL (remove trailing slash)
        if server_url.endswith('/'):
            server_url = server_url[:-1]

        # Update base_url and auth URLs with the dynamic server URL
        self.base_url = server_url
        self.auth_url = self.auth_url.format(server_url=server_url)
        self.token_url = self.token_url.format(server_url=server_url)

        # Store connection details for XML-RPC usage
        self.xmlrpc_server_url = server_url
        self.xmlrpc_database = database
        self.xmlrpc_username = username
        self.xmlrpc_password = password

        return super().connect_to_api(auth_type or AuthType.BASIC, **auth_params)

    def get_xmlrpc_connection(self):
        """
        Creates XML-RPC connection to Odoo server.

        Returns:
            tuple: (common, models, uid) where common and models are XML-RPC clients, uid is user id
        """
        try:
            # Create XML-RPC clients
            common = xmlrpc.client.ServerProxy(f"{self.xmlrpc_server_url}/xmlrpc/2/common")
            models = xmlrpc.client.ServerProxy(f"{self.xmlrpc_server_url}/xmlrpc/2/object")

            # Authenticate and get user ID
            uid = common.authenticate(self.xmlrpc_database, self.xmlrpc_username, self.xmlrpc_password, {})

            if not uid:
                raise ValueError("XML-RPC Authentication failed")

            return common, models, uid
        except Exception as e:
            raise ConnectionError(f"Failed to create XML-RPC connection: {str(e)}")

    def fetch_data_xmlrpc(self, model_name, method='search_read', domain=None, fields=None, limit=None, offset=None):
        """
        Fetch data using XML-RPC interface.

        Parameters:
            model_name (str): Odoo model name (e.g., 'res.partner', 'product.product')
            method (str): Method to call ('search_read', 'read', 'search', etc.)
            domain (list): Search domain filters
            fields (list): Fields to fetch
            limit (int): Number of records to fetch
            offset (int): Offset for pagination

        Returns:
            list: List of records
        """
        try:
            common, models, uid = self.get_xmlrpc_connection()

            # Set defaults
            if domain is None:
                domain = []
            if limit is None:
                limit = self.limit.get("limit", 100)
            if offset is None:
                offset = 0

            if method == 'search_read':
                # search_read combines search and read operations
                kwargs = {
                    'limit': limit,
                    'offset': offset
                }
                if fields:
                    kwargs['fields'] = fields

                records = models.execute_kw(
                    self.xmlrpc_database, uid, self.xmlrpc_password,
                    model_name, 'search_read',
                    [domain], kwargs
                )
            elif method == 'search':
                # Search for record IDs only
                records = models.execute_kw(
                    self.xmlrpc_database, uid, self.xmlrpc_password,
                    model_name, 'search',
                    [domain], {'limit': limit, 'offset': offset}
                )
            elif method == 'read':
                # Read specific records by ID
                if not domain:
                    raise ValueError("Domain (record IDs) required for 'read' method")
                kwargs = {}
                if fields:
                    kwargs['fields'] = fields
                records = models.execute_kw(
                    self.xmlrpc_database, uid, self.xmlrpc_password,
                    model_name, 'read',
                    [domain], kwargs
                )
            else:
                # Generic method call
                records = models.execute_kw(
                    self.xmlrpc_database, uid, self.xmlrpc_password,
                    model_name, method,
                    [domain] if domain else []
                )

            return records if records else []
        except Exception as e:
            raise RuntimeError(f"XML-RPC fetch failed: {str(e)}")

    def fetch_data(self, api_session, table) -> pd.DataFrame:
        """
        Fetches data from the Odoo API with pagination support.

        This method handles both REST API calls and XML-RPC calls based on the table endpoint.
        For XML-RPC endpoints, it uses the fetch_data_xmlrpc method.
        For REST API endpoints, it uses the parent class method with pagination.

        Parameters:
            api_session: The API session object
            table (str): The table/endpoint identifier

        Returns:
            pd.DataFrame: DataFrame containing the fetched data
        """
        arr = []

        # Check if this is an XML-RPC call
        if table in ['xmlrpc_common', 'xmlrpc_object']:
            # Handle XML-RPC specific calls
            if table == 'xmlrpc_common':
                # Get version info or other common operations
                common, _, _ = self.get_xmlrpc_connection()
                version_info = common.version()
                return pd.DataFrame([version_info])
            else:
                # This would need specific model and method parameters
                # For now, return empty DataFrame
                return pd.DataFrame()

        # Check if we should use XML-RPC for standard model operations
        model_mapping = {
            "get_all_partners": "res.partner",
            "get_all_products": "product.product",
            "get_product_templates": "product.template",
            "get_all_sale_orders": "sale.order",
            "get_sale_order_lines": "sale.order.line",
            "get_all_purchase_orders": "purchase.order",
            "get_purchase_order_lines": "purchase.order.line",
            "get_all_invoices": "account.move",
            "get_invoice_lines": "account.move.line",
            "get_all_pickings": "stock.picking",
            "get_stock_moves": "stock.move",
            "get_all_locations": "stock.location",
            "get_stock_quants": "stock.quant",
            "get_all_users": "res.users",
            "get_all_companies": "res.company",
            "get_all_employees": "hr.employee",
            "get_all_projects": "project.project",
            "get_all_tasks": "project.task",
            "get_all_leads": "crm.lead",
            "get_all_events": "calendar.event",
            "get_all_manufacturing_orders": "mrp.production",
            "get_all_journal_entries": "account.move",
            "get_all_payment_terms": "account.payment.term",
            "get_all_product_categories": "product.category",
            "get_all_taxes": "account.tax"
        }

        if table in model_mapping:
            # Use XML-RPC for better compatibility
            model_name = model_mapping[table]
            offset = 0
            limit = self.limit.get("limit", 100)

            while True:
                try:
                    records = self.fetch_data_xmlrpc(
                        model_name=model_name,
                        method='search_read',
                        limit=limit,
                        offset=offset
                    )

                    if not records:
                        break

                    arr.extend(records)

                    # Check if we got fewer records than limit (last page)
                    if len(records) < limit:
                        break

                    offset += limit

                except Exception as e:
                    print(f"Error fetching data from {model_name}: {str(e)}")
                    break

            return pd.DataFrame(arr) if arr else pd.DataFrame()

        else:
            # Try REST API approach (if REST API module is installed)
            endpoint = self.construct_endpoint(table)
            offset = 0
            limit = self.limit.get("limit", 100)

            while True:
                try:
                    # Add pagination parameters
                    paginated_endpoint = f"{endpoint}?limit={limit}&offset={offset}"
                    resp = super().fetch_data(api_session, paginated_endpoint)

                    if resp and isinstance(resp, dict):
                        # Check if response has data
                        data = resp.get('data', resp.get('result', [resp] if resp else []))
                        if not data:
                            break
                        arr.extend(data if isinstance(data, list) else [data])

                        # Check if we got fewer records than limit (last page)
                        if len(data) < limit:
                            break
                    else:
                        break

                    offset += limit

                except Exception as e:
                    print(f"Error fetching REST data from {endpoint}: {str(e)}")
                    break

            return self.return_final_df(arr) if arr else pd.DataFrame()

    def return_final_df(self, responses) -> pd.DataFrame:
        """
        Generates a pandas DataFrame from the API responses.

        Parameters:
            responses (list): List of response dictionaries

        Returns:
            pd.DataFrame: Normalized DataFrame
        """
        if not responses:
            return pd.DataFrame()

        # Handle XML-RPC responses (list of dictionaries)
        if isinstance(responses, list) and all(isinstance(item, dict) for item in responses):
            return pd.json_normalize(responses)

        return super().return_final_df(responses)

    def construct_endpoint(self, endpoint) -> str:
        """
        Constructs the full endpoint URL.

        Parameters:
            endpoint (str): The endpoint key

        Returns:
            str: The complete endpoint URL
        """
        endpoint_path = self.tables.get(endpoint)
        if not endpoint_path:
            raise ValueError(f"Unknown endpoint: {endpoint}")

        # Handle XML-RPC endpoints
        if endpoint_path.startswith('/xmlrpc'):
            return f"{self.base_url}{endpoint_path}"

        # Handle REST API endpoints
        return f"{self.base_url}{endpoint_path}"

    def get_table_schema(self, api_session, table) -> dict:
        """
        Get the schema details of a table/model.

        Parameters:
            api_session: The API session
            table (str): The table identifier

        Returns:
            dict: Schema information
        """
        try:
            # For XML-RPC models, get field definitions
            model_mapping = {
                "get_all_partners": "res.partner",
                "get_all_products": "product.product",
                "get_product_templates": "product.template",
                "get_all_sale_orders": "sale.order",
                "get_all_users": "res.users",
                "get_all_companies": "res.company",
            }

            if table in model_mapping:
                model_name = model_mapping[table]
                common, models, uid = self.get_xmlrpc_connection()

                # Get field definitions
                fields_info = models.execute_kw(
                    self.xmlrpc_database, uid, self.xmlrpc_password,
                    model_name, 'fields_get', []
                )

                return {
                    "model": model_name,
                    "fields": fields_info
                }
            else:
                # Try REST API approach
                return super().get_table_schema(api_session, table)

        except Exception as e:
            return {"error": f"Failed to retrieve schema: {str(e)}"}

    def install_missing_libraries(self) -> bool:
        """
        Install any missing required libraries.

        Returns:
            bool: True if successful
        """
        return super().install_missing_libraries()

    def test_connection(self, api_session) -> bool:
        """
        Test the connection to Odoo server.

        Parameters:
            api_session: The API session

        Returns:
            bool: True if connection is successful
        """
        try:
            # Test XML-RPC connection
            common, models, uid = self.get_xmlrpc_connection()

            # Try to get version info
            version = common.version()
            if version:
                return True

            # Alternative: try to read user info
            user_info = models.execute_kw(
                self.xmlrpc_database, uid, self.xmlrpc_password,
                'res.users', 'read', [uid], {'fields': ['name', 'login']}
            )

            return bool(user_info)

        except Exception as e:
            print(f"Connection test failed: {str(e)}")
            return False

    def get_metadata(self, *args, **kwargs) -> dict:
        """
        Returns the metadata for the Odoo API.

        Returns:
            dict: Dictionary containing available endpoints and models
        """
        return {
            "public": self.tables,
            "models": {
                "res.partner": "Partners (Contacts, Customers, Vendors)",
                "product.product": "Products",
                "product.template": "Product Templates",
                "sale.order": "Sales Orders",
                "sale.order.line": "Sales Order Lines",
                "purchase.order": "Purchase Orders",
                "purchase.order.line": "Purchase Order Lines",
                "account.move": "Invoices & Journal Entries",
                "account.move.line": "Invoice & Journal Entry Lines",
                "stock.picking": "Inventory Transfers",
                "stock.move": "Stock Moves",
                "stock.location": "Inventory Locations",
                "stock.quant": "Stock Quantities",
                "res.users": "Users",
                "res.company": "Companies",
                "hr.employee": "Employees",
                "project.project": "Projects",
                "project.task": "Tasks",
                "crm.lead": "CRM Leads/Opportunities",
                "calendar.event": "Calendar Events"
            }
        }