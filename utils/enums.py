from enum import Enum

class AuthType(Enum):
    BASIC = 'basic'
    BEARER = 'bearer'
    OAUTH2 = 'oauth2'
    

class ConnectionType(Enum):
    DATABASE = "database"
    API = "api"
    
    
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
    