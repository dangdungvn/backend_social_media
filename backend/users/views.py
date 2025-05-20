from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from rest_framework import viewsets, status, generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Profile, Friendship, Follow
from .serializers import (
    UserSerializer,
    ProfileSerializer,
    FriendshipSerializer,
    FollowSerializer,
)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint để xem và tìm kiếm người dùng"""

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Tìm kiếm theo username, email, họ tên
        search = self.request.query_params.get("search", None)
        if search:
            queryset = (
                queryset.filter(username__icontains=search)
                | queryset.filter(email__icontains=search)
                | queryset.filter(first_name__icontains=search)
                | queryset.filter(last_name__icontains=search)
            )

        return queryset


class ProfileViewSet(viewsets.ModelViewSet):
    """API endpoint cho trang cá nhân người dùng"""

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Giới hạn quyền chỉnh sửa chỉ cho chủ profile
        if self.action in ["update", "partial_update", "destroy"]:
            return Profile.objects.filter(user=self.request.user)
        return Profile.objects.all()

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Lấy profile của người dùng đang đăng nhập"""
        profile = get_object_or_404(Profile, user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def posts(self, request, pk=None):
        """Lấy tất cả bài viết của một người dùng"""
        profile = self.get_object()
        posts = profile.user.posts.order_by("-created_at")

        from posts.serializers import PostSerializer

        serializer = PostSerializer(posts, many=True, context={"request": request})
        return Response(serializer.data)


class FriendshipViewSet(viewsets.ModelViewSet):
    """API endpoint cho quản lý kết bạn"""

    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Người dùng chỉ xem được yêu cầu kết bạn liên quan đến họ
        return Friendship.objects.filter(
            sender=self.request.user
        ) | Friendship.objects.filter(receiver=self.request.user)

    def perform_create(self, serializer):
        # Người gửi luôn là người đang đăng nhập
        serializer.save(sender=self.request.user)

    @action(detail=False, methods=["get"])
    def pending(self, request):
        """Lấy tất cả yêu cầu kết bạn đang chờ"""
        pending_requests = Friendship.objects.filter(
            receiver=request.user, status="pending"
        )
        serializer = self.get_serializer(pending_requests, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def friends(self, request):
        """Lấy danh sách bạn bè hiện tại"""
        friends_as_sender = Friendship.objects.filter(
            sender=request.user, status="accepted"
        ).values_list("receiver", flat=True)

        friends_as_receiver = Friendship.objects.filter(
            receiver=request.user, status="accepted"
        ).values_list("sender", flat=True)

        friends = User.objects.filter(
            id__in=list(friends_as_sender) + list(friends_as_receiver)
        )

        serializer = UserSerializer(friends, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        """Chấp nhận yêu cầu kết bạn"""
        friendship = self.get_object()
        if friendship.receiver != request.user:
            return Response(
                {"detail": "Bạn không có quyền chấp nhận yêu cầu này."},
                status=status.HTTP_403_FORBIDDEN,
            )

        friendship.status = "accepted"
        friendship.save()
        serializer = self.get_serializer(friendship)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Từ chối yêu cầu kết bạn"""
        friendship = self.get_object()
        if friendship.receiver != request.user:
            return Response(
                {"detail": "Bạn không có quyền từ chối yêu cầu này."},
                status=status.HTTP_403_FORBIDDEN,
            )

        friendship.status = "rejected"
        friendship.save()
        serializer = self.get_serializer(friendship)
        return Response(serializer.data)


class FollowViewSet(viewsets.ModelViewSet):
    """API endpoint cho theo dõi người dùng"""

    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Người dùng chỉ xem được thông tin theo dõi liên quan đến họ
        return Follow.objects.filter(
            follower=self.request.user
        ) | Follow.objects.filter(followed=self.request.user)

    def perform_create(self, serializer):
        # Người theo dõi luôn là người đang đăng nhập
        serializer.save(follower=self.request.user)

    @action(detail=False, methods=["get"])
    def following(self, request):
        """Lấy danh sách người đang theo dõi"""
        following_ids = Follow.objects.filter(follower=request.user).values_list(
            "followed", flat=True
        )

        following = User.objects.filter(id__in=following_ids)
        serializer = UserSerializer(following, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def followers(self, request):
        """Lấy danh sách người theo dõi mình"""
        follower_ids = Follow.objects.filter(followed=request.user).values_list(
            "follower", flat=True
        )

        followers = User.objects.filter(id__in=follower_ids)
        serializer = UserSerializer(followers, many=True)
        return Response(serializer.data)
