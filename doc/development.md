Developing LinkChecker
======================

The following steps describe how to compile LinkChecker from source
on various platforms.

This is a technical document, if you are looking for ways to
participate in the community, you should rather look into
[contributing](contributing).

Requirements
------------
On Mac OS X systems, using MacPorts, Fink or homebrew for software
installation is recommended.

- Install Python >= 2.7.2 from http://www.python.org/

- *On Windows only*, install the Windows SDK
  http://msdn.microsoft.com/de-de/windows/bb980924

- *On Windows only*, download and install the Microsoft
  Visual C++ 2008 runtime from
  http://www.microsoft.com/downloads/details.aspx?FamilyID=9b2da534-3e03-4391-8a4d-074b9f2bc1bf&displaylang=en

- *Optional, used for Virus checking:*
  ClamAv for Unix from http://www.clamav.net/lang/en/download/
  or for Windows from http://www.sosdg.org/clamav-win32/

- *Optional, for displaying country codes:*
  Pygeoip from http://code.google.com/p/pygeoip/


Setup for Unix/Linux
--------------------
Execute ``make localbuild`` to compile a local version and execute
``./linkchecker``.
Execute ``make test`` to run the unittest suite.
Execute ``make dist`` to build a distributable source package.


Setup for Mac OS X
------------------
Execute ``make localbuild`` to compile a local version and execute
``./linkchecker``.
Execute ``make test`` to run the unittest suite.
Execute ``make app`` to build a distributable source package.


Setup for Windows
-----------------
Execute ``windows\build.bat`` to build a local version.
Execute ``windows\test.bat`` to run the unittest suite.
Execute ``windows\dist.bat`` to build a binary installer.


Release process
---------------

1. check whether updated translations need committing
   (`make locale; make -C doc locale; make -C doc man`)

2. bump AppVersion in `setup.py`, edit `changelog.txt`, and if applicable the
   copyright date in `linkcheck/configuration/__init__.py`

3. confirm tests have passed

4. submit a pull request

5. create a new git clone

6. build Python distribution files (`setup.py sdist bdist_wheel`)

7. check distribution files (`twine check dist/*`) and upload to PyPI (`twine upload dist/*`)

8. create release (vX.Y.Z) on GitHub (GitHub creates the .tar.gz and .zip archives)

9. increment AppVersion to vX.Y.Z+1.dev0
