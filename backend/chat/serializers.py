from rest_framework import serializers
from .models import Room, Message, MessageMedia, UserStatus
from django.contrib.auth.models import User


class UserStatusSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = UserStatus
        fields = ["id", "user", "username", "is_online", "last_activity"]
        read_only_fields = ["id", "user", "last_activity"]


class UserChatSerializer(serializers.ModelSerializer):
    is_online = serializers.SerializerMethodField()
    last_activity = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "is_online",
            "last_activity",
        ]

    def get_is_online(self, obj):
        try:
            return obj.chat_status.is_online
        except UserStatus.DoesNotExist:
            return False

    def get_last_activity(self, obj):
        try:
            return obj.chat_status.last_activity
        except UserStatus.DoesNotExist:
            return None


class MessageMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageMedia
        fields = ["id", "file", "media_type", "created_at"]
        read_only_fields = ["id", "created_at"]


class MessageSerializer(serializers.ModelSerializer):
    sender = UserChatSerializer(read_only=True)
    media = MessageMediaSerializer(many=True, read_only=True)
    uploaded_media = serializers.ListField(
        child=serializers.FileField(), write_only=True, required=False
    )
    media_types = serializers.ListField(
        child=serializers.ChoiceField(choices=MessageMedia.MEDIA_TYPES),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Message
        fields = [
            "id",
            "room",
            "sender",
            "content",
            "created_at",
            "is_read",
            "media",
            "uploaded_media",
            "media_types",
        ]
        read_only_fields = ["id", "sender", "created_at"]

    def create(self, validated_data):
        uploaded_media = validated_data.pop("uploaded_media", [])
        media_types = validated_data.pop("media_types", [])

        # Tạo tin nhắn
        message = Message.objects.create(
            sender=self.context["request"].user, **validated_data
        )

        # Xử lý media nếu có
        if uploaded_media and media_types and len(uploaded_media) == len(media_types):
            for media_file, media_type in zip(uploaded_media, media_types):
                MessageMedia.objects.create(
                    message=message, file=media_file, media_type=media_type
                )

        return message


class RoomSerializer(serializers.ModelSerializer):
    participants = UserChatSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = [
            "id",
            "participants",
            "created_at",
            "updated_at",
            "last_message",
            "unread_count",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_last_message(self, obj):
        last_message = obj.messages.order_by("-created_at").first()
        if last_message:
            return MessageSerializer(last_message, context=self.context).data
        return None

    def get_unread_count(self, obj):
        user = self.context["request"].user
        return obj.messages.filter(is_read=False).exclude(sender=user).count()
