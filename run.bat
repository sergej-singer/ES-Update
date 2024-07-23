@echo off 
rem You can change your default EuroScope path here
set defaultConfigPath="D:\Documents\EuroScope"

echo EuroScope Path (leave empty for default: %defaultConfigPath%):
set /p a=
if [%a%]==[] (python %~dp0\es-update\__main__.py %defaultConfigPath%) else (python %~dp0\es-update\__main__.py %a%)
pause