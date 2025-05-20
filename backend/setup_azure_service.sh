#!/bin/bash
# filepath: d:\Workspace\flutter\social_app\server\backend\setup_azure_service.sh
# Script để cài đặt và quản lý Django WebSocket Service trên Azure VM

# Đảm bảo chạy với quyền sudo
if [ "$(id -u)" -ne 0 ]; then
    echo "Vui lòng chạy script này với quyền sudo"
    exit 1
fi

# Thư mục hiện tại
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SERVICE_NAME="django-websocket"
SERVICE_FILE="$SERVICE_NAME.service"
PYTHON_PATH=$(which python3)
VENV_PATH=""

# Tìm đường dẫn virtualenv
if [ -d "$SCRIPT_DIR/../venv_social" ]; then
    VENV_PATH="$SCRIPT_DIR/../venv_social/bin/python"
    echo "Tìm thấy virtualenv tại: $VENV_PATH"
else
    echo "Không tìm thấy virtualenv, sử dụng Python mặc định: $PYTHON_PATH"
    VENV_PATH=$PYTHON_PATH
fi

# Thiết lập quyền thực thi cho script chạy server
chmod +x "$SCRIPT_DIR/run_azure_server.py"

# Cập nhật nội dung file service
cat > "/etc/systemd/system/$SERVICE_FILE" << EOL
[Unit]
Description=Django ASGI WebSocket Server
After=network.target redis-server.service

[Service]
User=$(whoami)
Group=$(whoami)
WorkingDirectory=$SCRIPT_DIR
ExecStart=$VENV_PATH $SCRIPT_DIR/run_azure_server.py --action start --server daphne
ExecStop=$VENV_PATH $SCRIPT_DIR/run_azure_server.py --action stop
Restart=on-failure
RestartSec=5s
Environment=DJANGO_SETTINGS_MODULE=backend.settings

[Install]
WantedBy=multi-user.target
EOL

echo "Đã tạo file service tại /etc/systemd/system/$SERVICE_FILE"

# Khởi động Redis server nếu chưa chạy
if ! systemctl is-active --quiet redis-server; then
    echo "Đang khởi động Redis server..."
    if ! systemctl start redis-server; then
        echo "Redis chưa được cài đặt. Đang cài đặt Redis..."
        apt-get update
        apt-get install -y redis-server
        systemctl enable redis-server
        systemctl start redis-server
    fi
fi

# Reload systemd để cập nhật thông tin service
systemctl daemon-reload

# Enable service để tự động khởi động khi boot
systemctl enable $SERVICE_NAME
echo "Đã enable service $SERVICE_NAME để tự khởi động khi boot"

# Menu chức năng
echo ""
echo "==== DJANGO WEBSOCKET SERVICE MANAGER ===="
echo "1. Khởi động service"
echo "2. Dừng service"
echo "3. Kiểm tra trạng thái"
echo "4. Xem log"
echo "5. Thoát"
echo "========================================"
echo ""

read -p "Chọn chức năng (1-5): " choice

case $choice in
    1)
        echo "Đang khởi động service..."
        systemctl start $SERVICE_NAME
        sleep 2
        systemctl status $SERVICE_NAME
        ;;
    2)
        echo "Đang dừng service..."
        systemctl stop $SERVICE_NAME
        ;;
    3)
        echo "Trạng thái service:"
        systemctl status $SERVICE_NAME
        ;;
    4)
        echo "Log của service:"
        journalctl -u $SERVICE_NAME -f
        ;;
    5)
        echo "Thoát."
        exit 0
        ;;
    *)
        echo "Lựa chọn không hợp lệ."
        ;;
esac

echo ""
echo "Để quản lý service, bạn có thể sử dụng các lệnh sau:"
echo "sudo systemctl start $SERVICE_NAME    # Khởi động service"
echo "sudo systemctl stop $SERVICE_NAME     # Dừng service"
echo "sudo systemctl restart $SERVICE_NAME  # Khởi động lại service"
echo "sudo systemctl status $SERVICE_NAME   # Kiểm tra trạng thái"
echo "sudo journalctl -u $SERVICE_NAME -f   # Xem log real-time"
