# Social App - Backend

Ứng dụng mạng xã hội với đầy đủ tính năng như Facebook/Twitter kết hợp với hệ thống đánh giá comment giống Stack Overflow.

## Tính năng chính

### Tính năng cốt lõi giống Facebook:

- Đăng bài viết (text, hình ảnh, video)
- News feed hiển thị bài viết từ bạn bè/người theo dõi
- Tương tác cơ bản (like, share)
- Trang cá nhân người dùng
- Kết bạn và theo dõi

### Hệ thống comment nâng cao:

- Upvote/downvote cho mỗi comment giống Stack Overflow
- Hiển thị số điểm vote cho mỗi comment
- Admin có quyền đánh dấu comment là "Đúng" hoặc "Sai"
- Sắp xếp comment theo số điểm vote
- Threading comments (trả lời comment)

### Tính năng chat:

- Chat 1-1 real-time
- Gửi file, hình ảnh
- Hiển thị trạng thái online/offline
- Thông báo tin nhắn mới
- Lưu trữ lịch sử chat

## Cài đặt

### Yêu cầu hệ thống

- Python 3.8+
- Django 4.0+
- Redis (cho WebSocket)

### Cài đặt môi trường

```bash
# Tạo và kích hoạt môi trường ảo
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
source venv/bin/activate  # Linux/Mac

# Cài đặt các gói phụ thuộc
pip install -r requirements.txt

# Tạo cơ sở dữ liệu
python manage.py migrate

# Tạo tài khoản admin
python manage.py createsuperuser

# Chạy server
python manage.py runserver
```

### Chạy Redis cho WebSocket (Tính năng chat)

Để các tính năng WebSocket hoạt động, bạn cần cài đặt và chạy Redis:

#### Windows:

Tải và cài đặt Redis từ https://github.com/tporadowski/redis/releases

```
redis-server
```

#### Linux/Mac:

```
sudo apt-get install redis-server  # Ubuntu
brew install redis  # macOS
redis-server
```

## API Endpoints

### Authentication

- `POST /auth/users/` - Đăng ký
- `POST /auth/token/login/` - Đăng nhập
- `POST /auth/token/logout/` - Đăng xuất
- `GET /auth/users/me/` - Lấy thông tin người dùng hiện tại

### Users

- `GET /api/users/` - Danh sách người dùng
- `GET /api/users/{id}/` - Chi tiết người dùng
- `GET /api/users/profiles/me/` - Profile của bạn
- `PUT /api/users/profiles/{id}/` - Cập nhật profile
- `POST /api/users/friendships/` - Gửi yêu cầu kết bạn
- `GET /api/users/friendships/pending/` - Danh sách yêu cầu kết bạn đang chờ
- `GET /api/users/friendships/friends/` - Danh sách bạn bè
- `POST /api/users/friendships/{id}/accept/` - Chấp nhận yêu cầu kết bạn
- `POST /api/users/friendships/{id}/reject/` - Từ chối yêu cầu kết bạn
- `POST /api/users/follows/` - Theo dõi người dùng
- `DELETE /api/users/follows/{id}/` - Hủy theo dõi người dùng

### Posts

- `GET /api/posts/` - Danh sách bài viết
- `GET /api/posts/?feed_type=friends` - News feed từ bạn bè
- `GET /api/posts/?feed_type=following` - News feed từ người theo dõi
- `POST /api/posts/` - Tạo bài viết mới
- `GET /api/posts/{id}/` - Chi tiết bài viết
- `PUT /api/posts/{id}/` - Cập nhật bài viết
- `DELETE /api/posts/{id}/` - Xóa bài viết
- `POST /api/posts/{id}/like/` - Like/unlike bài viết
- `POST /api/posts/{id}/share/` - Share bài viết
- `GET /api/posts/{id}/likes/` - Danh sách người đã like bài viết
- `GET /api/posts/{id}/shares/` - Danh sách người đã share bài viết

### Comments

- `GET /api/comments/?post_id={id}` - Danh sách comments của bài viết
- `GET /api/comments/?parent_id={id}` - Danh sách replies cho comment
- `POST /api/comments/` - Tạo comment mới
- `PUT /api/comments/{id}/` - Cập nhật comment
- `DELETE /api/comments/{id}/` - Xóa comment
- `POST /api/comments/{id}/vote/` - Upvote/downvote comment
- `POST /api/comments/{id}/verify/` - Admin đánh dấu comment là đúng/sai

### Chat

- `GET /api/chat/rooms/` - Danh sách phòng chat
- `POST /api/chat/rooms/get_or_create/` - Lấy hoặc tạo phòng chat với người dùng khác
- `GET /api/chat/messages/?room_id={id}` - Lấy tin nhắn trong phòng chat
- `POST /api/chat/messages/` - Gửi tin nhắn mới
- `POST /api/chat/messages/mark_as_read/` - Đánh dấu tin nhắn là đã đọc
- `GET /api/chat/status/` - Danh sách trạng thái online/offline của người dùng
- `POST /api/chat/status/set_status/` - Cập nhật trạng thái online/offline

### WebSocket

- `ws://domain/ws/chat/{room_id}/` - WebSocket cho chat real-time

## Đóng góp

Vui lòng tạo issue hoặc pull request nếu bạn muốn đóng góp cho dự án.
