from secrets  import token_hex
from datetime import datetime
from hashlib  import sha256

def password_hash(password: str) -> str: return sha256(password.encode()).hexdigest() if password else None
def generate_token() -> str: return token_hex(32)
def get_now_datetime() -> str: return datetime.now().strftime('%d-%m-%Y %H:%M:%S')
def strip_json(filename: str) -> str: return filename.rstrip('.json') if filename.endswith('.json') else filename