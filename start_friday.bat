@echo off
echo ========================================
echo    FRIDAY - Business Advisor AI
echo    Starting all systems...
echo ========================================

:: Start LiveKit Server
start "LiveKit" /min cmd /c "cd /d C:\claude\jarvis\friday-tony-stark-demo\livekit && livekit-server.exe --dev"
timeout /t 5 /nobreak > nul

:: Start MCP Server
start "MCP" /min cmd /c "cd /d C:\claude\jarvis\friday-tony-stark-demo && uv run friday"
timeout /t 5 /nobreak > nul

:: Start Voice Agent
start "Agent" /min cmd /c "cd /d C:\claude\jarvis\friday-tony-stark-demo && uv run friday_voice"
timeout /t 6 /nobreak > nul

:: Wait longer for agent to fully register
timeout /t 8 /nobreak > nul

:: Auto-dispatch
cd /d C:\claude\jarvis\friday-tony-stark-demo\livekit
lk.exe dispatch create --room my-room --agent-name "friday" --url ws://localhost:7880 --api-key devkey --api-secret secret

:: Keep window open to show status
echo.
echo All systems online! Friday is ready.
echo.
echo Press any key to close this window...
pause > nul
