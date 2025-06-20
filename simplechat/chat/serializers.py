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
