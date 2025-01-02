# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------

project = 'OpenETL docs'
copyright = '2025, DataOmni Solutions'
author = 'DataOmni Solutions'
release = '0.1'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

# The master toctree document.
master_doc = 'index'

# -- Options for HTML output -------------------------------------------------

html_theme = 'alabaster'  # You can replace this with 'sphinx_rtd_theme' if preferred
html_static_path = ['_static']

# -- Options for HTMLHelp output --------------------------------------------

htmlhelp_basename = 'OpenETLDocs'

# -- Options for LaTeX output -----------------------------------------------

latex_documents = [
    (master_doc, 'OpenETLDocs.tex', 'OpenETL Documentation',
     'DataOmni Solutions', 'manual'),
]

# -- Options for manual page output ----------------------------------------

man_pages = [
    (master_doc, 'openetl', 'OpenETL Documentation',
     [author], 1)
]

# -- Options for Texinfo output ---------------------------------------------

texinfo_documents = [
    (master_doc, 'OpenETL', 'OpenETL Documentation',
     author, 'OpenETL', 'Open-source ETL framework for modern data pipelines.',
     'Miscellaneous'),
]

# -- Extension configuration -------------------------------------------------

# Napoleon settings for Google and NumPy style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
master_doc = 'index'
