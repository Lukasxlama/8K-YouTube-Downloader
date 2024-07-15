@echo off
setlocal

set "script_dir=%~dp0"
set "ps_script=%script_dir%starting.ps1"

powershell -ExecutionPolicy Bypass -File "%ps_script%"

endlocal
