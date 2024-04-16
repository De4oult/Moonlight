from Moonlight.paths     import make_moonfile_path
from Moonlight.config    import app_data, config
from Moonlight.messages  import t
from Moonlight.methods   import Methods
from Moonlight.moonlight import Moonlight

from rich.console import Console

console = Console()

class Moonfile:
    def __init__(self):
        self.path: str = make_moonfile_path(app_data.get('moonfile'))
        
        self.app_config: dict[str, any] = {}
        self.databases: list = []
        self.users: list = []
        
        self.ignore: bool = False

    def parse_config(self):
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
                    case '?':           continue
                    case 'IGNORE':      self.ignore = True
                    case _:             console.print(t('warnings.moonfile', 'undefined_command', command = command), style = 'bold yellow')

    def set_app(self, *args) -> None:
        if not len(args):
            console.print(t('errors.moonfile', 'no_host_app', default_port = app_data.get('base_config').get('port')), style = 'bold red')
            return
        
        host = list(filter(None, args[0].split(':')))

        self.app_config['host'] = host[0]

        if len(host) == 1:
            console.print(t('warnings.moonfile', 'no_port_app', default_port = app_data.get('base_config').get('port')), style = 'bold yellow')
        
        self.app_config['port'] = host[1] if len(host) > 1 else app_data.get('base_config').get('port')

    def set_logging(self, *args):
        if not len(args):
            console.print(t('errors.moonfile', 'no_loggers_log'), style = 'bold red')
            return

        loggers: list[str] = [''.join(filter(str.isalpha, level)) for level in args]

        invalid_loggers: set = set(loggers) - set(app_data.get('loggers'))

        if len(invalid_loggers) != 0:
            console.print(t('errors.moonfile', 'undefined_logger_type', default_loggers = ', '.join(app_data.get('loggers')), undefined_logger = list(invalid_loggers)[0]), style = 'bold red')
            return

        self.app_config['loggers'] = loggers

    def create_user(self, *args):
        if len(args) < 3:
            console.print(t('errors.moonfile', 'params_create_user', length_args = len(args)), style = 'bold red')
            return
        
        self.users.append({
            'username'    : args[1],
            'password'    : args[2],
            'permissions' : args[0]
        })

    def create_database(self, *args):
        if not len(args):
            console.print(t('errors.moonfile', 'no_params_database', default_author = app_data.get('self_admin')), style = 'bold red')
            return
        
        name   = args[0]
        author = args[1] if len(args) > 1 else app_data.get('self_admin')

        if author and author.startswith('@'):
            author = author[1:]

            if author not in [user.get('username') for user in self.users]:
                console.print(t('errors.moonfile', 'undefined_user', undefined_user = author), style = 'bold red')
                return
            
        self.databases.append({'name': name, 'author': author})

    def compile(self) -> None:
        if self.ignore:
            console.print(t('warnings.moonfile', 'ignored'), style = 'bold yellow')
            return
        
        Methods.configure(self.app_config.get('host'), self.app_config.get('port'), self.app_config.get('loggers'))

        for user in self.users:
            Methods.create_user(user.get('username'), user.get('password'), user.get('permissions'))


moonfile = Moonfile()
moonfile.parse_config()
moonfile.compile()