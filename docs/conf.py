import sys
import os

sys.path.append(os.path.abspath('..'))

project = 'Post-manager API'
copyright = '2024, Vivern0'
author = 'Vivern0'
release = '1.0.0'

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'nature'
html_static_path = ['_static']
