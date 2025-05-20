from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Post, PostMedia, Like, Share
from .serializers import (
    PostSerializer,
    PostMediaSerializer,
    LikeSerializer,
    ShareSerializer,
)


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


class PostViewSet(viewsets.ModelViewSet):
    """API endpoint cho quản lý bài viết"""

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """
        Tùy chỉnh queryset dựa trên loại feed hoặc các bài viết công khai
        """
        queryset = super().get_queryset()

        # Mặc định chỉ hiển thị các bài viết công khai
        queryset = queryset.filter(is_public=True)

        # Lọc theo loại feed nếu có
        feed_type = self.request.query_params.get("feed_type", None)
        if feed_type == "friends":
            # Lấy danh sách bạn bè từ Friendship model
            from users.models import Friendship

            friends_as_sender = Friendship.objects.filter(
                sender=self.request.user, status="accepted"
            ).values_list("receiver", flat=True)

            friends_as_receiver = Friendship.objects.filter(
                receiver=self.request.user, status="accepted"
            ).values_list("sender", flat=True)

            # Lấy bài viết từ bạn bè và chính mình
            queryset = queryset.filter(
                user__in=list(friends_as_sender)
                + list(friends_as_receiver)
                + [self.request.user.id]
            )
        elif feed_type == "following":
            # Lấy danh sách người đang theo dõi từ Follow model
            from users.models import Follow

            following_ids = Follow.objects.filter(
                follower=self.request.user
            ).values_list("followed", flat=True)

            # Lấy bài viết từ người đang theo dõi và chính mình
            queryset = queryset.filter(
                user__in=list(following_ids) + [self.request.user.id]
            )
        elif feed_type == "my":
            # Chỉ lấy bài viết của chính mình
            queryset = queryset.filter(user=self.request.user)

        # Lọc theo user nếu có
        user_id = self.request.query_params.get("user_id", None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # Tìm kiếm theo nội dung
        search = self.request.query_params.get("search", None)
        if search:
            queryset = queryset.filter(content__icontains=search)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def like(self, request, pk=None):
        """API để like một bài viết"""
        post = self.get_object()

        # Kiểm tra xem đã like chưa
        like, created = Like.objects.get_or_create(user=request.user, post=post)

        if not created:
            # Nếu đã like rồi, xóa like (unlike)
            like.delete()
            return Response({"status": "unliked"}, status=status.HTTP_200_OK)

        serializer = LikeSerializer(like)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def share(self, request, pk=None):
        """API để chia sẻ một bài viết"""
        post = self.get_object()

        content = request.data.get("content", "")

        share = Share.objects.create(user=request.user, post=post, content=content)

        serializer = ShareSerializer(share)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated]
    )
    def likes(self, request, pk=None):
        """API để lấy danh sách người đã like bài viết"""
        post = self.get_object()
        likes = post.likes.all()

        serializer = LikeSerializer(likes, many=True)
        return Response(serializer.data)

    @action(
        detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated]
    )
    def shares(self, request, pk=None):
        """API để lấy danh sách người đã chia sẻ bài viết"""
        post = self.get_object()
        shares = post.shares.all()

        serializer = ShareSerializer(shares, many=True)
        return Response(serializer.data)


class PostMediaViewSet(viewsets.ModelViewSet):
    """API endpoint cho quản lý media trong bài viết"""

    queryset = PostMedia.objects.all()
    serializer_class = PostMediaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Giới hạn media theo post nếu có
        post_id = self.request.query_params.get("post_id", None)
        if post_id:
            return PostMedia.objects.filter(post_id=post_id)
        return PostMedia.objects.none()  # Mặc định không trả về gì nếu không có post_id
