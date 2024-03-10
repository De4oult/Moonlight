from filelock import FileLock
from datetime import datetime

import asyncio

import os

def init_log(filename: str):    
    if os.path.exists(filename): return

    log_file = open(filename, 'w', encoding = 'utf-8')
    log_file.close()

class Logger:
    def __init__(self, database: str) -> None:
        self.database = database.rstrip('.json')
        self.filename = '%s-%s.txt' % (self.database, datetime.now().strftime('%d-%m-%Y'))
        self.lock     = FileLock(f'{self.filename}.lock')

        init_log(self.filename)

    async def write(self, message):
        with self.lock:
            with open(self.filename, 'a', encoding = 'utf-8') as log_file:
                log_file.write('[%s] %s\n' % (datetime.now().strftime('%H:%M:%S'), message))

        return message


# async def main():
#     logger = Logger('test.json')
#     await logger.write('Тестовое сообщение 1')
#     await logger.write('Тестовое сообщение 2')

# if __name__ == '__main__':
#     asyncio.run(main = main())