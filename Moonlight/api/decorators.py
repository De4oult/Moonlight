from sanic.response import json
from functools      import wraps

from Moonlight.api.response_codes import ResponseCodes
from Moonlight.config.config      import app_data, config

access_hierarchy: dict[str, int] = app_data.get('access_hierarchy')

def permission(minimal_permissions):
    def decorator(func):
        @wraps(func)
        async def decorated_function(request, *args, **kwargs):
            user_permissions = request.ctx.user.get('permissions')
            
            if access_hierarchy.get(user_permissions, 0) < access_hierarchy.get(minimal_permissions, 0): return json({ 'error': 'Permission denied' }, status = ResponseCodes['FORBIDDEN'].value)
            
            return await func(request, *args, **kwargs)
        
        return decorated_function
    
    return decorator

def required_fields(*fields):
    def decorator(func):
        @wraps(func)
        async def decorated_function(request, *args, **kwargs):
            missing_fields: list[str] = []
            empty_fields:   list[str] = []

            for field in fields:
                if field not in request.json:
                    missing_fields.append(field)
                
                elif not request.json.get(field, None):
                    empty_fields.append(field)

            if missing_fields: return json({ 'message' : 'Required fields are not specified', 'missing_fields': missing_fields }, status = ResponseCodes['BAD_REQUEST'].value)
            if empty_fields:   return json({ 'message' : 'Some fields are empty', 'empty_fields' : empty_fields },                status = ResponseCodes['BAD_REQUEST'].value)

            return await func(request, *args, **kwargs)
        
        return decorated_function
    
    return decorator

def get_database(func):
    @wraps(func)
    async def decorated_function(request, database_id, *args, **kwargs):
        existed_database = next((database for database in config.get('databases') if database.get('id') == database_id), None)
        
        if not existed_database: return json({ 'message': 'Database not found' }, status = ResponseCodes['NOT_FOUND'].value)
        
        return await func(request, existed_database, *args, **kwargs)
        
    return decorated_function
