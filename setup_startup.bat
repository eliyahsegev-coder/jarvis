@echo off
echo Adding Sachbak to Windows startup...
set STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
copy "%~dp0start_friday.bat" "%STARTUP%\friday.bat" /Y
echo Done! Sachbak will now start automatically with Windows.
pause
