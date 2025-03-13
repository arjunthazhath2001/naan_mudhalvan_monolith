import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from students.models import StudentRegistration, RecruiterStudentAttendance
from django.utils import timezone

class RecruiterConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get recruiter_id and job_fair_id from URL route
        self.recruiter_id = self.scope['url_route']['kwargs']['recruiter_id']
        self.job_fair_id = self.scope['url_route']['kwargs']['job_fair_id']
        
        # Create a unique group name for this recruiter at this job fair
        self.room_group_name = f'recruiter_{self.recruiter_id}_jobfair_{self.job_fair_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    # Receive message from WebSocket (not needed for this implementation)
    async def receive(self, text_data):
        pass
    
    # Receive message from room group
    async def new_attendance(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'new_attendance',
            'student': event['student'],
            'timestamp': event['timestamp'],
            'status': event.get('status', 'pending'),
            'round_1': event.get('round_1', 'not_started'),
            'round_2': event.get('round_2', 'not_started'),
            'round_3': event.get('round_3', 'not_started'),
            'notes': event.get('notes', '')
        }))