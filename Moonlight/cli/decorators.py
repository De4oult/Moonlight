from sanic.response import json
from functools      import wraps
from InquirerPy     import prompt
from rich.console   import Console

from Moonlight.config.config     import config, app_data
from Moonlight.core.tools        import password_hash
from Moonlight.messages.messages import t

console: Console = Console()

access_hierarchy: dict[str, int] = app_data.get('access_hierarchy')

def auth_cli(minimal_permissions):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            users = config.get('users')

            console.print(t('methods.auth'), style = 'bold purple')

            if len(users) == 0:
                console.print('\n' + t('errors.user.need_create_user'), style = 'bold red')
                return

            username = prompt({
                'type'    : 'input',
                'message' :  t('prompt.enter.username'),
                'name'    : 'username'
            }).get('username')
            
            user = next((user for user in users if user.get('username') == username), None)

            if not user:
                console.print('\n' + t('errors.user.cant_find', username = username), style = 'bold red')
                return
                
            password = prompt({
                'type'    : 'password',
                'message' : t('prompt.enter.password'),
                'name'    : 'password'
            }).get('password')

            if password_hash(password) != user.get('password'):
                console.print('\n' + t('errors.user.invalid_password'), style = 'bold red')
                return
            
            if access_hierarchy.get(user.get('permissions'), 0) < access_hierarchy.get(minimal_permissions, 0):
                console.print('\n' + t('errors.user.low_permissions', minimal_permissions = minimal_permissions, permissions = user.get('permissions')), style = 'bold red')
                return                
            
            return func(username, *args, **kwargs)
        
        return decorated_function
    
    return decorator