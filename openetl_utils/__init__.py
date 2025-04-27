from .database_utils import *
from .local_connection_utils import *
from .connector_utils import *
from .pipeline_utils import *
from .spark_utils import *
from .enums import *
from .main_api_class import *
from .cache import *
from .celery_utils import *
import tomllib
import pathlib

__version__ = tomllib.loads(
    pathlib.Path(__file__).parent.parent.joinpath("pyproject.toml").read_text()
)["tool"]["poetry"]["version"]

def _print_logo():
    print(f"""
 ██████  ██████  ███████ ███    ██ ███████ ████████ ██      
██    ██ ██   ██ ██      ████   ██ ██         ██    ██      
██    ██ ██████  █████   ██ ██  ██ █████      ██    ██      
██    ██ ██      ██      ██  ██ ██ ██         ██    ██      
 ██████  ██      ███████ ██   ████ ███████    ██    ███████  {__version__}
                                                            
""")
    print("Authored by DataOmni Solutions")
    print("Follow us on Github: https://github.com/RusabKhan/OpenETL")
    print("Visit our website: https://dataomnisolutions.com")


_print_logo()