import os
import django
import random
from datetime import datetime, timedelta

# Cài đặt môi trường Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from users.models import Profile, Friendship, Follow
from posts.models import Post, Like, Share
from comments.models import Comment, CommentVote
from chat.models import Room, Message, UserStatus


# Tạo người dùng mẫu
def create_users():
    usernames = ["trung", "linh", "minh", "huong", "tuan", "hoa", "nam", "thanh"]
    users = []

    print("Tạo người dùng...")

    for username in usernames:
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username, email=f"{username}@example.com", password="123456"
            )
            user.first_name = username.capitalize()
            user.last_name = "Nguyễn"
            user.save()

            # Cập nhật profile
            profile = user.profile
            profile.bio = f"Đây là trang cá nhân của {username.capitalize()}"
            profile.location = "Việt Nam"
            profile.birth_date = timezone.now().date() - timedelta(
                days=random.randint(8000, 12000)
            )
            profile.save()

            users.append(user)
            print(f"  Đã tạo người dùng: {username}")

    return users if users else User.objects.all()


# Tạo mối quan hệ bạn bè và theo dõi
def create_relationships(users):
    print("Tạo mối quan hệ bạn bè và theo dõi...")

    for i, user1 in enumerate(users):
        for j, user2 in enumerate(users):
            if i != j:  # Tạo bạn bè (khoảng 50% người dùng)
                if (
                    random.random() > 0.5
                    and not Friendship.objects.filter(
                        (
                            django.db.models.Q(sender=user1)
                            & django.db.models.Q(receiver=user2)
                        )
                        | (
                            django.db.models.Q(sender=user2)
                            & django.db.models.Q(receiver=user1)
                        )
                    ).exists()
                ):
                    friendship = Friendship.objects.create(
                        sender=user1, receiver=user2, status="accepted"
                    )
                    print(f"  {user1.username} và {user2.username} là bạn bè")

                # Tạo người theo dõi (khoảng 70% người dùng)
                if (
                    random.random() > 0.3
                    and not Follow.objects.filter(
                        follower=user1, followed=user2
                    ).exists()
                ):
                    follow = Follow.objects.create(follower=user1, followed=user2)
                    print(f"  {user1.username} theo dõi {user2.username}")


# Tạo bài viết mẫu
def create_posts(users):
    print("Tạo bài viết...")

    posts = []
    contents = [
        "Hôm nay trời đẹp quá! 🌞",
        "Vừa đọc xong một cuốn sách hay! Các bạn có đề xuất gì không?",
        "Món ăn hôm nay rất ngon! 🍜",
        "Đi làm mệt quá, về đến nhà là muốn nghỉ ngơi!",
        "Cuối tuần có ai rảnh không? Đi cà phê không?",
        "Vừa xem một bộ phim hay! Mọi người đã xem 'Không thể không xem' chưa?",
        "Ngày hôm nay thật tuyệt vời! 😊",
        "Đang học một kỹ năng mới, rất thú vị!",
        "Mình vừa thử một nhà hàng mới, đồ ăn khá ngon! 🍕",
        "Ai có kinh nghiệm về lập trình Python không? Mình đang bị stuck!",
    ]

    for user in users:
        for _ in range(random.randint(1, 5)):  # Mỗi người dùng tạo 1-5 bài viết
            post = Post.objects.create(
                user=user,
                content=random.choice(contents),
                is_public=random.random() > 0.1,  # 90% bài viết là công khai
            )
            posts.append(post)
            print(f"  {user.username} đã đăng một bài viết")

    return posts


# Tạo like và share
def create_interactions(users, posts):
    print("Tạo like và share...")

    for user in users:
        # Mỗi người dùng like khoảng 40% bài viết
        for post in random.sample(posts, int(len(posts) * 0.4)):
            if not Like.objects.filter(user=user, post=post).exists():
                Like.objects.create(user=user, post=post)
                print(f"  {user.username} đã like bài viết của {post.user.username}")

        # Mỗi người dùng share khoảng 10% bài viết
        for post in random.sample(posts, int(len(posts) * 0.1)):
            if not Share.objects.filter(user=user, post=post).exists():
                Share.objects.create(
                    user=user,
                    post=post,
                    content=f"Chia sẻ bài viết của {post.user.username}",
                )
                print(f"  {user.username} đã share bài viết của {post.user.username}")


