from Moonlight.paths  import make_locale_path
from Moonlight.config import app_data

import json

class Messages:
    def __init__(self) -> None:
        self.locale_path = make_locale_path(app_data.get('current_locale'))

        with open(self.locale_path, 'r', encoding = 'utf-8') as locales_file:
            self.messages = json.load(locales_file)

    def get_message(self, category: str, message_id: str, **kwargs) -> str:
        def get_nested_message(parts, messages):
            if parts and messages: return get_nested_message(parts[1:], messages.get(parts[0], {}))
            
            return messages

        parts = category.split('.')
        message = get_nested_message(parts + [message_id], self.messages)

        return message.format(**kwargs)
    
t =  Messages().get_message