import os
import django

# Cài đặt môi trường Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from django.contrib.auth.models import User
from users.models import Profile


def create_missing_profiles():
    users_without_profile = []

    for user in User.objects.all():
        try:
            # Thử truy cập profile để xem nó có tồn tại không
            profile = user.profile
            print(f"User {user.username} đã có profile.")
        except User.profile.RelatedObjectDoesNotExist:
            # Nếu profile không tồn tại, sử dụng get_or_create để tránh race condition
            profile, created = Profile.objects.get_or_create(user=user)
            if created:
                users_without_profile.append(user.username)
                print(f"Đã tạo profile cho user {user.username}.")

    print("\nKết quả:")
    print(f"Đã tạo {len(users_without_profile)} profile mới.")
    if users_without_profile:
        print(
            "Danh sách người dùng được tạo profile mới:",
            ", ".join(users_without_profile),
        )
    else:
        print("Không có user nào cần tạo profile mới.")


if __name__ == "__main__":
    print("Bắt đầu tạo profile cho các user hiện có...")
    create_missing_profiles()
    print("Hoàn tất!")
