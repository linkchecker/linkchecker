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

Sphinx is used to generate .pot and .po (with sphinx-intl) files in i18n/
and man pages in man/.

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
