from sanic.response import json
from functools      import wraps

from Moonlight.api.response_codes import ResponseCodes
from Moonlight.config.config      import app_data, config
from Moonlight.core.moonlight     import Moonlight

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

            if not request.json: return json({ 'message' : 'The request body must contain data in json format.', 'missing_fields' : fields }, status = ResponseCodes['BAD_REQUEST'].value)

            for field in fields:
                if field not in request.json:
                    missing_fields.append(field)
                
                elif not request.json.get(field, None):
                    empty_fields.append(field)

            if missing_fields: return json({ 'message' : 'Required fields are not specified', 'missing_fields' : missing_fields }, status = ResponseCodes['BAD_REQUEST'].value)
            if empty_fields:   return json({ 'message' : 'Some fields are empty',             'empty_fields'   : empty_fields },   status = ResponseCodes['BAD_REQUEST'].value)

            return await func(request, *args, **kwargs)
        
        return decorated_function
    
    return decorator


def required_arguments(*arguments):
    def decorator(func):
        @wraps(func)
        async def decorated_function(request, *args, **kwargs):
            missing_arguments: list[str] = []
            empty_arguments:   list[str] = []

            for argument in arguments:
                if argument not in request.args:
                    missing_arguments.append(argument)
                
                elif not request.args.get(argument, None):
                    empty_arguments.append(argument)

            if missing_arguments: return json({ 'message' : 'Required arguments are not specified', 'missing_arguments' : missing_arguments }, status = ResponseCodes['BAD_REQUEST'].value)
            if empty_arguments:   return json({ 'message' : 'Some arguments are empty',             'empty_arguments'   : empty_arguments },   status = ResponseCodes['BAD_REQUEST'].value)

            return await func(request, *args, **kwargs)
    
        return decorated_function
    
    return decorator

def get_database_by_id(func):
    @wraps(func)
    async def decorated_function(request, database_id, *args, **kwargs):
        existed_database = next((database for database in config.get('databases') if database.get('id') == database_id), None)
        
        if not existed_database: return json({ 'message': 'Database not found' }, status = ResponseCodes['NOT_FOUND'].value)
        
        return await func(request, Moonlight(existed_database.get('name')), *args, **kwargs)
        
    return decorated_function