# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "P3 Analysis Library"
copyright = (
    " Intel Corporation. Intel, the Intel logo, and other Intel marks are "
    + "trademarks of Intel Corporation or its subsidiaries. Other names and "
    + "brands may be claimed as the property of others."
)
author = "Intel Corporation"
version = ""
release = ""

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.mathjax',
    'sphinx_gallery.gen_gallery',
    'sphinx.ext.intersphinx',
]

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
html_title = "P3 Analysis Library"

sphinx_gallery_conf = {
     'examples_dirs': ['../../examples','../../case-studies'],
     'gallery_dirs': ['examples','case-studies'],
     'run_stale_examples': True,
     'filename_pattern': '/',
}

intersphinx_mapping = {
    "matplotlib": ('https://matplotlib.org/stable/', None),
    "pandas": ('https://pandas.pydata.org/pandas-docs/stable/', None),
}
