@echo off
pyinstaller --onefile --noconsole sensor_gui.py
mkdir release
copy dist\sensor_gui.exe release\sensor_gui.exe
echo Build complete. .EXE copied to /release
pause
