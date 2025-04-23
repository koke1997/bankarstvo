import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

User = get_user_model()

class NotificationsConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications.
    Handles connections for individual users and broadcasts notifications.
    """
    
    async def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection.
        """
        # Get the user
        user = self.scope["user"]
        
        if user.is_anonymous:
            # Reject the connection for anonymous users
            await self.close()
            return
        
        # Create a user-specific notification group
        self.notification_group_name = f'user_{user.id}_notifications'
        
        # Join the user-specific group
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        
        # Accept the WebSocket connection
        await self.accept()
    
    async def disconnect(self, close_code):
        """
        Called when the WebSocket closes for any reason.
        """
        # Leave the user-specific group
        if hasattr(self, 'notification_group_name'):
            await self.channel_layer.group_discard(
                self.notification_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """
        Called when we get a text frame from the client.
        """
        # Parse the received JSON
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message', '')
            
            # Echo the message back (for testing purposes)
            await self.send(text_data=json.dumps({
                'message': f'Echo: {message}'
            }))
        except json.JSONDecodeError:
            # Send an error message if the received data is not valid JSON
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))
    
    async def notification_message(self, event):
        """
        Handler for messages sent to the notification group.
        """
        # Send the notification to the WebSocket
        await self.send(text_data=json.dumps({
            'type': event.get('type', 'notification'),
            'message': event.get('message', ''),
            'data': event.get('data', {})
        }))