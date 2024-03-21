from filelock import FileLock
from datetime import datetime
from colorama import Fore, Style
from tools    import get_now_datetime

import os

def init_log(path: str):
    if not os.path.exists(path): os.makedirs('\\'.join(path.split('\\')[0:-2]), exist_ok = True)

    with open(path, 'a', encoding = 'utf-8') as logs_file:
        logs_file.write('[%s] Database connected\n' % get_now_datetime())

class Logger:
    def __init__(self, filename: str, show_messages: tuple[str]) -> None:
        self.filename = filename
        
        self.lock          = FileLock(f'{self.filename}.lock')
        self.show_messages = show_messages

        init_log(self.filename)

    async def write(self, text: str, type: str):
        with self.lock:
            with open(self.filename, 'a', encoding = 'utf-8') as log_file:
                match type:
                    case 'success':  
                        message_string = '[%s] ::Success:: %s\n' % (get_now_datetime(), text)
                        log_file.write(message_string + '\n' + '_' * len(message_string) + '\n')
                        if type in self.show_messages: print(Fore.GREEN  + f'Success: {text}' + Style.RESET_ALL)
                    
                    case 'info': 
                        message_string = '[%s] ::Info   :: %s\n' % (get_now_datetime(), text)
                        log_file.write(message_string + '\n' + '_' * len(message_string) + '\n')
                        if type in self.show_messages: print(Fore.BLUE   + f'Info: {text}' + Style.RESET_ALL)
                    
                    case 'warning': 
                        message_string = '[%s] ::Warning:: %s\n' % (get_now_datetime(), text)
                        log_file.write(message_string + '\n' + '_' * len(message_string) + '\n')
                        if type in self.show_messages: print(Fore.YELLOW + f'Warning: {text}' + Style.RESET_ALL)
                    
                    case 'error':  
                        message_string = '[%s] ::Error  :: %s\n' % (get_now_datetime(), text)
                        log_file.write(message_string + '\n' + '_' * len(message_string) + '\n')
                        if type in self.show_messages: print(Fore.RED    + f'Error: {text}' + Style.RESET_ALL)
                    
                    case _: return