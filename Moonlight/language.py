import json
import re

configuration: dict[str, any] = {
    'host'      : '',
    'port'      : 0,
    'need_logs' : False,
    'users'     : [],
    'loggers'   : [],
    'databases' : [],
    'api_keys'  : []
}

class Moonfile:
    def __init__(self) -> None:
        pass

def set_app(url: str) -> None: 
    configuration['host'], configuration['port'] = url.split(':')

def set_logging(messages: str) -> None: 
    configuration['loggers']   = messages.split()
    configuration['need_logs'] = True

def set_database(database: str) -> None:
    database = database.split()
    configuration['databases'].append({
        'name'   : database[0],
        'author' : database[-1].lstrip('@') if database[-1].startswith('@') else ''
    })

def create_user(user: str) -> None:
    permissions, username, password = user.split()
    configuration['users'].append({
        'permissions' : permissions.lower(), 
        'username'    : username, 
        'password'    : password
    })

command_map: dict[str, any] = {
    'APP'         : set_app,
    'LOGGING'     : set_logging,
    'DATABASE'    : set_database,
    'CREATE_USER' : create_user
}

def parse_config(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            if not line.strip() or line.startswith('#'): continue

            parts    = re.split(r'\s+', line.strip(), maxsplit = 1)
            command = parts[0]
            args    = parts[1] if len(parts) > 1 else ''
            
            if command in command_map: command_map[command](args)

# Путь к файлу конфигурации
config_file_path = './Moonlight/Moonfile'

# Парсинг и выполнение команд из файла конфигурации
parse_config(config_file_path)

# Вывод результата
print(json.dumps(configuration, indent = 4))