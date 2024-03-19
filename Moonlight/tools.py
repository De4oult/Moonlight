from hashlib import sha256

def password_hash(password: str) -> str: return sha256(password).hexdigest()