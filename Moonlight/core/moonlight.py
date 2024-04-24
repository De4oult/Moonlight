from filelock import FileLock

import json

from Moonlight.core.tools    import check_path_exist, get_filename_from_path, generate_uuid
from Moonlight.core.paths    import make_database_path, make_logging_path
from Moonlight.config.config import config, app_data
from Moonlight.core.methods  import Methods
from Moonlight.core.logger   import Logger, LogLevel
from Moonlight.core.messages import t


def init_database(path: str):
    if check_path_exist(path): return

    with open(path, 'w', encoding = 'utf-8') as database_file: 
        json.dump(app_data.get('base_database_data'), database_file, indent = 4)

class Moonlight:
    '''Moonlight json database class'''
    def __init__(self, filename: str, author: str = app_data.get('self_admin')) -> None:
        '''
        arguments
            - filename (str) <- relative path to database .json-file
            - author   (str) <- creator of database
        '''
        self.filename: str  = make_database_path(filename)
        self.logs_path: str = make_logging_path(filename)
        self.name: str      = get_filename_from_path(self.filename)
        
        init_database(self.filename)

        Methods.create_database(self.name, self.filename, self.logs_path, author)

        self.__primary_key = 'id'
        self.lock          = FileLock(f'{self.filename}.lock')

        self.logger: Logger = Logger(self.logs_path, [LogLevel[level.upper()] for level in config.get('loggers') if level.upper() in LogLevel.__members__]) 
        
        self.logger.write(t('loggers.info', 'database_connect'), LogLevel.INFO)

    def __get_id(self) -> int:           return int(generate_uuid())
    def __cast_id(self, id: int) -> int: return int(id)
    def __get_load_func(self):           return json.load
    def __get_dump_func(self):           return json.dump

    # Database methods hier
    async def push(self, data_to_push: dict[str, any]) -> int | None:
        '''
        Adds an object with the given fields to the database

        arguments
            - data_to_push (dict[str, any]) <- the key-value dictionary to be added to the database

        @returns {id: int}.
        '''
        if type(data_to_push) != type({}): 
            self.logger.write(t('loggers.error', 'must_be_dict', command = 'PUSH', typeof = type(data_to_push)), LogLevel.ERROR)    
            return
        
        if data_to_push == {}:
            self.logger.write(t('loggers.error', 'nothing_to_push'), LogLevel.ERROR)
            
            return

        with self.lock:
            with open(self.filename, 'r+', encoding = 'utf-8') as database_file:
                database_data: dict[str, any] = self.__get_load_func()(database_file)

                data_to_push = { self.__primary_key : self.__get_id() } | data_to_push

                database_data['data'].append(data_to_push)
                database_file.seek(0)
                self.__get_dump_func()(database_data, database_file, indent = 4, ensure_ascii = False)

                self.logger.write(t('loggers.success', 'pushed', data = data_to_push), LogLevel.SUCCESS)

                return data_to_push.get(self.__primary_key)

    async def all(self) -> list[dict[str, any]]:
        '''
        Get all objects from the database

        @returns {all_objects: list[dict[str, any]]}.
        '''
        with self.lock:
            with open(self.filename, 'r', encoding = 'utf-8') as database_file:
                self.logger.write(t('loggers.success', 'get_all'), LogLevel.SUCCESS)
                
                return self.__get_load_func()(database_file).get('data')
            
    async def get(self, query: dict[str, any]) -> list[dict[str, any]] | list | None:
        '''
        Get object/s from the database by query

        arguments
            - query (dict[str, any]) <- the key-value dictionary to find in database

        @returns {object/s: list[dict[str, any]]}.
        '''
        if not isinstance(query, dict): 
            self.logger.write(t('loggers.error', 'must_be_dict', command = 'GET', typeof = type(query)), LogLevel.ERROR)    
            return
        
        if query == {}:
            self.logger.write(t('loggers.error', 'empty_query'), LogLevel.ERROR)
            
            return

        with self.lock:
            with open(self.filename, 'r', encoding = 'utf-8') as database_file:
                database_data = self.__get_load_func()(database_file)

                result: list = []
                
                for data in database_data.get('data'):
                    if all((x in data) and (data[x] == query[x]) for x in query): result.append(data)

                if result == []:
                    self.logger.write(t('loggers.error', 'no_result', query = query), LogLevel.WARNING)
                    return []

                self.logger.write(t('loggers.success', 'get', result = result), LogLevel.SUCCESS)

                return result
            
    async def update(self, data_to_update: dict[str, any]) -> None | int:
        '''
        Update object in the database

        arguments
            - data_to_update (dict[str, any]) <- the key-value dictionary to change in object in database (`id` in `data_to_update` required!)

        @returns {id: int}.
        '''
        if type(data_to_update) != type({}): 
            self.logger.write(t('loggers.error', 'must_be_dict', command = 'UPDATE', typeof = type(data_to_update)), LogLevel.ERROR)    

            return
        
        if not data_to_update.get(self.__primary_key): 
            self.logger.write(t('loggers.error', 'id_not_specified', data = data_to_update), LogLevel.ERROR)

            return
        
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
                    self.logger.write(t('loggers.error', 'nothing_to_update', query = data_to_update), LogLevel.ERROR)
                    
                    return

                database_data['data'] = result
                database_file.seek(0)
                database_file.truncate()

                self.__get_dump_func()(database_data, database_file, indent = 4, ensure_ascii = False)

                self.logger.write(t('loggers.success', 'updated', result = result), LogLevel.SUCCESS)

                return data_to_update.get(self.__primary_key)

    async def delete(self, id: int) -> dict[str, any]:
        '''
        Remove object from the database

        arguments
            - id (int) <- primary key of object in database to delete

        @returns {object: dict[str, any]}.
        '''
        with self.lock:
            with open(self.filename, 'r+', encoding='utf-8') as database_file:
                database_data = self.__get_load_func()(database_file)
                data_list = database_data.get('data')
                deleted_data = next((item for item in data_list if item.get(self.__primary_key) == self.__cast_id(id)), None)

                if not deleted_data:
                    self.logger.write(t('loggers.error', 'id_not_found', id = id), LogLevel.ERROR)
                    return None
                
                database_data['data'] = [item for item in data_list if item.get(self.__primary_key) != self.__cast_id(id)]
                database_file.seek(0)
                database_file.truncate()
                self.__get_dump_func()(database_data, database_file, indent = 4, ensure_ascii = False)
                self.logger.write(t('loggers.success', 'deleted', id = id), LogLevel.SUCCESS)
                return deleted_data

            
    async def drop(self) -> None:
        '''
        Removes database file
        '''
        self.logger.write(t('loggers.info', 'database_drop'), LogLevel.INFO)
        self.logger.stop()

        Methods.delete_database(get_filename_from_path(self.filename), self.filename, self.logs_path)


    # Tools
    async def contains(self, key: str, value: any) -> bool:
        '''
        Checks if database contains `key` where `value`

        arguments
            - key   (str)
            - value (any)

        @returns {contains: bool}.
        '''
        query = { key : value}
        
        with self.lock:
            with open(self.filename, 'r', encoding = 'utf-8') as database_file:
                database_data = self.__get_load_func()(database_file)
                
                for data in database_data.get('data'):
                    if all((x in data) and (data[x] == query[x]) for x in query): return True

                return False
    
    async def length(self) -> int:
        '''
        Returns count of objects in database

        @returns {length: int}.
        '''
        return len(await self.all())

    async def count(self, key: str, value: any) -> int:
        '''
        Returns count of objects in database where `key` is `value`

        arguments
            - key   (str)
            - value (any)

        @returns {count: int}.
        '''
        query = { key : value}
        
        with self.lock:
            with open(self.filename, 'r', encoding = 'utf-8') as database_file:
                database_data = self.__get_load_func()(database_file)

                count: int = 0
                
                for data in database_data.get('data'):
                    if all((x in data) and (data[x] == query[x]) for x in query):
                        count += 1

                return count