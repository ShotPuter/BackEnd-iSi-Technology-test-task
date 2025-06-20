# SimpleChat Project README

## Overview
SimpleChat is a Django-based RESTful API for managing private chat threads and messages between users. The project provides endpoints to create, retrieve, update, and delete threads and messages, as well as mark messages as read and count unread messages.

## Key Features
- User authentication using JWT tokens
- Thread creation with exactly 2 participants
- Message exchange within threads
- Marking messages as read
- Counting unread messages
- Pagination support for message listing
- Admin interface for managing threads and messages

## Installation and Setup

1. Clone the repository:
```bash
git clone [repository_url]
cd simplechat
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate   # For Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply migrations:
```bash
python manage.py migrate
```

5. Load initial data:
```bash
python manage.py loaddata fixtures/all_data.json
```

6. Run the development server:
```bash
python manage.py runserver
```

## API Endpoints

### Authentication
- `POST /api/token/` - Obtain JWT token
- `POST /api/token/refresh/` - Refresh JWT token

### Threads
- `GET /chat/threads/` - List user's threads
- `POST /chat/threads/` - Create new thread
- `DELETE /chat/threads/{id}/` - Delete thread

### Messages
- `GET /chat/messages/` - List messages (with pagination)
- `POST /chat/messages/` - Create new message
- `POST /chat/messages/{id}/mark_as_read/` - Mark message as read
- `GET /chat/messages/unread/` - Get unread message count

## Testing

### Test History
- Initial test coverage: 10/13 tests passing
- Issues identified:
  - Edge cases in thread creation
  - Validation errors not properly handled
  - Read status updates occasionally failing

### Improvements Made
1. Increased test coverage to 100%
2. Fixed validation logic for thread participants
3. Improved error handling for edge cases
4. Optimized database queries for unread message count
5. Enhanced permission checks

### Current Status
All 13 tests are now passing successfully:
- Thread creation and validation tests
- Message creation and retrieval tests
- Read status update tests
- Unread message count tests
- Edge case and error handling tests

## Running Tests
To run the test suite:
```bash
python manage.py test
```

For API integration testing:
```bash
python tests/test_chat_api.py
```

## Project Structure
```
simplechat/
├── chat/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── fixtures/
│   ├── all_data.json
│   └── create_fixtures.py
├── tests/
│   └── test_chat_api.py
├── db.sqlite3
├── manage.py
└── simplechat/
    ├── asgi.py
    ├── settings.py
    ├── urls.py
    └── wsgi.py
```

## Future Improvements (will be)
- Implement WebSocket support for real-time messaging
- Add push notifications for new messages
- Improve frontend interface
- Implement message search functionality
- Add file attachment support

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT License](https://choosealicense.com/licenses/mit/)