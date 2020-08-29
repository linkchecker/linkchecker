import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

# -- Project information -----------------------------------------------------

from datetime import date
import linkcheck.configuration

project = 'LinkChecker'
copyright = linkcheck.configuration.Copyright.split("Copyright (C) ")[1]
version = str(date.today())
release = version

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

today_fmt = '%B %d, %Y'

# -- Options for HTML output -------------------------------------------------

html_favicon = 'images/favicon.ico'

html_logo = 'images/logo128x128.png'

html_theme = 'sphinx_rtd_theme'

html_theme_options = {
    'collapse_navigation': False
}

# only use :manpage: within man pages
manpages_url = '{page}.html'

# -- Options for man output -------------------------------------------------

man_pages = [
    (
     'man/linkchecker', 'linkchecker',
     'Kommandozeilenprogramm zum Prüfen von HTML Dokumenten und '
     'Webseiten auf ungültige Verknüpfungen'
     if tags.has('de') else
     'command line client to check HTML documents and websites for broken links',
     ['Bastian Kleineidam <bastian.kleineidam@web.de>'], 1),
    (
     'man/linkcheckerrc', 'linkcheckerrc',
     'Konfigurationsdatei für LinkChecker'
     if tags.has('de') else
     'configuration file for LinkChecker',
     ['Bastian Kleineidam <bastian.kleineidam@web.de>'], 5),
]

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
linkcheck.logger.failures.FailuresLogger.LoggerArgs = {
    'filename': '~/.linkchecker/failures'}
