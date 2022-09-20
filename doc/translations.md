LinkChecker Translations
========================

Translations for the application are stored in po/.
Translations for the man pages are stored in doc/.

Application Translations
------------------------

Makefiles using GNU gettext utilities are provided to manage .po and .pot files.

If the strings in the application change, update the .pot and .po files:

``linkchecker/po $ rm linkchecker.pot; make``

Do make a commit at this point.

Translation progress and validity can be monitored with:

``linkchecker/po $ make check``

.mo files are not stored in the repository and are created on building,
using polib.

Man Page Translations
---------------------

Sphinx is used to generate .pot and .po (with sphinx-intl) files in i18n/
and man pages in man/.

If the application metadata has not been created, first run:
``linkchecker $ hatchling build -t sdist --hooks-only``

Create man.pot file in i18n/gettext/:

``linkchecker/doc $ make -C src gettext``

Create man.po file in i18n/locales/:

``linkchecker/doc/src $ sphinx-intl update -p ../i18n/gettext -l de``

These two steps can be performed with:

``linkchecker/doc $ make locale``

Create man pages:

``linkchecker/doc $ make man``

After updating the source files all steps need to be repeated, if translations
alone have been changed in the .po file only the last step is needed.
