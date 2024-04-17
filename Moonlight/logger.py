from Moonlight.tools  import check_path_exist

from loguru import logger

class Logger:
    def __init__(self, path: str, loggers: tuple[str]) -> None:
        self.path: str = path
        self.loggers: tuple[str] = loggers

        check_path_exist(self.path)

        self.logger = logger

        self.logger.remove()
        self.logger.add(
            self.path,
            format = '[{time:DD.MM.YYYY HH:mm:ss}] <{level}> -> {message}',
            level  = 'INFO'
        )
        

    def write(self, content: str, logger: str) -> None:
        if logger in self.loggers: self.logger.log(logger.upper(), content)

    def stop(self) -> None:
        self.logger.remove()
