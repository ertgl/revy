# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

import datetime

# -- Project information -----------------------------------------------------
from typing import List


project = 'Revy'
copyright = f'{datetime.date.today().year}, Ertuğrul Noyan Keremoğlu'
author = 'Ertuğrul Noyan Keremoğlu'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
    'sphinx.ext.intersphinx',
    'sphinx_copybutton',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns: List[str] = []

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}

autodoc_inherit_docstrings = False

autodoc_preserve_defaults = True

autodoc_default_options = {
    'show-inheritance': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
}

autodoc_typehints = 'both'

autodoc_typehints_format = 'short'

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'pydata_sphinx_theme'

html_theme_options = {
    'use_edit_page_button': False,
    'search_bar_text': 'Search',
    'icon_links': [
        {
            'name': 'GitHub',
            'url': 'https://github.com/ertgl/revy',
            'icon': 'fab fa-github-square',
            'type': 'fontawesome'
        },
    ],
}

html_context = {
    "github_user": "ertgl",
    "github_repo": "revy",
    "github_version": "main",
    "doc_path": "docs/source",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
