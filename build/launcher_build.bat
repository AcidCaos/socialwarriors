@echo off
set NAME=social-warriors_0.02a

REM remember to activate the venv first (Scripts\activate)

:main
call :pyInstaller
echo [+] Building Done!
REM call :clean
REM echo [+] Cleaning Done!
pause>NUL
exit

:pyInstaller
echo [+] Starting pyInstaller...
pyinstaller --onefile ^
 --console ^
 --add-data "..\..\assets;assets" ^
 --add-data "..\..\stub;stub" ^
 --add-data "..\..\templates;templates" ^
 --add-data "..\..\villages;villages" ^
 --add-data "..\..\config;config" ^
 --paths ..\. ^
 --workpath .\work ^
 --distpath .\dist ^
 --specpath .\bundle ^
 --noconfirm ^
 --icon=..\icon.ico ^
 --noupx ^
 --name %NAME% ..\server.py
REM --debug bootloader
echo [+] pyInstaller Done.
EXIT /B 0

:clean
echo [+] Cleaning...
rm .\work\*
rm .\work\.*
rmdir .\work
rm .\dist\*
rm .\dist\.*
rmdir .\dist
rm .\bundle\*
rm .\bundle\.*
rmdir .\bundle
echo [+] Cleaning Done.
EXIT /B 0