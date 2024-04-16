from Moonlight.styles import Style
from Moonlight.tools  import check_path_exist, get_now_datetime

from rich.console import Console

console = Console()

class Logger:
    def __init__(self, path: str, loggers: tuple[str]) -> None:
        self.path: str = path
        self.loggers: tuple[str] = loggers

        check_path_exist(self.path)

    def write(self, content: str, logger: str) -> None:
        if logger not in self.loggers: return

        header:  str = f'[{get_now_datetime()}] <{logger.upper()}>'
        content: str = f'\n-> {content}'

        console.rule(f'[{Style[logger].value}]' + header, style = Style[logger].value, align = 'left')
        console.print(content, style = Style[logger].value)

        with open(self.path, 'a+', encoding = 'utf-8') as logging_file: logging_file.write(f'{header}\n{content}\n\n')

if __name__ == '__main__':
    logger = Logger('E:\\Документы\\Программирование\\Moonlight\\logs\\test.log', ['success', 'info'])

    logger.write('DASDASD', 'info')