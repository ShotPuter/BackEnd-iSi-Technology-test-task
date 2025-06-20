from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q, Count

from .models import Thread, Message
from .serializers import ThreadSerializer, MessageSerializer


class ThreadViewSet(viewsets.ModelViewSet):
    """ViewSet for managing threads (conversations)."""

    serializer_class = ThreadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get threads for the current user."""
        return Thread.objects.filter(participants=self.request.user)

    def create(self, request, *args, **kwargs):
        """Create a new thread or return existing one."""
        participants = request.data.get('participants', [])

        # Basic validation of participant count
        if len(participants) != 2:
            return Response(
                {'detail': 'Thread must have exactly 2 participants.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        for participant_id in participants:
            try:
                threads = Thread.objects.filter(participants=participant_id)
                for thread in threads:
                    thread_participants = list(
                        thread.participants.values_list('id', flat=True)
                    )
                    if (len(thread_participants) == 2 and
                            set(thread_participants) == set(participants)):
                        # Found duplicate - return existing thread
                        serializer = self.get_serializer(thread)
                        return Response(
                            serializer.data,
                            status=status.HTTP_200_OK
                        )
            except Exception:
                continue

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            thread = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing messages."""

    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get messages from threads where current user is a participant."""
        return Message.objects.filter(thread__participants=self.request.user)

    def perform_create(self, serializer):
        """Save message with current user as sender."""
        serializer.save(sender=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark a message as read."""
        msg = self.get_object()
        if msg.thread.participants.filter(id=request.user.id).exists():
            msg.is_read = True
            msg.save()
            return Response({'status': 'marked as read'})
        return Response(
            {'error': 'Not allowed'},
            status=status.HTTP_403_FORBIDDEN
        )

    @action(detail=False, methods=['get'], url_path='unread')
    def unread_count(self, request):
        """Get count of unread messages."""
        count = Message.objects.filter(
            thread__participants=request.user,
            is_read=False
        ).exclude(sender=request.user).count()

        return Response({'unread_count': count})


class UnreadCountView(generics.GenericAPIView):
    """View for getting unread message count."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get count of unread messages for current user."""
        count = Message.objects.filter(
            thread__participants=request.user,
            is_read=False
        ).exclude(sender=request.user).count()

        return Response({'unread_count': count})