"""
Script để khởi động server ASGI với WebSocket.
Đảm bảo Redis server đã chạy trước khi thực thi script này.
"""

import sys
import subprocess
import time
import os
import webbrowser
from pathlib import Path

# Đường dẫn thư mục hiện tại
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def check_redis():
    """Kiểm tra xem Redis có đang chạy không."""
    try:
        import redis

        client = redis.Redis(host="127.0.0.1", port=6379)
        return client.ping()
    except Exception as e:
        print(f"Lỗi khi kết nối Redis: {e}")
        return False


def collect_static():
    """Thu thập static files."""
    try:
        print("Thu thập static files...")
        subprocess.run(
            ["python", "manage.py", "collectstatic", "--noinput"], cwd=CURRENT_DIR
        )
        print("Đã thu thập static files thành công.")
        return True
    except Exception as e:
        print(f"Lỗi khi thu thập static files: {e}")
        return False


def start_daphne():
    """Khởi động server Daphne."""
    try:
        print("Đang khởi động server Daphne...")
        # Khởi động Daphne trong một tiến trình con
        process = subprocess.Popen(
            ["daphne", "-b", "0.0.0.0", "-p", "8000", "backend.asgi:application"],
            cwd=CURRENT_DIR,
        )
        return process
    except Exception as e:
        print(f"Lỗi khi khởi động Daphne: {e}")
        return None


def start_uvicorn():
    """Khởi động server Uvicorn."""
    try:
        print("Đang khởi động server Uvicorn...")
        # Khởi động Uvicorn trong một tiến trình con
        process = subprocess.Popen(
            [
                "uvicorn",
                "backend.asgi:application",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
            ],
            cwd=CURRENT_DIR,
        )
        return process
    except Exception as e:
        print(f"Lỗi khi khởi động Uvicorn: {e}")
        return None


def main():
    """Hàm chính để chạy server."""
    # Thu thập static files trước
    collect_static()

    print("Đang kiểm tra Redis...")
    if not check_redis():
        print("\nCảnh báo: Redis không hoạt động!")
        print(
            "1. Hãy cài đặt Redis: Tải từ https://github.com/tporadowski/redis/releases (cho Windows)"
        )
        print("2. Khởi động Redis server: Chạy redis-server.exe")
        print("WebSocket sẽ không hoạt động đúng nếu Redis không chạy!")

        choice = input("\nBạn vẫn muốn tiếp tục không? (y/n): ")
        if choice.lower() != "y":
            print("Đang thoát...")
            return

    server_type = input("\nChọn ASGI server (1=Daphne, 2=Uvicorn): ")

    # Khởi động server
    server_process = None
    if server_type == "1":
        server_process = start_daphne()
    else:
        server_process = start_uvicorn()

    if not server_process:
        print("Không thể khởi động server. Đang thoát...")
        return

    print("\nServer đã khởi động tại http://127.0.0.1:8000/")
    print("WebSocket có thể truy cập tại ws://127.0.0.1:8000/ws/chat/<room_name>/")

    # Hiển thị đường dẫn tới trang test WebSocket
    test_page_path = os.path.join(CURRENT_DIR, "websocket_test.html")
    if os.path.exists(test_page_path):
        print(f"\nTrang test WebSocket: file://{test_page_path}")
        open_browser = input(
            "Bạn có muốn mở trang test trong trình duyệt không? (y/n): "
        )
        if open_browser.lower() == "y":
            webbrowser.open("file://" + test_page_path)

    try:
        print("\nNhấn Ctrl+C để dừng server...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nĐang dừng server...")
        server_process.terminate()
        server_process.wait()
        print("Server đã dừng.")


if __name__ == "__main__":
    main()
