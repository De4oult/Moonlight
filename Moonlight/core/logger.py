from loguru import logger
from enum   import Enum

from Moonlight.core.tools import check_path_exist


class LogLevel(Enum):
    '''Enum of logging levels'''
    INFO:    str = 'INFO'
    SUCCESS: str = 'SUCCESS'
    WARNING: str = 'WARNING'
    ERROR:   str = 'ERROR'

class Logger:
    '''Class for logging basic actions in the database, based on the loguru library'''
    def __init__(self, path: str, loggers: tuple[LogLevel]) -> None:
        '''
        `Initializes the logger, creates a log file in the specified path and adjusts its formatting.`

        arguments
            - path    (str)   <- the path to the log file
            - loggers (tuple) <- tuple of logging levels that will be written to the file
        '''
        self.path: str = path
        self.loggers: tuple[LogLevel] = loggers

        check_path_exist(self.path)

        self.logger = logger

        self.logger.remove()
        self.logger.add(
            self.path,
            format = '[{time:DD.MM.YYYY HH:mm:ss}] <{level}> -> {message}',
            level  = 'INFO'
        )
        

    def write(self, content: str, level: LogLevel) -> None:
        '''
        `Writes the message to the log.`

        arguments
            - content (str)      <- the text of the message for logging
            - level   (LogLevel) <- the logging level at which the message should be recorded
        '''
        if level in self.loggers: 
            self.logger.log(level.value, content)

    def stop(self) -> None:
        '''Removes all handlers from the logger'''
        self.logger.remove()
