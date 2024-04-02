from paths import conf_path, data_path

import json
import os

def init_config(path: str, initial_data: dict[str, any]) -> None:
    if os.path.exists(path): return

    with open(path, 'w', encoding = 'utf-8') as config_file:
        json.dump(initial_data, config_file, indent = 4)

class Config:
    def __init__(self, path: str, initial_data: dict[str, any] = {}) -> None:
        init_config(path, initial_data)

        self.path = path

        with open(path, 'r', encoding = 'utf-8') as config_file: self.config = json.load(config_file)

    def get(self, key: str) -> any: return self.config.get(key)

    def set(self, key: str, value: str) -> None:
        self.config[key] = value

        with open(self.path, 'w', encoding = 'utf-8') as config_file: json.dump(self.config, config_file, indent = 4)

    def push(self, key: str, value: str) -> None:
        array: list[any] = self.config.get(key)

        array.append(value)

        self.set(key, array)

app_data = Config(data_path)
config   = Config(conf_path, app_data.get('base_config'))