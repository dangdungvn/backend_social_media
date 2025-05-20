from rest_framework import serializers
from .models import Comment, CommentVote
from django.contrib.auth.models import User


class UserSimpleSerializer(serializers.ModelSerializer):
    """Serializer đơn giản cho User để dùng trong CommentSerializer"""

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name"]


class RecursiveField(serializers.Serializer):
    """Trường đệ quy để hiển thị comment con (replies)"""

    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CommentVoteSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)

    class Meta:
        model = CommentVote
        fields = ["id", "user", "comment", "vote_type", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "created_at"]


class CommentSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)
    replies = RecursiveField(many=True, read_only=True)
    vote_score = serializers.IntegerField(read_only=True)
    user_vote = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "post",
            "parent",
            "content",
            "created_at",
            "updated_at",
            "verification_status",
            "replies",
            "vote_score",
            "user_vote",
        ]
        read_only_fields = [
            "id",
            "user",
            "created_at",
            "updated_at",
            "verification_status",
        ]

    def get_user_vote(self, obj):
        """Trả về loại vote của người dùng hiện tại cho comment này"""
        user = self.context["request"].user
        if not user.is_authenticated:
            return None

        try:
            vote = obj.votes.get(user=user)
            return vote.vote_type
        except CommentVote.DoesNotExist:
            return None

    def create(self, validated_data):
        # Gán người dùng hiện tại cho comment
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
