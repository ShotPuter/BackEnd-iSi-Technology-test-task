from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from .models import Thread, Message
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class ChatAPITest(APITestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username='alice', password='test1234')
        self.bob = User.objects.create_user(username='bob', password='test1234')

        self.thread = Thread.objects.create()
        self.thread.participants.set([self.alice, self.bob])

        self.message = Message.objects.create(
            thread=self.thread,
            sender=self.alice,
            text="Привіт, як справи?"
        )

        self.alice_token = str(RefreshToken.for_user(self.alice).access_token)
        self.bob_token = str(RefreshToken.for_user(self.bob).access_token)

        self.client_alice = APIClient()
        self.client_alice.credentials(HTTP_AUTHORIZATION='Bearer ' + self.alice_token)

        self.client_bob = APIClient()
        self.client_bob.credentials(HTTP_AUTHORIZATION='Bearer ' + self.bob_token)

    def test_get_threads(self):
        response = self.client_alice.get('/chat/threads/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_thread_duplicate(self):
        response = self.client_alice.post('/chat/threads/', {"participants": [self.alice.id, self.bob.id]})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_thread(self):
        response = self.client_alice.post('/chat/threads/', {"participants": [self.alice.id]})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_message(self):
        response = self.client_alice.post('/chat/messages/', {
            "thread": self.thread.id,
            "text": "Ще одне повідомлення"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['text'], "Ще одне повідомлення")

    def test_unread_count(self):
        # Убедимся, что сообщение существует и принадлежит диалогу
        self.assertFalse(self.message.is_read)  # Сообщение должно быть непрочитанным
        self.assertIn(self.bob, self.thread.participants.all())  # Bob должен быть участником диалога

        # Выполняем запрос
        response = self.client_bob.get('/chat/messages/unread/')  # Или '/chat/messages/unread/'

        # Проверяем результат
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 1)

    def test_mark_message_as_read(self):
        response = self.client_bob.post(f'/chat/messages/{self.message.id}/mark_as_read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'marked as read')

    def test_delete_thread(self):
        response = self.client_alice.delete(f'/chat/threads/{self.thread.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_message_validation(self):
        response = self.client_alice.post('/chat/messages/', {
            "thread": self.thread.id
            # no "text"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('text', response.data)

    def test_unauthenticated_access(self):
        client = APIClient()
        res = client.get('/chat/threads/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_foreign_thread(self):
        charlie = User.objects.create_user(username='charlie', password='test1234')
        charlie_token = str(RefreshToken.for_user(charlie).access_token)
        client_charlie = APIClient()
        client_charlie.credentials(HTTP_AUTHORIZATION='Bearer ' + charlie_token)

        res = client_charlie.get('/chat/messages/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 0)
        res = client_charlie.post('/chat/messages/', {
            "thread": self.thread.id,
            "text": "Привіт від чужака"
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_thread_id(self):
        res = self.client_alice.post('/chat/messages/', {
            "thread": 999,
            "text": "Це неіснуючий тред"
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('thread', res.data)

    def test_pagination_on_messages(self):
        for i in range(3):
            Message.objects.create(
                thread=self.thread,
                sender=self.bob,
                text=f"test msg {i}"
            )

        res = self.client_alice.get('/chat/messages/?limit=2&offset=0')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 2)
        self.assertIn('next', res.data)

    def test_cannot_create_thread_with_more_than_two(self):
        charlie = User.objects.create_user(username='charlie', password='test1234')
        res = self.client_alice.post('/chat/threads/', {
            "participants": [self.alice.id, self.bob.id, charlie.id]
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

