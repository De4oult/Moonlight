from Moonlight.tools     import generate_uuid, get_now_datetime, remove_file, password_hash, generate_token
from Moonlight.config    import config

from datetime import datetime, timedelta

class Methods:
    def configure(host: str, port: int, loggers: list[str]) -> None:
        config.set('host',      host)
        config.set('port',      int(port))
        config.set('need_logs', True)
        config.set('loggers',   loggers)

    def create_user(username: str, password: str, permissions: str) -> None:
        config.push('users', {
            'username'    : username,
            'password'    : password_hash(password),
            'permissions' : permissions.lower()
        })

    def delete_user(username: str) -> None:
        config.delete('users', 'username', username)

    def create_database(database_name: str, path: str, logs_path: str, author: str) -> dict[str, any]:
        if any(database.get('name') == database_name for database in config.get('databases')): return
        
        database_info = {
            'id'         : generate_uuid(),
            'name'       : database_name,
            'path'       : path,
            'logs_path'  : logs_path,
            'created_at' : get_now_datetime(),
            'author'     : author
        }

        config.push('databases', database_info)
    
        return database_info
    
    def delete_database(database_name: str, filename: str, logs_path: str):
        remove_file(filename)
        remove_file(logs_path)
        
        config.delete('databases', 'name', database_name)

    def create_token(username: str) -> dict[str, str]:
        token: str   = generate_token()
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