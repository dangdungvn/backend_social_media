from rest_framework import serializers
from .models import Post, PostMedia, Like, Share
from django.contrib.auth.models import User


class UserSimpleSerializer(serializers.ModelSerializer):
    """Serializer đơn giản cho User để dùng trong PostSerializer"""

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name"]


class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = ["id", "file", "media_type", "created_at"]
        read_only_fields = ["id", "created_at"]


class PostSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)
    media = PostMediaSerializer(many=True, read_only=True)
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    share_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    uploaded_media = serializers.ListField(
        child=serializers.FileField(), write_only=True, required=False
    )
    media_types = serializers.ListField(
        child=serializers.ChoiceField(choices=PostMedia.MEDIA_TYPES),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Post
        fields = [
            "id",
            "user",
            "content",
            "created_at",
            "updated_at",
            "is_public",
            "media",
            "like_count",
            "comment_count",
            "share_count",
            "is_liked",
            "uploaded_media",
            "media_types",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_share_count(self, obj):
        return obj.shares.count()

    def get_is_liked(self, obj):
        user = self.context["request"].user
        return obj.likes.filter(user=user).exists()

    def create(self, validated_data):
        uploaded_media = validated_data.pop("uploaded_media", [])
        media_types = validated_data.pop("media_types", [])

        # Tạo bài viết
        post = Post.objects.create(user=self.context["request"].user, **validated_data)

        # Xử lý media nếu có
        if uploaded_media and media_types and len(uploaded_media) == len(media_types):
            for media_file, media_type in zip(uploaded_media, media_types):
                PostMedia.objects.create(
                    post=post, file=media_file, media_type=media_type
                )

        return post


class LikeSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ["id", "user", "post", "created_at"]
        read_only_fields = ["id", "user", "created_at"]


class ShareSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)
    original_post = PostSerializer(source="post", read_only=True)

    class Meta:
        model = Share
        fields = ["id", "user", "post", "original_post", "content", "created_at"]
        read_only_fields = ["id", "user", "created_at"]
