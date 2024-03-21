from paths import conf_path

import json
import os

def init_config(path) -> None:
    if os.path.exists(path): return

    with open(path, 'w', encoding = 'utf-8') as config_file:
        json.dump({
            'host'      : '127.0.0.1',
            'port'      : 3000,
            'need_logs' : False,
            'users'     : [],
            'loggers'   : ['warning', 'error'],
            'api_keys'  : [],
            'databases' : []
        }, config_file, indent = 4)

class Config:
    def __init__(self, path: str) -> None:
        init_config(path)

        self.path   = path

        with open(conf_path, 'r', encoding = 'utf-8') as config_file: 
            self.config = json.load(config_file)

    def get(self, key: str) -> any: return self.config.get(key)

    def set(self, key: str, value: str) -> None:
        self.config[key] = value

        with open(self.path, 'w', encoding = 'utf-8') as config_file: json.dump(self.config, config_file, indent = 4)

    def push(self, key: str, value: str) -> None:
        array: list[any] = self.config.get(key)

        array.append(value)

        self.set(key, array)


config = Config(conf_path)