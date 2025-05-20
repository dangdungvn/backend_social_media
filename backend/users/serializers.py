from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Friendship, Follow


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined"]


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)

    class Meta:
        model = Profile
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "location",
            "birth_date",
            "avatar",
            "cover_photo",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def update(self, instance, validated_data):
        # Cập nhật thông tin người dùng nếu có
        user_data = validated_data.pop("user", {})
        user = instance.user

        for attr, value in user_data.items():
            setattr(user, attr, value)

        user.save()

        # Cập nhật profile
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance


class FriendshipSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source="sender.username", read_only=True)
    receiver_username = serializers.CharField(
        source="receiver.username", read_only=True
    )

    class Meta:
        model = Friendship
        fields = [
            "id",
            "sender",
            "sender_username",
            "receiver",
            "receiver_username",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class FollowSerializer(serializers.ModelSerializer):
    follower_username = serializers.CharField(
        source="follower.username", read_only=True
    )
    followed_username = serializers.CharField(
        source="followed.username", read_only=True
    )

    class Meta:
        model = Follow
        fields = [
            "id",
            "follower",
            "follower_username",
            "followed",
            "followed_username",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
