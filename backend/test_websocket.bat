@echo off
REM Script để chạy test WebSocket với Redis

echo Kiểm tra Redis server...
tasklist /fi "ImageName eq redis-server.exe" | find "redis-server.exe" > nul
if errorlevel 1 (
    echo Redis Server chưa chạy. Đang khởi động Redis...
    start "" "C:\Program Files\Redis\redis-server.exe"
    timeout /t 2 > nul
) else (
    echo Redis Server đã đang chạy.
)

echo Mở trang test WebSocket trong trình duyệt...
start "" "D:\Workspace\flutter\social_app\server\backend\websocket_test.html"

echo.
echo Đã mở trang test WebSocket.
echo Hãy đảm bảo ASGI server đã được chạy (start_websocket_server.bat).
pause
