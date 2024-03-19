import json
from pathlib import Path

config_path = Path('config.json')

def load_config():
    if config_path.exists(): 
        with open(config_path, 'r') as f: return json.load(f)
    
    return {'auth_enabled': True, 'api_key': None}

def save_config(config):
    with open(config_path, 'w') as f:
        json.dump(config, f)