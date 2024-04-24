from Moonlight.core.paths import conf_path, data_path

import json
import os

def init_config(path: str, initial_data: dict[str, any], skip: bool = False) -> dict[str, any]:
    if os.path.exists(path) and not skip: 
        with open(path, 'r', encoding = 'utf-8') as config_file: 
            return json.load(config_file)

    with open(path, 'w', encoding = 'utf-8') as config_file:
        json.dump(initial_data, config_file, indent = 4)

    return initial_data

class Config:
    def __init__(self, path: str, initial_data: dict[str, any] = {}) -> None:
        self.path = path

        self.config = init_config(self.path, initial_data)

    def get(self, tab: str) -> any: return self.config.get(tab)

    def set(self, tab: str, value: str) -> None:
        self.config[tab] = value

        with open(self.path, 'w', encoding = 'utf-8') as config_file: json.dump(self.config, config_file, indent = 4)

    def push(self, tab: str, value: str) -> None:
        array: list[any] = self.config.get(tab)

        array.append(value)

        self.set(tab, array)
    
    def delete(self, tab: str, key: str, value: str) -> None:
        self.set(tab, [element for element in self.config.get(tab) if element.get(key) != value])

    def reinit(self, initial_data: dict[str, any]) -> None:
        self.config = init_config(self.path, initial_data, skip = True)

app_data = Config(data_path)
config   = Config(conf_path, app_data.get('base_config'))