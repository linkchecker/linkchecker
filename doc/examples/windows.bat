@echo off
:: Do replace the for loop with setting SCRIPTSDIR to the literal path
for /f "delims=" %%i in ('python -c "import site; print(site.getusersitepackages().replace('site-packages', 'Scripts'))"') do set SCRIPTSDIR=%%i
python %SCRIPTSDIR%\linkchecker %*
