
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .serializers import MessageSerializer
from .models import Conversation
from user_agents import parse
import socketio


class ChatbotConsumer(AsyncWebsocketConsumer):

    """
    Consumer WebSocket qui relaie les messages entre un client web
    (via Channels) et un serveur Rasa (via Socket.IO).
    """
    @database_sync_to_async
    def get_or_create_conv(self, channel):
        return Conversation.objects.get_or_create(
            user= self.user.id if self.user.is_authenticated else None,
            anonymous_id= self.scope.get("chat_uuid"),
            channel= channel
        )

    @database_sync_to_async
    def save_message(self, conv, sender, text):
        message_data = {
            "conversation": conv.id,
            "sender": sender,
            "content": text
        }
        message = MessageSerializer(data=message_data)
        if message.is_valid():
            message.save()
            return message

    async def connect(self):

        header = dict(self.scope.get('headers', []))
        user_agent_bytes = header.get(b'user-agent', b'')
        user_agent_string = user_agent_bytes.decode('utf-8')
        user_agent = parse(user_agent_string)
         
        self.channel = "unknown"
        if user_agent.is_mobile:
            self.channel = 'mobile'
        elif user_agent.is_tablet:
            self.channel = 'tablet'
        elif user_agent.is_pc:
            self.channel = 'desktop'
        elif user_agent.is_bot:
            self.channel = 'bot'

        self.user = self.scope["user"]
        anonymous = self.scope.get("chat_uuid")

        if self.user.is_authenticated:
            self.room_group_name = f"user_{self.user.id}"
        else:
            self.room_group_name = f"anonymous_{anonymous}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        await self.accept()

        self.sio = socketio.AsyncClient()

        self.sio.on("bot_uttered", self.on_bot_uttered)

        try:
            await self.sio.connect("http://localhost:5005")
        except Exception:
            await self.close(code=1011)

    async def receive(self, text_data=None, bytes_data=None):
        """
        Appelée automatiquement par Channels à chaque message
        reçu du client WebSocket.
        """

        if not hasattr(self, "sio") or not self.sio.connected:
            return

        if text_data is None:
            return
        conversation, conv_created = await self.get_or_create_conv(self.channel)
        
        await self.save_message(conversation, 'user', text_data)
        
        user_uttered = {
            "groupe_name": self.room_group_name,
            "sender": self.channel,
            "message": text_data,
        }
        print('User message :', user_uttered)
        await self.sio.emit(
            "user_uttered",
            {
                "sender": self.channel,
                "message": text_data,
            },
        )

    async def on_bot_uttered(self, user_data):
        """
        Callback appelé par python-socketio quand Rasa émet
        l'événement 'bot_uttered'.
        """            
        conversation, conv_created = await self.get_or_create_conv(self.channel)

        await self.save_message(conversation, 'bot', user_data.get('text'))
        
        bot_uttered = {
            "groupe_name": self.room_group_name,
            "sender": self.channel,
            "message": user_data.get("text"),
        }
        print('Bot message :', bot_uttered)
        text = user_data.get("text")
        if text:
            await self.send(text_data=text)

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name,
            )
        if hasattr(self, "sio"):
            await self.sio.disconnect()