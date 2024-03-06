from filelock import FileLock
from uuid     import uuid4 

from Moonlight.messages import Message

import json
import os

EMPTY: dict[str, list] = {
    'data' : []
}

def init_database(filename: str):
    if not filename.endswith('.json'): 
        filename += '.json'
    
    if os.path.exists(filename): return

    with open(filename, 'w', encoding = 'utf-8') as database_file:
        json.dump(EMPTY, database_file, indent = 4)


class Moonlight:
    def __init__(self, filename: str, primary_key: str = 'id', show_messages: tuple = ('warning', 'error')) -> None:
        """
        
        """
        init_database(filename)

        self.__primary_key = primary_key
        self.filename      = filename
        self.lock          = FileLock(f'{self.filename}.lock')
        self.show_messages = show_messages

    def __get_id(self) -> int:           return int(str(uuid4().int)[:14])
    def __cast_id(self, id: int) -> int: return int(id)
    def __get_load_func(self):           return json.load
    def __get_dump_func(self):           return json.dump

    # Database methods hier
    async def push(self, data_to_push: dict[str, any]) -> int:
        if data_to_push == {}:
            if 'error' in self.show_messages: Message(f'Nothing to push [from `{self.filename}`: push({data_to_push})] \n\n>>> Query is empty', 'err')()
            
            return -1

        with self.lock:
            with open(self.filename, 'r+', encoding = 'utf-8') as database_file:
                database_data: dict[str, any] = self.__get_load_func()(database_file)

                data_to_push = { self.__primary_key : self.__get_id() } | data_to_push

                database_data['data'].append(data_to_push)
                database_file.seek(0)
                self.__get_dump_func()(database_data, database_file, indent = 4, ensure_ascii = False)

                if 'success' in self.show_messages: Message(f'Pushed [from `{self.filename}`: push({data_to_push})]', 'suc')()

                return data_to_push[self.__primary_key]

    async def all(self) -> list[dict[str, any]]:
        with self.lock:
            with open(self.filename, 'r', encoding = 'utf-8') as database_file:
                if 'success' in self.show_messages: Message(f'Returned [from `{self.filename}`: all()]', 'suc')()
                
                return self.__get_load_func()(database_file)['data']
            
    async def get(self, query: dict[str, any]) -> list[dict[str, any]]:
        if query == {}:
            if 'error' in self.show_messages: Message(f'No query [from `{self.filename}`: get({query})] \n\n>>> Query is empty', 'err')()
            
            return []

        with self.lock:
            with open(self.filename, 'r', encoding = 'utf-8') as database_file:
                database_data = self.__get_load_func()(database_file)

                result: list = []
                
                for data in database_data.get('data'):
                    if all((x in data) and (data[x] == query[x]) for x in query):
                        result.append(data)

                if result == []:
                    if 'error' in self.show_messages: Message(f'Nothing to get [from `{self.filename}`: get({query})] \n\n>>> No element with {query}', 'err')()
                    return []

                if 'success' in self.show_messages: Message(f'Returned [from `{self.filename}`: get({query})]', 'suc')()

                return result
            
    async def update(self, data_to_update: dict[str, any]) -> int:
        if not data_to_update.get(self.__primary_key): 
            if 'error' in self.show_messages: Message(f'{self.__primary_key} not specified [from `{self.filename}`: update({data_to_update})] \n\n>>> No `{self.__primary_key}` in {data_to_update}', 'err')()
            
            return -1
        
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
                    if 'err' in self.show_messages: Message(f'Nothing to update [from `{self.filename}`: update({data_to_update})] \n\n>>> Element with {self.__primary_key}=`{data_to_update.get(self.__primary_key)}` was not found', 'err')()
                    
                    return -1

                database_data['data'] = result
                database_file.seek(0)
                database_file.truncate()

                self.__get_dump_func()(database_data, database_file, indent = 4, ensure_ascii = False)

                if 'success' in self.show_messages: Message(f'Updated [from `{self.filename}`: update({data_to_update})', 'suc')()

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
                    if 'error' in self.show_messages: Message(f'Nothing to delete [from `{self.filename}`: delete({id})] \n\n>>> Element with {self.__primary_key}=`{id}` was not found', 'err')()
                    
                    return
                
                database_data['data'] = result
                database_file.seek(0)
                database_file.truncate()

                self.__get_dump_func()(database_data, database_file, indent = 4, ensure_ascii = False)

                if 'success' in self.show_messages: Message(f'Deleted [from `{self.filename}`: delete({id})', 'suc')()

                return deleted_data
            
    async def drop(self) -> None:
        with self.lock:
            with open(self.filename, 'w', encoding = 'utf-8') as database_file:
                if 'success' in self.show_messages: Message(f'Database drop [from `{self.filename}`: drop()', 'suc')()

                json.dump(EMPTY, database_file, indent = 4)