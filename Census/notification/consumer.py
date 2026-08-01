import json
from channels.generic.websocket import AsyncWebsocketConsumer
from crum import get_current_user


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if self.user.is_authenticated:
            self.room_group_name = f"user_{self.user.id}"
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def send_notification(self, event):
        title = event.get("title", "")
        message = event.get("message", "")
        notification_type = event.get("notification_type", "")
        await self.send(text_data=json.dumps({
            "type": "notification",
            "title": title,
            "message": message,
            "notification_type": notification_type
        }))