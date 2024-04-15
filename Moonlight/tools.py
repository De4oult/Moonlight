from secrets  import token_hex
from datetime import datetime
from hashlib  import sha256
from uuid     import uuid4

import os

def password_hash(password: str) -> str | None: return sha256(password.encode()).hexdigest() if password else None
def generate_token() -> str:                    return token_hex(32)
def get_now_datetime() -> str:                  return datetime.now().strftime('%d-%m-%Y %H:%M:%S')
def strip_ext(filename: str, ext: str) -> str:  return filename.rstrip(ext) if filename.endswith(ext) else filename
def add_ext(filename: str, ext: str) -> str:    return filename if filename.endswith(ext) else filename + ext
def generate_uuid() -> str:                     return int(str(uuid4().int)[:14]) 
def remove_file(filename: str) -> str:
    if os.path.isfile(filename):
        os.remove(filename)
    
def check_path_exist(path: str) -> bool:
    if os.path.exists(path): return True

    os.makedirs(os.path.dirname(path), exist_ok = True)

    return False