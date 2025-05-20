@echo off
REM Script để khởi động Redis Server và ASGI Server

echo Kiểm tra Redis server...
tasklist /fi "ImageName eq redis-server.exe" | find "redis-server.exe" > nul
if errorlevel 1 (
    echo Redis Server chưa chạy. Đang khởi động Redis...
    start "" "C:\Program Files\Redis\redis-server.exe"
    timeout /t 2 > nul
) else (
    echo Redis Server đã đang chạy.
)

echo Thu thập static files...
D:\Workspace\flutter\social_app\server\venv_social\Scripts\python.exe D:\Workspace\flutter\social_app\server\backend\manage.py collectstatic --noinput

echo Khởi động ASGI Server với Daphne...
cd /d D:\Workspace\flutter\social_app\server\backend
D:\Workspace\flutter\social_app\server\venv_social\Scripts\daphne.exe -b 0.0.0.0 -p 8000 backend.asgi:application

echo Server đã dừng.
pause
