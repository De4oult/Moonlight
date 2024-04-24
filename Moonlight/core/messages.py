from enum import Enum

import json

from Moonlight.core.paths    import make_locale_path
from Moonlight.config.config import app_data


class Style(Enum):
    INFO:    str = 'bold blue'
    SUCCESS: str = 'bold green'
    WARNING: str = 'bold yellow'
    ERROR:   str = 'bold red'
    TITLE:   str = 'bold purple'

class Messages:
    '''Сlass for working with localized messages.'''
    def __init__(self) -> None:
        self.locale_path = make_locale_path(app_data.get('current_locale'))

        self.messages: dict[str, str] = {}

        try:
            with open(self.locale_path, 'r', encoding = 'utf-8') as locales_file:
                self.messages = json.load(locales_file)
        
        except (FileNotFoundError, json.JSONDecodeError) as error:
            raise Exception(f'class Messages: the localization file could not be loaded \n\n{error}')
        
    def __get_nested_message(self, parts: list[str], messages: dict[str, str]) -> str:
        '''
        `Recursively traverses parts of the path to retrieve the message`

        argument
            - parts    (list[str])      <- a list of parts of the message path.
            - messages (dict[str, str]) <- a dictionary with messages.

        @returns {message: str}            
        '''
        for part in parts:
            messages: dict[str, str] = messages.get(part, {})
            
            if not messages: return 'The message could not be found'

        return messages

    def get_message(self, message_path: str, **kwargs) -> str:
        '''
        `Extracts a localized message by message json-path, substituting the data`

        arguments
            - message_path (str) <- the path to the message in the localization file
            - **kwargs           <- parameters for substitution in the message

        @returns {formated_message: str}
        '''
        message: str = self.__get_nested_message(message_path.split('.'), self.messages)

        return message.format(**kwargs)
    
t = Messages().get_message