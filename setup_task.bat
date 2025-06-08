@echo off
REM Resolve the absolute path of this script's directory
SET "SCRIPT_DIR=%~dp0"

REM Ensure the Python script uses the full path
SET "PYTHON_SCRIPT=%SCRIPT_DIR%deadman.py"

REM Use schtasks to register the task with full absolute path
schtasks /Create ^
  /TN "DeadManSwitch" ^
  /TR "\"%PYTHON_SCRIPT%"\" ^
  /SC ONLOGON ^
  /RL HIGHEST ^
  /F

echo DeadManSwitch task has been created to run at login using:
echo %PYTHON_SCRIPT%
pause
