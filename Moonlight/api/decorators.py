from sanic.response import json
from functools      import wraps

from Moonlight.config.config import app_data

access_hierarchy: dict[str, int] = app_data.get('access_hierarchy')

def permission(minimal_permissions):
    def decorator(func):
        @wraps(func)
        async def decorated_function(request, *args, **kwargs):
            user_permissions = request.ctx.user.get('permissions')
            
            if access_hierarchy.get(user_permissions, 0) < access_hierarchy.get(minimal_permissions, 0): return json({ 'error': 'Permission denied' }, status = 403)
            
            return await func(request, *args, **kwargs)
        
        return decorated_function
    
    return decorator

def required_fields(*fields):
    def decorator(func):
        @wraps(func)
        async def decorated_function(request, *args, **kwargs):
            missing_fields: list[str] = [field for field in fields if field not in request.json]

            if missing_fields: return json({ 'error': 'Required fields are not specified', 'missing_fields': missing_fields }, status = 400)

            return await func(request, *args, **kwargs)
        
        return decorated_function
    
    return decorator
