from sanic.response import json
from functools      import wraps
from InquirerPy     import prompt

from Moonlight.config   import config
from Moonlight.tools    import password_hash
from Moonlight.messages import t

access_hierarchy = {
    'Viewer'       : 1,
    'Editor'       : 2,
    'Administrator': 3
}

def permission(minimal_permission):
    def decorator(func):
        @wraps(func)
        async def decorated_function(request, *args, **kwargs):
            user_permission = request.ctx.user.get('permissions')
            
            if access_hierarchy.get(user_permission, 0) < access_hierarchy.get(minimal_permission, 0): return json({ 'error': 'Permission denied' }, status = 403)
            
            return await func(request, *args, **kwargs)
        
        return decorated_function
    
    return decorator

def auth_cli():
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            users = config.get('users')

            if len(users) == 0:
                print(t('errors.user', 'need_create_user'))
                return
            
            username = prompt({
                'type'    : 'input',
                'message' :  t('prompt.enter', 'username'),
                'name'    : 'username'
            }).get('username')
            
            user = next((user for user in users if user.get('username') == username), None)

            if not user:
                print(t('errors.user', 'cant_find', username = username))
                return
                
            password = prompt({
                'type'    : 'password',
                'message' : t('prompt.enter', 'password'),
                'name'    : 'password'
            }).get('password')

            if password_hash(password) != user.get('password'):
                print(t('errors.user', 'invalid_password'))
                return
            
            return func(*args, **kwargs)
        
        return decorated_function
    
    return decorator