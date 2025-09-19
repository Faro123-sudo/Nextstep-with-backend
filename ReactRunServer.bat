@echo off
cd Nextstep-frontend\nextstep-navigator
start npm run dev
timeout /t 3
start http://localhost:5173