import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

# -- Project information -----------------------------------------------------

project = 'LinkChecker'
copyright = '2000-2014 Bastian Kleineidam'
# version = '10'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.autosummary',
    'sphinx.ext.extlinks',
    'sphinx.ext.graphviz',
    'sphinx.ext.viewcode',
    'sphinx_epytext',
    'sphinx_rtd_theme',
]

locale_dirs = ['../i18n/locales']

templates_path = ['_templates']

# -- Options for HTML output -------------------------------------------------

html_favicon = 'images/favicon.ico'

html_logo = 'images/logo128x128.png'

html_theme = 'sphinx_rtd_theme'

html_theme_options = {
    'collapse_navigation': False
}

# only use :manpage: within man pages
manpages_url = '{page}.html'

# -- Extension configuration -------------------------------------------------

autoclass_content = 'both'

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}

autodoc_member_order = 'groupwise'

autosectionlabel_prefix_document = True

extlinks = {'pypi': ('https://pypi.org/project/%s/', '')}

graphviz_output_format = 'svg'

# -- Mock --------------------------------------------------------------------

import linkcheck.logger
linkcheck.logger.blacklist.BlacklistLogger.LoggerArgs = {
    'filename': '~/.linkchecker/blacklist'}
