from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Comment, CommentVote
from .serializers import CommentSerializer, CommentVoteSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission để chỉ cho phép chủ sở hữu của một đối tượng sửa đổi nó.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner
        return obj.user == request.user


class IsAdminForVerification(permissions.BasePermission):
    """
    Custom permission để chỉ cho phép admin đánh dấu comment là đúng/sai.
    """

    def has_permission(self, request, view):
        # Only allow admin to use verify action
        if view.action == "verify":
            return request.user.is_staff
        return True


class CommentViewSet(viewsets.ModelViewSet):
    """API endpoint cho quản lý comments"""

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsOwnerOrReadOnly,
        IsAdminForVerification,
    ]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at", "vote_score"]
    ordering = ["-vote_score", "-created_at"]

    def get_queryset(self):
        """
        Tùy chỉnh queryset dựa trên post_id hoặc parent_id
        """
        queryset = super().get_queryset()

        # Nếu có post_id, lọc theo post
        post_id = self.request.query_params.get("post_id", None)
        if post_id:
            queryset = queryset.filter(post_id=post_id)

        # Nếu có parent_id, lọc các replies của comment đó
        parent_id = self.request.query_params.get("parent_id", None)
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        elif post_id and parent_id is None:
            # Nếu chỉ có post_id và không có parent_id, chỉ lấy comment gốc (không phải replies)
            queryset = queryset.filter(parent__isnull=True)

        # Sắp xếp theo score nếu được yêu cầu
        sort_by = self.request.query_params.get("sort_by", None)
        if sort_by == "score":
            queryset = queryset.order_by("-vote_score", "-created_at")
        elif sort_by == "newest":
            queryset = queryset.order_by("-created_at")
        elif sort_by == "oldest":
            queryset = queryset.order_by("created_at")

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def vote(self, request, pk=None):
        """API để upvote hoặc downvote một comment"""
        comment = self.get_object()
        vote_type = request.data.get("vote_type", None)

        if vote_type not in ["upvote", "downvote"]:
            return Response(
                {"detail": "Loại vote không hợp lệ."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Kiểm tra xem đã vote chưa
        try:
            vote = CommentVote.objects.get(user=request.user, comment=comment)

            # Nếu vote cùng loại, xóa vote (hủy vote)
            if vote.vote_type == vote_type:
                vote.delete()
                return Response({"status": "vote removed"}, status=status.HTTP_200_OK)

            # Nếu vote khác loại, cập nhật vote
            vote.vote_type = vote_type
            vote.save()

        except CommentVote.DoesNotExist:
            # Nếu chưa vote, tạo vote mới
            vote = CommentVote.objects.create(
                user=request.user, comment=comment, vote_type=vote_type
            )

        serializer = CommentVoteSerializer(vote)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated, IsAdminForVerification],
    )
    def verify(self, request, pk=None):
        """API để admin đánh dấu comment là đúng hoặc sai"""
        comment = self.get_object()
        verification = request.data.get("verification", None)

        if verification not in ["correct", "incorrect", "unverified"]:
            return Response(
                {"detail": "Trạng thái xác minh không hợp lệ."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        comment.verification_status = verification
        comment.save()

        serializer = self.get_serializer(comment)
        return Response(serializer.data)
