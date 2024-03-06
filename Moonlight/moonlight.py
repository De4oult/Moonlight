from filelock import FileLock
from uuid     import uuid4 

import json
import os

import asyncio

EMPTY: dict[str, list] = {
    'data' : []
}

def init_database(filename: str, need_create_file: bool = True):
    if not filename.endswith('.json'): 
        filename += '.json'
    
    if not need_create_file or os.path.exists('filename'): return

    with open(filename, 'w', encoding = 'utf-8') as database_file:
        json.dump(EMPTY, database_file, indent = 4)


class Moonlight:
    def __init__(self, filename: str, primary_key: str = 'id') -> None:
        init_database(filename, need_create_file = False)

        self.__primary_key = primary_key
        self.filename      = filename
        self.lock          = FileLock(f'{self.filename}.lock')

    def __get_id(self) -> int:           return int(str(uuid4().int)[:14])
    def __cast_id(self, id: int) -> int: return int(id)
    def __get_load_func(self):           return json.load
    def __get_dump_func(self):           return json.dump

    # Database methods hier
    async def push(self, data_to_push: dict[str, any]) -> int:
        with self.lock:
            with open(self.filename, 'r+', encoding = 'utf-8') as database_file:
                database_data: dict[str, any] = self.__get_load_func()(database_file)

                data_to_push = { self.__primary_key : self.__get_id() } | data_to_push

                database_data['data'].append(data_to_push)
                database_file.seek(0)
                self.__get_dump_func()(database_data, database_file, indent = 4, ensure_ascii = False)

                return data_to_push[self.__primary_key]

    async def all(self) -> list[dict[str, any]]:
        with self.lock:
            with open(self.filename, 'r', encoding = 'utf-8') as database_file:
                return self.__get_load_func()(database_file)['data']
            
    async def get(self, query: dict[str, any]) -> list[dict[str, any]]:
        if not query:
                    ... # throw Error

        with self.lock:
            with open(self.filename, 'r', encoding = 'utf-8') as database_file:
                database_data = self.__get_load_func()(database_file)

                result: list = []
                
                for data in database_data.get('data'):
                    if all((x in data) and (data[x] == query[x]) for x in query):
                        result.append(data)

                return result
            
    async def update(self, data_to_update: dict[str, any]) -> int:
        if not data_to_update.get(self.__primary_key): return -1
        
        with self.lock:
            with open(self.filename, 'r+', encoding = 'utf-8') as database_file:
                database_data = self.__get_load_func()(database_file)
                result: list  = []
                updated: bool = False

                for data in database_data.get('data'):
                    if data.get(self.__primary_key) == self.__cast_id(data_to_update.get(self.__primary_key)):
                        data.update(data_to_update)
                        updated = True

                    result.append(data)

                if not updated:
                    print('nothing to update')
                    return -1

                database_data['data'] = result
                database_file.seek(0)
                database_file.truncate()

                self.__get_dump_func()(database_data, database_file, indent = 4, ensure_ascii = False)

                return data_to_update.get(self.__primary_key)

    async def delete(self, id: int) -> dict[str, any]:
        with self.lock:
            with open(self.filename, 'r+', encoding = 'utf-8') as database_file:
                database_data = self.__get_load_func()(database_file)
                result: list  = []
                founded: bool = False

                deleted_data: dict[str, any] = None

                for data in database_data.get('data'):
                    if data.get(self.__primary_key) == self.__cast_id(id): 
                        deleted_data = data
                        founded = True

                    else: result.append(data)

                if not founded:
                    print('nothing to delete')
                    return
                
                database_data['data'] = result
                database_file.seek(0)
                database_file.truncate()

                self.__get_dump_func()(database_data, database_file, indent = 4, ensure_ascii = False)

                return deleted_data
            
    async def drop(self) -> None:
        with self.lock:
            with open(self.filename, 'w', encoding = 'utf-8') as database_file:
                json.dump(EMPTY, database_file, indent = 4)

import time

async def main():
    database = Moonlight('test.json')

    await database.push({
        'name' : 'Oleg',
        'age'  : 20
    })

    time.sleep(2)

    persons = await database.get({
        'name' : 'Oleg'
    })

    print(persons)

    time.sleep(2)

    id = await database.update({
        'id'   : persons[0].get('id'),
        'name' : 'Peter'
    })

    time.sleep(2)

    await database.delete(id)

    await database.drop()

asyncio.run(main = main())