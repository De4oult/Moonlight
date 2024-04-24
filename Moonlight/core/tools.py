from secrets  import token_hex
from datetime import datetime
from hashlib  import sha256
from uuid     import uuid4

import os


def password_hash(password: str) -> str:
    '''Returns the SHA256 hash of the transmitted password'''
    return sha256(password.encode()).hexdigest() if password else None

def generate_token() -> str:
    '''Generates and returns a secure random token'''
    return token_hex(32)

def get_now_datetime() -> str:
    '''Returns the current date and time in the format `dd-mm-yyyy hh:mm:ss`'''
    return datetime.now().strftime('%d-%m-%Y %H:%M:%S')

def strip_ext(filename: str) -> str:
    '''Removes the file extension from the file name'''
    return os.path.splitext(filename)[0]

def get_filename_from_path(path: str) -> str:
    '''Extracts the file name without an extension from the full path'''
    return os.path.splitext(os.path.basename(path))[0]

def add_ext(filename: str, ext: str) -> str:
    '''Adds an extension to the file name'''
    return strip_ext(filename) + ext

def generate_uuid() -> str:
    '''Generates and returns a unique UUID'''
    return str(uuid4().int)[:14]

def is_full_path(path: str) -> bool:
    '''Checks if the path is absolute'''
    return os.path.isabs(path)

def remove_file(filename: str) -> None:
    '''Deletes the file if it exists'''
    if os.path.isfile(filename): os.remove(filename)

def is_file_exist(path: str) -> bool:
    '''Checks if the file exists at the specified path'''
    return os.path.exists(path)

def check_path_exist(path: str) -> bool:
    '''Checks the existence of the path, and if necessary, creates all the missing directories'''
    if os.path.exists(path): return True
    
    os.makedirs(os.path.dirname(path), exist_ok = True)
    
    return False











