@echo off
echo ========================================
echo    FRIDAY - Business Advisor AI
echo    Starting all systems...
echo ========================================

:: Start LiveKit Server
start "LiveKit" /min cmd /c "cd /d C:\claude\jarvis\friday-tony-stark-demo\livekit && livekit-server.exe --dev"
timeout /t 6 /nobreak > nul

:: Start MCP Server
start "MCP" /min cmd /c "cd /d C:\claude\jarvis\friday-tony-stark-demo && uv run friday"
timeout /t 6 /nobreak > nul

:: Start Voice Agent (single instance)
start "Agent" /min cmd /c "cd /d C:\claude\jarvis\friday-tony-stark-demo && uv run friday_voice"
timeout /t 10 /nobreak > nul

:: Keep window open to show status
echo.
echo All systems online! Friday is ready.
echo Run dispatch_friday.bat to connect.
echo.
echo Press any key to close this window...
pause > nul
