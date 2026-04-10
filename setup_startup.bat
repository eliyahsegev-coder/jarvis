@echo off
echo Adding Friday to Windows startup...
set STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
copy "%~dp0start_friday.bat" "%STARTUP%\friday.bat" /Y
echo Done! Friday will now start automatically with Windows.
pause
