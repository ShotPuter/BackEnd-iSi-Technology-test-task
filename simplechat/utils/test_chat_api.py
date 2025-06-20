import requests
import json

BASE_URL = "http://127.0.0.1:8000"


def print_json(title, res):
    """Print JSON response with indentation."""
    print(f"\n🔸 {title}")
    try:
        print(json.dumps(res.json(), indent=2, ensure_ascii=False))
    except Exception:
        print(res.text)


def auth(username, password):
    """Authenticate user and return authorization headers."""
    res = requests.post(
        f"{BASE_URL}/api/token/",
        json={"username": username, "password": password},
    )
    print(res.text)
    if "access" not in res.json():
        raise Exception("Login failed")
    token = res.json()["access"]
    return {"Authorization": f"Bearer {token}"}


# ==== Authenticate 2 users ====
print("🔐 Logging in...")
alice_headers = auth("alice", "test1234")
bob_headers = auth("bob", "test1234")

# ==== 1. Create or retrieve Thread ====
print("\n🧵 Creating thread (alice + bob)...")
res = requests.post(
    f"{BASE_URL}/chat/threads/",
    headers=alice_headers,
    json={"participants": [1, 2]},
)
thread = res.json()
thread_id = thread["id"]
print_json("Thread created or returned", res)

# ==== 2. Retrieve Thread list for the user ====
res = requests.get(f"{BASE_URL}/chat/threads/", headers=alice_headers)
print_json("Thread list (alice)", res)

# ==== 3. Check pagination ====
res = requests.get(
    f"{BASE_URL}/chat/messages/?limit=1&offset=0", headers=alice_headers
)
print_json("Paginated messages (limit=1)", res)

# ==== 4. Create a message ====
print("\n💬 Sending a message from Alice...")
res = requests.post(
    f"{BASE_URL}/chat/messages/",
    headers=alice_headers,
    json={"thread": thread_id, "text": "Hello from Alice"},
)
print_json("Message creation response", res)

if res.status_code != 201:
    print("❌ Message creation failed")
    exit(1)

message = res.json()
message_id = message["id"]

# ==== 5. Retrieve messages in this Thread ====
res = requests.get(
    f"{BASE_URL}/chat/messages/?thread={thread_id}", headers=bob_headers
)
print_json("Messages in thread", res)

# ==== 6. Mark message as read ====
res = requests.post(
    f"{BASE_URL}/chat/messages/{message_id}/mark_as_read/", headers=bob_headers
)
print_json("Mark as read", res)

# ==== 7. Retrieve unread count ====
res = requests.get(f"{BASE_URL}/chat/messages/unread/", headers=bob_headers)
print_json("Unread count", res)

# ==== 8. Delete Thread ====
res = requests.delete(
    f"{BASE_URL}/chat/threads/{thread_id}/", headers=alice_headers
)
print("\n🗑️ Delete thread:", "✅ OK" if res.status_code == 204 else f"❌ {res.status_code}")

# ==== 9. Validation: Create Thread with 1 participant (invalid) ====
res = requests.post(
    f"{BASE_URL}/chat/threads/",
    headers=alice_headers,
    json={"participants": [1]},
)
print_json("Invalid Thread (1 participant)", res)

# ==== 10. Validation: Create Message without text ====
res = requests.post(
    f"{BASE_URL}/chat/messages/",
    headers=alice_headers,
    json={"thread": thread_id},
)
print_json("Invalid Message (missing text)", res)