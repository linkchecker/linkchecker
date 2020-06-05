LinkChecker Translations
========================

Translations for the application are stored in po/.
Translations for the man pages are stored in doc/.

Application Translations
------------------------

``linkchecker $ make locale``

is equivalent to:

``linkchecker/po $ make``

Man Page Translations
---------------------

po4a is used to generate linkchecker.doc.pot, .po files and translated man pages.

``linkchecker/doc $ make po4a``
