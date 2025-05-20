import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Room, Message, UserStatus


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Tham gia room
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Cập nhật trạng thái người dùng thành online
        if self.user.is_authenticated:
            await self.set_user_online(True)

        await self.accept()

    async def disconnect(self, close_code):
        # Rời khỏi room
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        # Cập nhật trạng thái người dùng thành offline
        if hasattr(self, "user") and self.user.is_authenticated:
            await self.set_user_online(False)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get("type", "message")

        if message_type == "message":
            message = text_data_json["message"]

            # Lưu tin nhắn vào database
            if self.user.is_authenticated:
                message_obj = await self.save_message(message)

                # Gửi tin nhắn đến room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat_message",
                        "message": message,
                        "sender_id": self.user.id,
                        "sender_username": self.user.username,
                        "message_id": message_obj.id,
                        "timestamp": message_obj.created_at.isoformat(),
                    },
                )
        elif message_type == "typing":
            is_typing = text_data_json.get("is_typing", False)

            # Gửi trạng thái đang nhập đến room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_typing",
                    "sender_id": self.user.id,
                    "sender_username": self.user.username,
                    "is_typing": is_typing,
                },
            )
        elif message_type == "read_messages":
            message_ids = text_data_json.get("message_ids", [])

            # Đánh dấu tin nhắn đã đọc
            if self.user.is_authenticated and message_ids:
                await self.mark_messages_read(message_ids)

                # Gửi thông báo tin nhắn đã đọc
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "messages_read",
                        "reader_id": self.user.id,
                        "reader_username": self.user.username,
                        "message_ids": message_ids,
                    },
                )

    async def chat_message(self, event):
        # Gửi tin nhắn đến WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "type": "message",
                    "message": event["message"],
                    "sender_id": event["sender_id"],
                    "sender_username": event["sender_username"],
                    "message_id": event["message_id"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    async def user_typing(self, event):
        # Gửi trạng thái đang nhập đến WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "type": "typing",
                    "sender_id": event["sender_id"],
                    "sender_username": event["sender_username"],
                    "is_typing": event["is_typing"],
                }
            )
        )

    async def messages_read(self, event):
        # Gửi thông báo tin nhắn đã đọc
        await self.send(
            text_data=json.dumps(
                {
                    "type": "read",
                    "reader_id": event["reader_id"],
                    "reader_username": event["reader_username"],
                    "message_ids": event["message_ids"],
                }
            )
        )

    @database_sync_to_async
    def save_message(self, content):
        # Lấy hoặc tạo phòng chat
        room = Room.objects.get(id=self.room_name)

        # Tạo tin nhắn mới
        message = Message.objects.create(room=room, sender=self.user, content=content)

        return message

    @database_sync_to_async
    def set_user_online(self, is_online):
        # Cập nhật trạng thái người dùng
        status, created = UserStatus.objects.get_or_create(user=self.user)
        status.is_online = is_online
        status.save()

    @database_sync_to_async
    def mark_messages_read(self, message_ids):
        # Đánh dấu tin nhắn đã đọc
        Message.objects.filter(id__in=message_ids, room__id=self.room_name).exclude(
            sender=self.user
        ).update(is_read=True)
