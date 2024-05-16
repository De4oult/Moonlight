from rich.console import Console

from Moonlight.config.paths      import make_moonfile_path
from Moonlight.config.config     import app_data, config
from Moonlight.core.moonlight    import Moonlight
from Moonlight.core.methods      import Methods
from Moonlight.messages.messages import t, Style


console = Console()

class Moonfile:
    '''Class for managing configuration of Moonlight database by the Moonfile'''
    def __init__(self) -> None:
        self.path: str = make_moonfile_path(app_data.get('moonfile'))
        
        self.app_config: dict[str, any] = {}

        self.databases: list = []
        self.users:     list = []
        
        self.ignore: bool = False

    def parse_config(self) -> None:
        '''
        `Parses the configuration file and executes the commands specified in it`
        
        Operations include setting up the application, logging, and creating users and databases
        '''
        with open(self.path, 'r', encoding = 'utf-8') as moonfile:
            for line in moonfile.readlines():
                parts: list[str] = line.strip().split()
                
                if not parts: continue 
                
                command: str     = parts[0].upper()
                args: list[str]  = parts[1:]

                match command:     
                    case 'PURE':        config.reinit(app_data.get('base_config'))
                    case 'APP':         self.set_app(*args)
                    case 'LOG':         self.set_logging(*args)
                    case 'CREATE_USER': self.create_user(*args)
                    case 'DATABASE':    self.create_database(*args)
                    case 'MQ':          self.create_messages_queue(*args)
                    case '?':           continue
                    case 'IGNORE':      self.ignore = True
                    case _:             console.print(t('warnings.moonfile', 'undefined_command', command = command), style = Style.WARNING.value)

    def set_app(self, *args) -> None:
        '''
        `Sets the application parameters from the configuration file`

        arguments
            *args <- a list of arguments, including the host and port
        '''
        if not args:
            console.print(t('errors.moonfile', 'no_host_app', default_port = app_data.get('base_config').get('port')), style = 'bold red')
            return
        
        host = list(filter(None, args[0].split(':')))

        self.app_config['host'] = host[0]

        if len(host) == 1: console.print(t('warnings.moonfile', 'no_port_app', default_port = app_data.get('base_config').get('port')), style = Style.WARNING.value)
        
        self.app_config['port'] = int(host[1]) if len(host) > 1 else app_data.get('base_config').get('port')

    def set_logging(self, *args) -> None:
        '''
        `Configures logging parameters`

        arguments
            *args <- a list of logging levels
        '''
        if not args:
            console.print(t('errors.moonfile', 'no_loggers_log'), style = 'bold red')
            return

        loggers: list[str] = [''.join(filter(str.isalpha, level)) for level in args]

        invalid_loggers: set = set(loggers) - set(app_data.get('loggers'))

        if len(invalid_loggers) != 0:
            console.print(t('errors.moonfile', 'undefined_logger_type', default_loggers = ', '.join(app_data.get('loggers')), undefined_logger = list(invalid_loggers)[0]), style = Style.ERROR.value)
            return

        self.app_config['loggers'] = loggers

    def create_user(self, *args) -> None:
        '''
        `Creates a new user based on the provided data`

        arguments
            *args <- a list of user parameters, including access rights, username and password.
        '''
        if len(args) < 3:
            console.print(t('errors.moonfile', 'params_create_user', length_args = len(args)), style = Style.ERROR.value)
            return
        
        self.users.append({
            'username'    : args[1],
            'password'    : args[2],
            'permissions' : args[0]
        })

    def create_database(self, *args) -> None:
        '''
        `Initializes the database based on the provided parameters`

        arguments:
            *args <- a list of database parameters, including name and author
        '''
        if not args:
            console.print(t('errors.moonfile', 'no_params_database', default_author = app_data.get('self_admin')), style = Style.ERROR.value)
            return
        
        name, *optional = args
        author: str = optional[0] if optional else app_data.get('self_admin')

        if author.startswith('@'):
            author = author[1:]

            if not any(user.get('username') == author for user in self.users):
                console.print(t('errors.moonfile', 'undefined_user', undefined_user = author), style = Style.ERROR.value)
                return
            
        self.databases.append({ 'name': name, 'author': author })

    def compile(self) -> None:
        '''`Compiles and applies the settings defined in the Moonfile`'''
        if self.ignore:
            console.print(t('warnings.moonfile', 'ignored'), style = Style.WARNING.value)
            return
        
        if self.app_config: 
            Methods.configure(**self.app_config)

        for user in self.users: 
            Methods.create_user(**user)
        
        for database in self.databases: 
            Moonlight(database.get('name'), database.get('author'))