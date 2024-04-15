from filelock import FileLock
from uuid     import uuid4

from Moonlight.logger import Logger
from Moonlight.paths  import make_database_path, make_logging_path
from Moonlight.tools  import strip_ext, check_path

import json
import os

EMPTY: dict[str, list] = {
    'data' : []
}

def init_database(path: str): 
    with open(check_path(path), 'w', encoding = 'utf-8') as database_file: 
        json.dump(EMPTY, database_file, indent = 4)

class Moonlight:
    """
        class Moonlight
        
        arguments
            - filename      (str)        <- relative path to database .json-file
            - primary_key   (str)        <- primary key name (default: 'id') 
            - show_messages (tuple[str]) <- tuple of messages that will be output during operation (default: ('warning', 'error'))
                * 'success'
                * 'info'
                * 'warning'
                * 'error'
    """
    def __init__(self, filename: str, primary_key: str = 'id', show_messages: tuple = ('warning', 'error')) -> None:
        self.logs_path = make_logging_path(strip_ext(filename, '.json'))
        self.filename  = make_database_path(filename)
        
        init_database(self.filename)

        self.__primary_key = str(primary_key)
        self.lock          = FileLock(f'{self.filename}.lock')
        self.logger        = Logger(self.logs_path, show_messages)

    def __get_id(self) -> int:           return int(str(uuid4().int)[:14])
    def __cast_id(self, id: int) -> int: return int(id)
    def __get_load_func(self):           return json.load
    def __get_dump_func(self):           return json.dump

    # Database methods hier
    async def push(self, data_to_push: dict[str, any]) -> int:
        """
        Adds an object with the given fields to the database

        arguments
            - data_to_push (dict[str, any]) <- the key-value dictionary to be added to the database

        @returns {id: int}.
        """
        if data_to_push == {} or not data_to_push:
            await self.logger.write(f'Nothing to push [from `{self.filename}`: push({data_to_push})] \n\n>>> Query is empty', 'error')
            
            return -1

        with self.lock:
            with open(self.filename, 'r+', encoding = 'utf-8') as database_file:
                database_data: dict[str, any] = self.__get_load_func()(database_file)

                data_to_push = { self.__primary_key : self.__get_id() } | data_to_push

                database_data['data'].append(data_to_push)
                database_file.seek(0)
                self.__get_dump_func()(database_data, database_file, indent = 4, ensure_ascii = False)

                await self.logger.write(f'Pushed [from `{self.filename}`: push({data_to_push})]', 'success')

                return data_to_push.get(self.__primary_key)

    async def all(self) -> list[dict[str, any]]:
        """
        Get all objects from the database

        @returns {all_objects: list[dict[str, any]]}.
        """
        with self.lock:
            with open(self.filename, 'r', encoding = 'utf-8') as database_file:
                await self.logger.write(f'Returned [from `{self.filename}`: all()]', 'success')
                
                return self.__get_load_func()(database_file).get('data')
            
    async def get(self, query: dict[str, any]) -> list[dict[str, any]]:
        """
        Get object/s from the database by query

        arguments
            - query (dict[str, any]) <- the key-value dictionary to find in database

        @returns {object/s: list[dict[str, any]]}.
        """
        if query == {}:
            await self.logger.write(f'No query [from `{self.filename}`: get({query})] \n\n>>> Query is empty', 'error')
            
            return []

        with self.lock:
            with open(self.filename, 'r', encoding = 'utf-8') as database_file:
                database_data = self.__get_load_func()(database_file)

                result: list = []
                
                for data in database_data.get('data'):
                    if all((x in data) and (data[x] == query[x]) for x in query):
                        result.append(data)

                if result == []:
                    await self.logger.write(f'Nothing to get [from `{self.filename}`: get({query})] \n\n>>> No element with {query}', 'error')
                    return []

                await self.logger.write(f'Returned [from `{self.filename}`: get({query})]', 'success')

                return result
            
    async def update(self, data_to_update: dict[str, any]) -> int:
        """
        Update object in the database

        arguments
            - data_to_update (dict[str, any]) <- the key-value dictionary to change in object in database (`id` in `data_to_update` required!)

        @returns {id: int}.
        """
        if not data_to_update.get(self.__primary_key): 
            await self.logger.write(f'{self.__primary_key} not specified [from `{self.filename}`: update({data_to_update})] \n\n>>> No `{self.__primary_key}` in {data_to_update}', 'error')
            
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
                    await self.logger.write(f'Nothing to update [from `{self.filename}`: update({data_to_update})] \n\n>>> Element with {self.__primary_key}=`{data_to_update.get(self.__primary_key)}` was not found', 'error')
                    
                    return -1

                database_data['data'] = result
                database_file.seek(0)
                database_file.truncate()

                self.__get_dump_func()(database_data, database_file, indent = 4, ensure_ascii = False)

                await self.logger.write(f'Updated [from `{self.filename}`: update({data_to_update})', 'success')

                return data_to_update.get(self.__primary_key)

    async def delete(self, id: int) -> dict[str, any]:
        """
        Remove object from the database

        arguments
            - id (int) <- primary key of object in database to delete

        @returns {object: dict[str, any]}.
        """
        with self.lock:
            with open(self.filename, 'r+', encoding='utf-8') as database_file:
                database_data = self.__get_load_func()(database_file)
                data_list = database_data.get('data')
                deleted_data = next((item for item in data_list if item.get(self.__primary_key) == self.__cast_id(id)), None)

                if not deleted_data:
                    await self.logger.write(f'Nothing to delete [from `{self.filename}`: delete({id})] \n\n>>> Element with {self.__primary_key}=`{id}` was not found', 'error')
                    return None
                
                database_data['data'] = [item for item in data_list if item.get(self.__primary_key) != self.__cast_id(id)]
                database_file.seek(0)
                database_file.truncate()
                self.__get_dump_func()(database_data, database_file, indent = 4, ensure_ascii = False)
                await self.logger.write(f'Deleted [from `{self.filename}`: delete({id})]', 'success')
                return deleted_data

            
    async def drop(self) -> None:
        """
        Removes database file
        """
        if os.path.isfile(self.filename):
            os.remove(self.filename)

        await self.logger.write(f'Database drop [from `{self.filename}`: drop()]', 'success')


    # Tools
    async def contains(self, key: str, value: any) -> bool:
        """
        Checks if database contains `key` where `value`

        arguments
            - key   (str)
            - value (any)

        @returns {contains: bool}.
        """
        query = { key : value}
        
        with self.lock:
            with open(self.filename, 'r', encoding = 'utf-8') as database_file:
                database_data = self.__get_load_func()(database_file)
                
                for data in database_data.get('data'):
                    if all((x in data) and (data[x] == query[x]) for x in query): return True

                return False
    
    async def length(self) -> int:
        """
        Returns count of objects in database

        @returns {length: int}.
        """
        return len(await self.all())

    async def count(self, key: str, value: any) -> int:
        """
        Returns count of objects in database where `key` is `value`

        arguments
            - key   (str)
            - value (any)

        @returns {count: int}.
        """
        query = { key : value}
        
        with self.lock:
            with open(self.filename, 'r', encoding = 'utf-8') as database_file:
                database_data = self.__get_load_func()(database_file)

                count: int = 0
                
                for data in database_data.get('data'):
                    if all((x in data) and (data[x] == query[x]) for x in query):
                        count += 1

                return count