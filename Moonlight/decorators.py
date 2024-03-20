from sanic.response import json
from functools      import wraps

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