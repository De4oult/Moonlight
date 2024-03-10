from filelock import FileLock
from datetime import datetime
from colorama import Fore, Style

import os

def init_log(filename: str):    
    if os.path.exists(filename): return

    log_file = open(filename, 'w', encoding = 'utf-8')
    log_file.close()

class Logger:
    def __init__(self, database: str, show_messages: tuple[str]) -> None:
        self.database      = database.rstrip('.json')
        self.filename      = '%s-%s.txt' % (self.database, datetime.now().strftime('%d-%m-%Y'))
        
        self.lock          = FileLock(f'{self.filename}.lock')
        self.show_messages = show_messages

        init_log(self.filename)

    async def write(self, text: str, type: str):
        with self.lock:
            with open(self.filename, 'a', encoding = 'utf-8') as log_file:
                log_file.write('[%s] %s\n' % (datetime.now().strftime('%H:%M:%S'), text))
                # set type of message

        if not type in self.show_messages: return

        match type:
            case 'suc':  print(Fore.GREEN  + f'Success: {text}' + Style.RESET_ALL)
            case 'info': print(Fore.BLUE   + f'Info: {text}' + Style.RESET_ALL)
            case 'warn': print(Fore.YELLOW + f'Warning: {text}' + Style.RESET_ALL)
            case 'err':  print(Fore.RED    + f'Error: {text}' + Style.RESET_ALL)
            case _: return