from enum import Enum

class AuthType(Enum):
    SERVICE_ACCOUNT = "service_account"
    BASIC = 'basic'
    BEARER = 'bearer'
    OAUTH2 = 'oauth2'
    

class ConnectionType(Enum):
    DATABASE = "database"
    API = "api"
    STORAGE = "storage"
    
    
class TableAction(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    SELECT = "select"
    TRUNCATE = "truncate"
    DROP = "drop"
    ALTER = "alter"
    

class ColumnActions(Enum):
    ADD = "add"
    DROP = "drop"
    MODIFY = "modify"
    
    
class APIMethod(Enum):
    GET = "get"
    POST = "post"
    PUT = "put"
    PATCH = "patch"
    DELETE = "delete"


class RunStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    RUNNING = "running"

class IntegrationType(Enum):
    FULL_LOAD = "full_load"


class LogsType(Enum):
    INTEGRATION = "integration"
    CELERY = "celery"
    SCHEDULER = "scheduler"
    API = "api"


class SCDType(Enum):
    # (code, description, implementation_steps)
    SCD0 = (
        "scd0",
        "Fixed: Data is static and never updated after insertion.",
        "1. Insert if new | 2. Ignore if exists"
    )
    SCD1 = (
        "scd1",
        "Overwrite: Updates existing records. No history is kept.",
        "1. Insert if new | 2. Update existing row"
    )
    SCD2 = (
        "scd2",
        "Row History: Tracks every change as a new row with timestamps.",
        "1. Insert if new | 2. Expire old row (end_date) | 3. Insert new active row"
    )
    SCD3 = (
        "scd3",
        "Column History: Keeps current and previous value in the same row.",
        "1. Move current to 'previous' column | 2. Update current column"
    )
    SCD4 = (
        "scd4",
        "History Table: Current state in one table, all history in another.",
        "1. Copy old row to History Table | 2. Update Main Table"
    )
    SCD6 = (
        "scd6",
        "Hybrid: Combines Type 1, 2, and 3 for total traceability.",
        "1. Perform Type 2 (new row) | 2. Update 'current' attribute on all historical rows"
    )

    def __init__(self, code, description, steps):
        self.code = code
        self.description = description
        self.steps = steps

    def __str__(self):
        return self.code