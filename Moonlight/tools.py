from secrets import token_hex
from hashlib import sha256

def password_hash(password: str) -> str: return sha256(password.encode()).hexdigest() if password else None
def generate_token() -> str: return token_hex(32)