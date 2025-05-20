@echo off
REM Script để chạy Uvicorn thay vì Daphne
REM Uvicorn có thể dễ debug hơn cho ASGI application

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

echo Khởi động ASGI Server với Uvicorn (với debug)...
cd /d D:\Workspace\flutter\social_app\server\backend
D:\Workspace\flutter\social_app\server\venv_social\Scripts\python.exe run_uvicorn.py

echo Server đã dừng.
pause
