from rest_framework import serializers
from .models import Thread, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class ThreadSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())

    class Meta:
        model = Thread
        fields = ['id', 'participants', 'created', 'updated']

    def validate_participants(self, value):
        if len(value) != 2:
            raise serializers.ValidationError("A thread must have exactly 2 participants.")
        return value


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source='sender.id')

    class Meta:
        model = Message
        fields = ['id', 'thread', 'sender', 'text', 'created', 'is_read']

    def validate_thread(self, value):
        """Ensure the current user is a participant in the thread"""
        request = self.context.get('request')
        if request and request.user:
            if not value.participants.filter(id=request.user.id).exists():
                raise serializers.ValidationError("You are not a participant in this thread.")
        return value

    def validate_text(self, value):
        """Ensure text is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Text field is required and cannot be empty.")
        return value