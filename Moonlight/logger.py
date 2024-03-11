from filelock import FileLock
from datetime import datetime
from colorama import Fore, Style

import os

def init_log(filename: str):    
    if os.path.exists(filename): return

    full_dir = ''

    for directory in filename.split('/')[0:-1]:
        full_dir += directory

        if os.path.exists(full_dir): continue
        
        os.mkdir(full_dir)

    log_file = open(filename, 'w', encoding = 'utf-8')
    log_file.close()

class Logger:
    def __init__(self, database: str, show_messages: tuple[str]) -> None:
        self.database      = database.rstrip('.json')
        self.filename      = 'logs/%s-%s.txt' % (self.database, datetime.now().strftime('%d-%m-%Y'))
        
        self.lock          = FileLock(f'{self.filename}.lock')
        self.show_messages = show_messages

        init_log(self.filename)

    async def write(self, text: str, type: str):
        with self.lock:
            with open(self.filename, 'a', encoding = 'utf-8') as log_file:
                match type:
                    case 'success':  
                        message_string = '[%s] ::Success:: %s\n' % (datetime.now().strftime('%H:%M:%S'), text)
                        log_file.write(message_string + '\n' + '_' * len(message_string) + '\n')
                        if type in self.show_messages: print(Fore.GREEN  + f'Success: {text}' + Style.RESET_ALL)
                    
                    case 'info': 
                        message_string = '[%s] ::Info   :: %s\n' % (datetime.now().strftime('%H:%M:%S'), text)
                        log_file.write(message_string + '\n' + '_' * len(message_string) + '\n')
                        if type in self.show_messages: print(Fore.BLUE   + f'Info: {text}' + Style.RESET_ALL)
                    
                    case 'warning': 
                        message_string = '[%s] ::Warning:: %s\n' % (datetime.now().strftime('%H:%M:%S'), text)
                        log_file.write(message_string + '\n' + '_' * len(message_string) + '\n')
                        if type in self.show_messages: print(Fore.YELLOW + f'Warning: {text}' + Style.RESET_ALL)
                    
                    case 'error':  
                        message_string = '[%s] ::Error  :: %s\n' % (datetime.now().strftime('%H:%M:%S'), text)
                        log_file.write(message_string + '\n' + '_' * len(message_string) + '\n')
                        if type in self.show_messages: print(Fore.RED    + f'Error: {text}' + Style.RESET_ALL)
                    
                    case _: return