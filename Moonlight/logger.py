from loguru import logger
import os

def init_log(path: str):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)

class Logger:
    def __init__(self, filename: str, show_messages: tuple[str]) -> None:
        self.filename = filename
        self.show_messages = show_messages

        init_log(self.filename)

        logger.remove()
        logger.add(
            self.filename, 
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS zz}</green> [<level>{level: <8}</level>] \n <yellow>Line {line: >4} ({file}):</yellow> <b>{message}</b>",
            level="DEBUG"
        )
        
        logger.add(
            self.filter_show_messages,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS zz}</green> [<level>{level: <8}</level>] \n <yellow>Line {line: >4} ({file}):</yellow> <b>{message}</b>",
            level="DEBUG"
        )
    
    def filter_show_messages(self, record):
        return record["level"].name.lower() in self.show_messages

    async def write(self, text: str, type: str):
        getattr(logger, type.lower())(text)
