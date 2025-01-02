import glob
import os
import sys
import subprocess

# Insert project directories into sys.path for module access
sys.path.insert(0, os.path.abspath('../backend'))
sys.path.insert(0, os.path.abspath('../backend/app'))
sys.path.insert(0, os.path.abspath('../backend/app/middlewares'))
sys.path.insert(0, os.path.abspath('../backend/app/models'))

sys.path.insert(0, os.path.abspath('../utils/'))
sys.path.insert(0, os.path.abspath('../utils/__migrations__'))
sys.path.insert(0, os.path.abspath('..'))

# Project Information
project = 'OpenETL'
copyright = '2025, DataOmni Solutions'
author = 'DataOmni Solutions'
release = '1.0.0'

# Sphinx Extension Configuration
extensions = [
    'sphinx.ext.autodoc',           # Automatically generate documentation from docstrings
    'sphinx.ext.autosummary',       # Generate summaries for modules
    'sphinx.ext.napoleon',          # Google-style docstrings support
    'sphinx_autodoc_typehints',     # Include type hints in documentation
]

# Enable autosummary to generate automatic summaries for modules
autosummary_generate = True

# Mock imports to avoid errors during documentation generation
autodoc_mock_imports = [
    'pandas',
    'sqlalchemy',
    'fastapi',
    'redis',
    'celery',
    'psycopg2',
    'pydantic',
    'streamlit',
    'oauth',
    'streamlit-oauth',
    'jaydebeapi'
]

# Paths for templates and static files
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# HTML Output Configuration
html_theme = 'sphinx_rtd_theme'  # Read the Docs theme
html_static_path = ['_static']

# Disable module names in autodoc output
add_module_names = False

# Autodoc default options to avoid module name inclusion
autodoc_default_options = {
    'show-inheritance': True,  # Optional: if you want to show inheritance info
    'module': False,           # Disable module name inclusion
}

# Function to generate RST documentation from source directories
def run_apidoc(_):
    docs_dir = os.path.dirname(__file__)

    # Define source directories (backend and utils)
    source_dirs = [
        os.path.abspath(os.path.join(docs_dir, '../backend/')),
        os.path.abspath(os.path.join(docs_dir, '../utils/')),
    ]

    for source_dir in source_dirs:
        output_dir = os.path.join(docs_dir, 'modules')
        print(f"Generating documentation for {source_dir} into {output_dir}")

        subprocess.run([
            'sphinx-apidoc',
            '-f',             # Overwrite existing files
            '-o', output_dir, # Output directory for RST files
            source_dir,       # Source directory
            '--no-toc',       # Optional: Exclude the Table of Contents from each module
        ], check=True)

# Connect the run_apidoc function to the 'builder-inited' event
def setup(app):
    app.connect('builder-inited', run_apidoc)
