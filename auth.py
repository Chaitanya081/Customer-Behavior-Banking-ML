import hashlib

USERS = {}  # In-memory (hackathon safe)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(email, password):
    if email in USERS:
        return False
    USERS[email] = hash_password(password)
    return True

def login_user(email, password):
    if email not in USERS:
        return False
    return USERS[email] == hash_password(password)
