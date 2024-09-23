@echo off
set path=%path%;C:\Python27\
set PYTHONPATH=C:\Python27;C:\Python27\Lib

set PROJNR=14405
set PROJDIR=14405_AlphaESS_ModbusTCP
set PROJNAME=Alpha ESS Modbus

echo ^<head^> > .\release\DE-log%PROJNR%.html
echo ^<link rel="stylesheet" href="style.css"^> >> .\release\DE-log%PROJNR%.html
echo ^<title^>Logik - %PROJNAME% (%PROJNR%)^</title^> >> .\release\DE-log%PROJNR%.html
echo ^<style^> >> .\release\DE-log%PROJNR%.html
echo body { background: none; } >> .\release\DE-log%PROJNR%.html
echo ^</style^> >> .\release\DE-log%PROJNR%.html
echo ^<meta http-equiv="Content-Type" content="text/html;charset=UTF-8"^> >> .\release\DE-log%PROJNR%.html
echo ^</head^> >> .\release\DE-log%PROJNR%.html

@echo on
type .\README.md | C:\Python27\python -m markdown -x tables >> .\release\DE-log%PROJNR%.html

@echo off
cd ..\..
cd
@echo on

C:\Python27\python generator.pyc "%PROJDIR%" UTF-8

xcopy .\projects\%PROJDIR%\src .\projects\%PROJDIR%\release /exclude:.\projects\%PROJDIR%\src\exclude.txt

@echo Fertig.

@pause