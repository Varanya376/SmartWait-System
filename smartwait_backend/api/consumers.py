from channels.generic.websocket import AsyncWebsocketConsumer
import json

class QueueConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.group_name = "queue_updates"

        # join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # leave group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # 🔥 receive update from backend
    async def send_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))