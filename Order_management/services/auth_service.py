import requests
from config import AUTH_SERVICE_URL

def is_authenticated(token):
    if not token:
        return False
    # Nếu token có tiền tố "Bearer ", loại bỏ nó
    if token.startswith("Bearer "):
        token = token.split(" ")[1]
    try:
        response = requests.post(
            AUTH_SERVICE_URL,
            json={'token': token}
        )
        return response.status_code == 200 and response.json().get('valid', False)
    except Exception:
        return False
