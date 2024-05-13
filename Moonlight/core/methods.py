from datetime import datetime, timedelta
from typing   import Any

from Moonlight.core.tools    import generate_uuid, get_now_datetime, remove_file, password_hash, generate_token
from Moonlight.config.config import config


class Methods:
    '''Class of the main blocks of the application functionality'''
    @staticmethod
    def configure(host: str, port: int, loggers: list[str]) -> None:
        '''`Configures the database API`'''
        config.set('host',      host)
        config.set('port',      int(port))
        config.set('need_logs', True)
        config.set('loggers',   loggers)
    
    @staticmethod
    def create_user(username: str, password: str, permissions: str) -> None:
        '''`Creates a new user and writes it to the configuration`'''
        config.push('users', {
            'username'    : username,
            'password'    : password_hash(password),
            'permissions' : permissions.lower()
        })

    @staticmethod
    def delete_user(username: str) -> None:
        '''`Deletes a user`'''
        config.delete('users', 'username', username)

    @staticmethod
    def create_database(database_name: str, path: str, logs_path: str, author: str) -> dict[str, Any] | None:
        '''`Creates the database on behalf of the user passed in the {author} argument`'''
        if any(database.get('name') == database_name for database in config.get('databases')): return None
        
        database_info: dict[str, Any] = {
            'id'         : int(generate_uuid()),
            'name'       : database_name,
            'path'       : path,
            'logs_path'  : logs_path,
            'created_at' : get_now_datetime(),
            'author'     : author
        }

        config.push('databases', database_info)
    
        return database_info
    
    @staticmethod
    def delete_database(database_name: str, filename: str, logs_path: str) -> None:
        '''`Deletes the database and its corresponding log file`'''
        remove_file(filename)
        remove_file(logs_path)
        
        config.delete('databases', 'name', database_name)

    @staticmethod
    def create_token(username: str) -> dict[str, str]:
        '''`Generates a new user authorization token for API requests`'''
        token:   str = generate_token()
        expires: str = (datetime.now() + timedelta(hours = 3)).isoformat()
        created: str = datetime.now().isoformat()        

        config.push('api_keys', {
            'author'     : username,
            'token'      : token,
            'expires'    : expires,
            'created'    : created
        })

        return {
            'token'   : token, 
            'expires' : expires
        }