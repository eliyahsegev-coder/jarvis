@echo off
cd /d C:\claude\jarvis\friday-tony-stark-demo\livekit
lk.exe dispatch create --room my-room --agent-name "friday" --url ws://localhost:7880 --api-key devkey --api-secret secret
echo Dispatch sent! Check the browser.
timeout /t 3
