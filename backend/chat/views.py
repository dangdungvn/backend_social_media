from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Room, Message, MessageMedia, UserStatus
from .serializers import (
    RoomSerializer,
    MessageSerializer,
    MessageMediaSerializer,
    UserStatusSerializer,
)


class ChatRoomViewSet(viewsets.ModelViewSet):
    """API endpoint cho quản lý phòng chat"""

    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Chỉ lấy các phòng chat mà người dùng hiện tại tham gia
        return Room.objects.filter(participants=self.request.user)

    @action(
        detail=False, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def get_or_create(self, request):
        """
        API để lấy phòng chat hiện có hoặc tạo phòng chat mới giữa hai người dùng
        """
        other_user_id = request.data.get("user_id", None)

        if not other_user_id:
            return Response(
                {"detail": "Thiếu ID người dùng."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Kiểm tra xem đã có phòng chat giữa hai người dùng chưa
        rooms = Room.objects.filter(participants=request.user).filter(
            participants=other_user_id
        )

        if rooms.exists():
            # Nếu có rồi, trả về phòng chat đầu tiên
            room = rooms.first()
        else:
            # Nếu chưa có, tạo phòng chat mới
            room = Room.objects.create()
            room.participants.add(request.user.id, other_user_id)
            room.save()

        serializer = self.get_serializer(room)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """API endpoint cho quản lý tin nhắn"""

    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ["created_at"]

    def get_queryset(self):
        # Lọc tin nhắn theo phòng chat
        room_id = self.request.query_params.get("room_id", None)
        if room_id:
            return Message.objects.filter(room_id=room_id)
        return Message.objects.none()  # Mặc định không trả về gì nếu không có room_id

    def perform_create(self, serializer):
        # Gán người gửi là người dùng hiện tại
        serializer.save(sender=self.request.user)

    @action(
        detail=False, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def mark_as_read(self, request):
        """
        API để đánh dấu nhiều tin nhắn là đã đọc
        """
        message_ids = request.data.get("message_ids", [])
        room_id = request.data.get("room_id", None)

        if room_id:
            # Đánh dấu tất cả tin nhắn chưa đọc trong phòng từ người khác là đã đọc
            Message.objects.filter(room_id=room_id, is_read=False).exclude(
                sender=request.user
            ).update(is_read=True)
        elif message_ids:
            # Đánh dấu các tin nhắn cụ thể là đã đọc
            Message.objects.filter(id__in=message_ids).exclude(
                sender=request.user
            ).update(is_read=True)
        else:
            return Response(
                {"detail": "Thiếu room_id hoặc message_ids."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"status": "success"})


class UserStatusViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint để xem trạng thái online của người dùng"""

    queryset = UserStatus.objects.all()
    serializer_class = UserStatusSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(
        detail=False, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def set_status(self, request):
        """
        API để cập nhật trạng thái online của người dùng hiện tại
        """
        is_online = request.data.get("is_online", True)

        status_obj, created = UserStatus.objects.get_or_create(user=request.user)
        status_obj.is_online = is_online
        status_obj.save()

        serializer = self.get_serializer(status_obj)
        return Response(serializer.data)
