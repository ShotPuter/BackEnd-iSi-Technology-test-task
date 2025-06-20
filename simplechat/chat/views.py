from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Thread, Message
from .serializers import ThreadSerializer, MessageSerializer
from django.db.models import Q

class ThreadViewSet(viewsets.ModelViewSet):
    serializer_class = ThreadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Thread.objects.filter(participants=self.request.user)

    def create(self, request, *args, **kwargs):
        participants = request.data.get('participants', [])
        if len(participants) != 2:
            return Response({'detail': 'Thread must have exactly 2 participants.'}, status=400)
        threads = Thread.objects.filter(participants__in=participants).distinct()
        for thread in threads:
            if set(thread.participants.values_list('id', flat=True)) == set(participants):
                serializer = self.get_serializer(thread)
                return Response(serializer.data)
        return super().create(request, *args, **kwargs)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(thread__participants=self.request.user)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        msg = self.get_object()
        if msg.thread.participants.filter(id=request.user.id).exists():
            msg.is_read = True
            msg.save()
            return Response({'status': 'marked as read'})
        return Response({'error': 'Not allowed'}, status=403)


class UnreadCountView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Message.objects.filter(
            thread__participants=request.user,
            is_read=False
        ).exclude(sender=request.user).count()

        return Response({'unread_count': count})
