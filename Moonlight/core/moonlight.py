from filelock import FileLock
from typing   import Any
from enum     import Enum

import json

from Moonlight.core.tools    import check_path_exist, get_filename_from_path, generate_uuid
from Moonlight.core.paths    import make_database_path, make_logging_path
from Moonlight.config.config import config, app_data
from Moonlight.core.methods  import Methods
from Moonlight.core.logger   import Logger, LogLevel
from Moonlight.core.messages import t


def init_database(path: str) -> None:
    if check_path_exist(path): return None

    with open(path, 'w', encoding = 'utf-8') as database_file: 
        json.dump(app_data.get('base_database_data'), database_file, indent = 4)

class Operations(Enum):
    PUSH:     str = 'PUSH'
    ALL:      str = 'ALL'
    GET:      str = 'GET'
    UPDATE:   str = 'UPDATE'
    DELETE:   str = 'DELETE'
    DROP:     str = 'DROP'
    CONTAINS: str = 'CONTAINS'
    LENGTH:   str = 'LENGTH'
    COUNT:    str = 'COUNT'

class Moonlight:
    '''Moonlight json database class'''
    def __init__(self, filename: str, author: str = app_data.get('self_admin'), console_show: bool = True) -> None:
        '''
        arguments
            - filename (str) <- relative path to database .json-file
            - author   (str) <- creator of database
        '''
        self.filename:  str = make_database_path(filename)
        self.logs_path: str = make_logging_path(filename)
        self.name:      str = get_filename_from_path(self.filename)
        
        init_database(self.filename)

        Methods.create_database(self.name, self.filename, self.logs_path, author)

        self.__primary_key: str = 'id'

        self.lock = FileLock(f'{self.filename}.lock')

        self.log_levels: list[LogLevel] = [LogLevel[level.upper()] for level in config.get('loggers') if level.upper() in LogLevel.__members__]
        self.logger: Logger = Logger(self.logs_path, self.log_levels, console_show) 
        
        self.logger.write(t('loggers.info.database_connect', name = app_data.get('name')), LogLevel.INFO)

    def __get_id(self) -> int:           return int(generate_uuid())
    def __cast_id(self, id: int) -> int: return int(id)
    def __get_load_func(self):           return json.load
    def __get_dump_func(self):           return json.dump
    def __truncate(self, file) -> None:
        file.seek(0)
        file.truncate()
    

    async def push(self, query: dict[str, Any]) -> int | None:
        '''
        `Adds an object with the given fields to the database`

        arguments
            - query (dict[str, any]) <- the key-value dictionary to be added to the database

        @returns {id: int}
        '''
        if not isinstance(query, dict): 
            self.logger.write(t('loggers.error.must_be_dict', typeof = type(query), operation = Operations.PUSH.value), LogLevel.ERROR)    
            return None
        
        if not query:
            self.logger.write(t('loggers.error.empty_query', operation = Operations.PUSH.value), LogLevel.ERROR)
            return None

        with self.lock:
            try:
                with open(self.filename, 'r+', encoding = 'utf-8') as database_file:
                    database_data: dict[str, list] = self.__get_load_func()(database_file)

                    identifier: int = self.__get_id()
                    query: dict[str, Any] = { self.__primary_key : identifier, **query }

                    database_data['data'].append(query)

                    self.__truncate(database_file)

                    self.__get_dump_func()(database_data, database_file, indent = 4, ensure_ascii = False)

                    self.logger.write(t('loggers.success.completed', result = query, operation = Operations.PUSH.value), LogLevel.SUCCESS)

                    return identifier
            
            except Exception as error:
                self.logger.write(t('loggers.error.operation_failed', error = error, operation = Operations.PUSH.value), LogLevel.ERROR)
                return None

    async def all(self) -> list[dict[str, Any] | None]:
        '''
        `Get all objects from the database`

        @returns {all_objects: list[dict[str, any]]}
        '''
        with self.lock:
            try: 
                with open(self.filename, 'r', encoding = 'utf-8') as database_file:
                    database_data: dict[str, list] = self.__get_load_func()(database_file)
                    data: list[dict[str, Any]]     = database_data.get('data', [])
                    
                    self.logger.write(t('loggers.success.get_all', operation = Operations.ALL.value), LogLevel.SUCCESS)
                    
                    return data
                
            except Exception as error:
                self.logger.write(t('loggers.error.operation_failed', error = error, operation = Operations.ALL.value), LogLevel.ERROR)
                return []

    async def get(self, query: dict[str, Any]) -> list[dict[str, Any] | None] | None:
        '''
        `Get object/s from the database by query`

        arguments
            - query (dict[str, any]) <- the key-value dictionary to find in database

        @returns {object/s: list[dict[str, any]]}
        '''
        if not isinstance(query, dict): 
            self.logger.write(t('loggers.error.must_be_dict', typeof = type(query), operation = Operations.GET.value), LogLevel.ERROR)    
            return None
        
        if not query:
            self.logger.write(t('loggers.error.empty_query', operation = Operations.GET.value), LogLevel.ERROR)
            return None

        with self.lock:
            try:
                with open(self.filename, 'r', encoding = 'utf-8') as database_file:
                    database_data: dict[str, list] = self.__get_load_func()(database_file)

                    result: list = [data for data in database_data.get('data', []) if all(data.get(key) == value for key, value in query.items())]
                    
                    if not result: self.logger.write(t('loggers.warning.no_matches', query = query,   operation = Operations.GET.value), LogLevel.WARNING)
                    else:          self.logger.write(t('loggers.success.completed',  result = result, operation = Operations.GET.value), LogLevel.SUCCESS)

                    return result
            
            except Exception as error:
                self.logger.write(t('loggers.error.operation_failed', error = error, operation = Operations.GET.value), LogLevel.ERROR)
                return None

    async def update(self, query: dict[str, Any]) -> None | int:
        '''
        `Update object in the database`

        arguments
            - data_to_update (dict[str, any]) <- the key-value dictionary to change in object in database (`id` in `data_to_update` required!)

        @returns {id: int}
        '''
        if not isinstance(query, dict): 
            self.logger.write(t('loggers.error.must_be_dict', typeof = type(query), operation = Operations.UPDATE.value), LogLevel.ERROR)    
            return None
        
        if self.__primary_key not in query: 
            self.logger.write(t('loggers.error.id_not_specified', query = query, operation = Operations.UPDATE.value), LogLevel.ERROR)
            return None
        
        with self.lock:
            try:
                with open(self.filename, 'r+', encoding = 'utf-8') as database_file:
                    database_data: dict[str, list] = self.__get_load_func()(database_file)
                    data: list[dict[str, Any]]     = database_data.get('data', [])

                    updated: bool = False

                    for index, item in enumerate(data):
                        if item.get(self.__primary_key) == self.__cast_id(query.get(self.__primary_key)):
                            data[index].update(query)
                            updated = True

                    print(updated)

                    if not updated:
                        self.logger.write(t('loggers.error.nothing_to_update', query = query, operation = Operations.UPDATE.value), LogLevel.ERROR)
                        return None

                    self.__truncate(database_file)

                    self.__get_dump_func()(database_data, database_file, indent = 4, ensure_ascii = False)

                    print('ok')

                    self.logger.write(t('loggers.success.completed', result = query, operation = Operations.UPDATE.value), LogLevel.SUCCESS)

                    return query.get(self.__primary_key)
                
            except Exception as error:
                self.logger.write(t('loggers.error.operation_failed', error = error, operation = Operations.UPDATE.value), LogLevel.ERROR)
                return None

    async def delete(self, id: int) -> dict[str, Any] | None:
        '''
        `Remove object from the database`

        arguments
            - id (int) <- primary key of object in database to delete

        @returns {object: dict[str, any]}
        '''
        if not isinstance(id, int):
            self.logger.write(t('loggers.error.id_must_be_int', id = id, operation = Operations.DELETE.value), LogLevel.ERROR)
            return None

        with self.lock:
            try:
                with open(self.filename, 'r+', encoding = 'utf-8') as database_file:
                    database_data: dict[str, list] = self.__get_load_func()(database_file)
                    data: list[dict[str, Any]]     = database_data.get('data', [])

                    deleted_item: dict[str, Any] | None = next((item for item in data if item.get(self.__primary_key) == self.__cast_id(id)), None)

                    if not deleted_item:
                        self.logger.write(t('loggers.error.id_not_found', id = id, operation = Operations.DELETE.value), LogLevel.ERROR)
                        return None
                    
                    database_data['data'] = [item for item in data if item.get(self.__primary_key) != self.__cast_id(id)]
                    
                    self.__truncate(database_file)
                    
                    self.__get_dump_func()(database_data, database_file, indent = 4, ensure_ascii = False)
                    
                    self.logger.write(t('loggers.success.deleted', id = id, operation = Operations.DELETE.value), LogLevel.SUCCESS)
                    
                    return deleted_item
            
            except Exception as error:
                self.logger.write(t('loggers.error.operation_failed', error = error, operation = Operations.DELETE.value), LogLevel.ERROR)
                return None
            
    async def drop(self) -> None:
        '''`Removes database file`'''
        try:
            self.lock.acquire()
            self.logger.stop()

            Methods.delete_database(self.name, self.filename, self.logs_path)
            
            self.logger.write(t('loggers.info.database_drop', operation = Operations.DROP.value), LogLevel.INFO)
                
        except Exception as error:
            self.logger.write(t('loggers.error.operation_failed', error = error, operation = Operations.DROP.value), LogLevel.ERROR)

        finally:
            self.lock.release()

    async def contains(self, key: str, value: Any) -> bool:
        '''
        `Checks if database contains key where value`

        arguments
            - key   (str)
            - value (any)

        @returns {contains: bool}
        '''
        try:
            with self.lock:
                with open(self.filename, 'r', encoding = 'utf-8') as database_file:
                    database_data: dict[str, list] = self.__get_load_func()(database_file)
                    data: list[dict[str, Any]]     = database_data.get('data', [])

                    return any(record.get(key) == value for record in data)
        
        except Exception as error:
            self.logger.write(t('loggers.error.operation_failed', error = error, operation = Operations.CONTAINS.value), LogLevel.ERROR)
            return False
    
    async def length(self) -> int:
        '''
        `Returns count of objects in database`

        @returns {length: int}
        '''
        try:
            return len(await self.all())
        
        except Exception as error:
            self.logger.write(t('loggers.error.operation_failed', error = error, operation = Operations.LENGTH.value), LogLevel.ERROR)
            return 0

    async def count(self, key: str, value: Any) -> int:
        '''
        `Returns count of objects in database where key is value`

        arguments
            - key   (str)
            - value (any)

        @returns {count: int}
        '''
        try:
            with self.lock:
                with open(self.filename, 'r', encoding = 'utf-8') as database_file:
                    database_data: dict[str, list] = self.__get_load_func()(database_file)
                    data: list[dict[str, Any]]     = database_data.get('data', [])

                    return sum(1 for record in data if data.get(key) == value) 
                
        except Exception as error:
            self.logger.write(t('loggers.error.operation_failed', error = error, operation = Operations.COUNT.value), LogLevel.ERROR)
            return 0