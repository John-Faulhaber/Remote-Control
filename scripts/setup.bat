:: Expected to be run via a 'scripts\setup.bat' command from project root directory
:: Create venv, activate venv, install dependencies
@echo off
:: Try to create venv
call python -m virtualenv venv

:: If virtualenv module not found...
if %ERRORLEVEL% neq 0 goto ProcessError

:: Activate venv
call venv\Scripts\activate.bat
:: Detect if failure happened while running the above
if ERRORLEVEL 1 (
    echo.
    echo FAILURE DETECTED
    echo Failed to activate virtual environment [activate.bat]
    goto ERROR
)
:: Read in requirements for installation. Currently in the activated venv, so they will go there
call python -m pip install -r requirements.txt
:: Detect if failure happened while running the above
if ERRORLEVEL 1 (
    echo.
    echo FAILURE DETECTED
    echo Could not install requirements from requirements.txt
    goto ERROR
)

goto Finished

:: ...try with just venv instead
:ProcessError
call python -m venv venv
if ERRORLEVEL 1 (
    echo.
    echo FAILURE DETECTED
    echo Failed to create virtual environment [venv]
    goto ERROR
)
:: Activate venv
call venv\Scripts\activate.bat
:: Detect if failure happened while running the above
if ERRORLEVEL 1 (
    echo.
    echo FAILURE DETECTED
    echo Failed to activate virtual environment [activate.bat]
    goto ERROR
)
:: Read in requirements for installation. Currently in the activated venv, so they will go there
call python -m pip install -r requirements.txt
:: Detect if failure happened while running the above
if ERRORLEVEL 1 (
    echo.
    echo FAILURE DETECTED
    echo Could not install requirements from requirements.txt
    goto ERROR
)
goto Finished

:: Print error code, /b exits only to CMD (not out)
:ERROR
echo Error Code: %ERRORLEVEL%
exit /b %ERRORLEVEL%

:Finished