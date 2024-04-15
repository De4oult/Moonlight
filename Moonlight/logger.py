from loguru import logger
from tools  import check_path_exist

class Logger:
    def __init__(self, filename: str, show_messages: tuple[str]) -> None:
        self.filename = filename
        self.show_messages = show_messages

        check_path_exist(self.filename)

        logger.remove()
        logger.add(
            self.filename, 
            format='<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> [<level>{level}</level>] \n\t<b>{message}</b>',
            level='DEBUG'
        )
        
        # logger.add(
        #     self.filter_show_messages,
        #     format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS zz}</green> [<level>{level: <8}</level>] \n <yellow>Line {line: >4} ({file}):</yellow> <b>{message}</b>",
        #     level="DEBUG"
        # )
    
    # def filter_show_messages(self, record):
    #     return record['level'].name.lower() in self.show_messages

    async def write(self, text: str, type: str) -> None:
        getattr(logger, type.lower())(text)

    def stop(self) -> None:
        logger.remove()