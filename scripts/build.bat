:: Expected to be run via a 'scripts\build.bat' command from project root directory
:: Create .exe and literal zipped distributable folder
@echo off
:: Return error code of 0 as precaution, so initial failure detection is not mistakenly triggered
cd .
:: Activate venv, expected to be located in project root directory
call venv\Scripts\activate.bat
:: Detect if failure happened while running the above
if ERRORLEVEL 1 (
    echo.
    echo FAILURE DETECTED
    echo Failed to execute activate.bat
    goto ERROR
)
:: Make sure have pyinstaller
call python -m pip install pyinstaller
:: Detect if failure happened while running the above
if ERRORLEVEL 1 (
    echo.
    echo FAILURE DETECTED
    echo Failed to install pyinstaller
    goto ERROR
)

:: Run pyinstaller to produce the .exe, specifying 'code\run.py' as where pyinstaller should look
:: Output to a bin\bin folder in parent directpry (the CWD atm)
:: Remove temporary files created while generating the .exe
:: Create a single output folder
:: Specify .exe folder and application name
:: Look in \code for run.py
call pyinstaller --distpath ./bin\./bin ^
    --noconfirm ^
    --clean ^
    --onedir ^
    --console ^
    --debug=bootloader ^
    --name RemoteControl ^
    --add-data="res\remote_control.ico;." ^
    code\run.py
:: Detect if failure happened while running the above
if ERRORLEVEL 1 (
    echo.
    echo FAILURE DETECTED
    echo pyinstaller command could not be completed
    goto ERROR
)
:: Move all of pyinstaller's extra stuff into bin
move build bin
:: Detect if failure happened while running the above
if ERRORLEVEL 1 (
    echo.
    echo FAILURE DETECTED
    echo Could not move build directory into bin directory
    goto ERROR
)
del RemoteControl.spec
:: Detect if failure happened while running the above
if ERRORLEVEL 1 (
    echo.
    echo FAILURE DETECTED
    echo Could not delete RemoteControl.spec
    goto ERROR
)

:: Generate and encrypt a version number
call python scripts\helpers\make_version.py
:: Detect if failure happened while running the above
if ERRORLEVEL 1 (
    echo.
    echo FAILURE DETECTED
    echo Failed to execute make_version.py
    goto ERROR
)

:: Create temporary folder that will eventually be turned into a .zip for distribution
call mkdir temp_zip
:: Detect if failure happened while running the above
if ERRORLEVEL 1 (
    echo.
    echo FAILURE DETECTED
    echo Coulde not create temp_zip directory
    goto ERROR
)

:: Copy the .exe output folder from pyinstaller and the run.bat that finds the .exe into the temporary folder
:: Move generated .dat file containing encrypted version value to the folder to be zipped so GUI can find easily when run via .exe
call xcopy bin\bin temp_zip /s/h/e/k/f
:: Detect if failure happened while running the above
if ERRORLEVEL 1 (
    echo.
    echo FAILURE DETECTED
    echo Could not copy bin/bin directory into temp_zip directory
    goto ERROR
)
call xcopy res\run.bat temp_zip
:: Detect if failure happened while running the above
if ERRORLEVEL 1 (
    echo.
    echo FAILURE DETECTED
    echo Coule dnot copy run.bat into temp_zip directory
    goto ERROR
)
call move version.dat temp_zip\RemoteControl
:: Detect if failure happened while running the above
if ERRORLEVEL 1 (
    echo.
    echo FAILURE DETECTED
    echo Could not move version.dat into temp_zip\RemoteControl directory
    goto ERROR
)

:: Run small script to crate a zipped folder (named RemoteControl - see zip.py), contatining the contents of the temporary folder
call python code\zip.py
:: Detect if failure happened while running the above
if ERRORLEVEL 1 (
    echo.
    echo FAILURE DETECTED
    echo Failed to execute zip.py
    goto ERROR
)
:: Delete the temporary folder
rmdir /s /q temp_zip
:: Detect if failure happened while running the above
if ERRORLEVEL 1 (
    echo.
    echo FAILURE DETECTED
    echo Could not delete temp_zip directory
    goto ERROR
)

goto Finished

:: Print error code, /b exits only to CMD (not out)
:ERROR
echo Error Code: %ERRORLEVEL%
exit /b %ERRORLEVEL%

:Finished