# Tạo comment và vote
def create_comments(users, posts):
    print("Tạo comments và votes...")

    comments = []
    contents = [
        "Rất hay!",
        "Mình đồng ý với bạn.",
        "Thú vị đấy!",
        "Mình không đồng ý lắm, nhưng tôn trọng ý kiến của bạn.",
        "Làm tốt lắm!",
        "Cảm ơn bạn đã chia sẻ!",
        "Thông tin rất hữu ích.",
        "Mình có thắc mắc một chút.",
        "Chúc bạn một ngày tốt lành!",
        "Mình sẽ thử xem!",
    ]

    for post in posts:
        # Mỗi bài viết có 0-8 comment
        for _ in range(random.randint(0, 8)):
            user = random.choice(users)
            if user != post.user:  # Không comment vào bài viết của chính mình
                comment = Comment.objects.create(
                    user=user, post=post, content=random.choice(contents)
                )
                comments.append(comment)
                print(
                    f"  {user.username} đã comment vào bài viết của {post.user.username}"
                )

    # Tạo reply cho khoảng 30% comment
    for comment in random.sample(comments, int(len(comments) * 0.3)):
        user = random.choice(users)
        if user != comment.user:  # Không reply comment của chính mình
            reply = Comment.objects.create(
                user=user,
                post=comment.post,
                parent=comment,
                content=f"Trả lời {comment.user.username}: " + random.choice(contents),
            )
            comments.append(reply)
            print(f"  {user.username} đã trả lời comment của {comment.user.username}")

    # Tạo vote cho comment
    for comment in comments:
        # Mỗi comment được vote bởi 0-5 người
        for _ in range(random.randint(0, 5)):
            user = random.choice(users)
            if (
                user != comment.user
                and not CommentVote.objects.filter(user=user, comment=comment).exists()
            ):
                vote_type = (
                    "upvote" if random.random() > 0.3 else "downvote"
                )  # 70% là upvote
                CommentVote.objects.create(
                    user=user, comment=comment, vote_type=vote_type
                )
                print(
                    f"  {user.username} đã {vote_type} comment của {comment.user.username}"
                )


# Tạo phòng chat và tin nhắn
def create_chats(users):
    print("Tạo phòng chat và tin nhắn...")

    messages = [
        "Chào bạn!",
        "Bạn khỏe không?",
        "Hôm nay bạn làm gì vậy?",
        "Mình có một câu hỏi này...",
        "Cảm ơn bạn rất nhiều!",
        "Hẹn gặp lại bạn!",
        "Có gì mới không?",
        "Mình đang ở nhà.",
        "Bạn có rảnh không?",
        "Tối nay đi ăn không?",
    ]

    # Tạo phòng chat cho khoảng 50% cặp người dùng
    for i, user1 in enumerate(users):
        for j, user2 in enumerate(users):
            if (
                i < j and random.random() > 0.5
            ):  # Chỉ tạo một phòng cho mỗi cặp người dùng
                room = Room.objects.create()
                room.participants.add(user1, user2)

                # Tạo tin nhắn trong phòng chat
                num_messages = random.randint(3, 15)
                for _ in range(num_messages):
                    sender = random.choice([user1, user2])
                    Message.objects.create(
                        room=room,
                        sender=sender,
                        content=random.choice(messages),
                        is_read=random.random() > 0.3,  # 70% tin nhắn đã đọc
                    )

                print(
                    f"  Đã tạo phòng chat giữa {user1.username} và {user2.username} với {num_messages} tin nhắn"
                )


# Tạo trạng thái online cho người dùng
def create_user_statuses(users):
    print("Tạo trạng thái online cho người dùng...")

    for user in users:
        is_online = random.random() > 0.7  # 30% người dùng đang online
        UserStatus.objects.update_or_create(
            user=user,
            defaults={
                "is_online": is_online,
                "last_activity": (
                    timezone.now()
                    if is_online
                    else timezone.now() - timedelta(minutes=random.randint(10, 1000))
                ),
            },
        )
        status = "online" if is_online else "offline"
        print(f"  {user.username} đang {status}")


# Chạy tất cả các hàm
def run():
    print("Bắt đầu tạo dữ liệu mẫu...")

    users = create_users()
    create_relationships(users)
    posts = create_posts(users)
    create_interactions(users, posts)
    create_comments(users, posts)
    create_chats(users)
    create_user_statuses(users)

    print("Đã tạo xong dữ liệu mẫu!")


if __name__ == "__main__":
    run()
