from enum import Enum

class AuthType(Enum):
    BASIC = 'basic'
    BEARER = 'bearer'
    OAUTH2 = 'oauth2'
    

class ConnectionType(Enum):
    DATABASE = "database"
    API = "api"