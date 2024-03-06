from colorama import Fore, Style

class Message:
    """
    class Message used to issue messages:
        success
        warnings
        errors

    message(text, type)
    """
    def __init__(self, text: str, type: str) -> None:
        self.text = text
        self.type = type

    def __call__(self) -> None:
        match self.type:
            case 'suc':  print(Fore.GREEN  + f'Success: {self.text}' + Style.RESET_ALL)
            case 'warn': print(Fore.YELLOW + f'Warning: {self.text}' + Style.RESET_ALL)
            case 'err':  print(Fore.RED    +   f'Error: {self.text}' + Style.RESET_ALL)
            case _: return