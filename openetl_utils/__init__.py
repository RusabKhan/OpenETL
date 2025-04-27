import tomllib
import pathlib
import sys


def _get_version():
    try:
        pyproject_path = pathlib.Path(__file__).parent.parent / "pyproject.toml"
        if not pyproject_path.is_file():
            raise FileNotFoundError("pyproject.toml not found")

        content = pyproject_path.read_text(encoding="utf-8")
        data = tomllib.loads(content)
        version = data.get("project", {}).get("version")
        if not version:
            raise ValueError("Version not found in pyproject.toml under [project]")
        return version
    except Exception as e:
        print(f"[WARN] Could not read version from pyproject.toml: {e}", file=sys.stderr)
        return "0.0.0"


__version__ = _get_version()

from .celery_utils import *
from .main_api_class import *
from .connector_utils import *
from .pipeline_utils import *

from .database_utils import *
from .local_connection_utils import *
from .spark_utils import *
from .enums import *
from .cache import *


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
