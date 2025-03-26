@echo off
echo ================================
echo Building Sensor GUI
echo ================================

REM Clean previous builds
rmdir /S /Q build
rmdir /S /Q dist
del sensor_gui.spec

REM Build .exe with custom icon (absolute path)
pyinstaller --onefile --noconsole --icon=%~dp0resources\sensor_icon.ico sensor_gui.py

REM Create release folder if it doesn't exist
if not exist release (
    mkdir release
)

REM Copy final .exe to release folder
copy /Y dist\sensor_gui.exe release\sensor_gui.exe

echo ----------------
echo Build complete! 
echo .EXE with shark icon is in the /release folder
pause
