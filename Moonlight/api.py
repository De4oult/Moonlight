from sanic               import Sanic, Request
from sanic.response      import json
from sanic_cors          import CORS
from functools           import wraps

from Moonlight.moonlight import Moonlight

databases: Moonlight = Moonlight(
    'databases.json', 
    show_messages = (
        'success',
        'warning',
        'error'
    )
)

def permission(required_permission):
    permission_hierarchy = {
        'Viewer'       : 1,
        'Editor'       : 2,
        'Administrator': 3
    }

    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            user_permissions = request.ctx.user.get('permissions')
            
            if permission_hierarchy.get(user_permissions, 0) < permission_hierarchy.get(required_permission, 0): return json({ 'error': 'Permission denied' }, status = 403)

            return await f(request, *args, **kwargs)

        return decorated_function

    return decorator

def create_application():
    app: Sanic = Sanic('Moonlight')

    CORS(app)

    @app.route('/init', methods = ['POST'])
    @permission('Administrator')
    async def database_init(request: Request) -> json:
        filename     : str   = str(request.json.get('name'))            if request.json.get('name')          else None
        primary_key  : str   = str(request.json.get('primary_key'))     if request.json.get('primary_key')   else 'id'
        show_messages: tuple = tuple(request.json.get('show_messages')) if request.json.get('show_messages') else ('warning', 'error')

        if not filename: return json({ 'description' : 'Name of database required!' }, status = 400)

        if await databases.contains('filename', filename): return json({ 'data' : { 'id' : (await databases.get({ 'filename' : filename }))[0].get('id'), 'msg': f'Database with name `{filename}` already exists' } }, status = 200)

        id = await databases.push({
            'filename'      : filename,
            'primary_key'   : primary_key, 
            'show_messages' : show_messages
        })

        Moonlight(f'{id}.json', primary_key, show_messages)

        return json({ 'data' : { 'id' : id } }, status = 200)

    @app.route('/<database_id:int>/push', methods = ['POST'])
    @permission('Editor')
    async def database_push(request: Request, database_id: int) -> json:
        databaseExist = (await databases.get({ 'id' : int(database_id) }))

        if not databaseExist: return json({ 'description' : 'No database exists!' }, status = 400)

        id = await Moonlight(database_id).push(request.json)

        return json({ 'data' : { 'id' : id } }, status = 200)

    @app.route('/<database_id:int>/all', methods = ['GET'])
    @permission('Viewer')
    async def database_all(request: Request, database_id: int) -> json:
        databaseExist = (await databases.get({ 'id' : int(database_id) }))

        if not databaseExist: return json({ 'description' : 'No database exists!' }, status = 400)
        
        data = await Moonlight(database_id).all()

        return json({ 'data' : data }, status = 200)

    @app.route('/<database_id:int>/get', methods = ['POST'])
    @permission('Viewer')
    async def database_get(request: Request, database_id: int) -> json:
        databaseExist = (await databases.get({ 'id' : int(database_id) }))

        if not databaseExist:
            return json({
                'status' : 500,
                'description' : 'No database exists!'
            })
        
        data = await Moonlight(database_id).get(request.json)

        return json({ 'data' : data }, status = 200)

    @app.route('/<database_id:int>/update', methods = ['POST'])
    @permission('Editor')
    async def database_update(request: Request, database_id: int) -> json:
        databaseExist = (await databases.get({ 'id' : int(database_id) }))

        if not databaseExist:
            return json({
                'status'      : 500,
                'description' : 'No database exists!'
            })
        
        if not request.json.get('id'):
            return json({
                'status'      : 500,
                'description' : 'No `id` specified!'
            })

        data = await Moonlight(database_id).update(request.json)

        return json({ 'data' : data }, status = 200)

    @app.route('/<database_id:int>/delete', methods = ['POST'])
    @permission('Editor')
    async def database_delete(request: Request, database_id: int) -> json:
        databaseExist = (await databases.get({ 'id' : int(database_id) }))

        if not databaseExist: return json({ 'description' : 'No database exists!' }, status = 400)

        data = await Moonlight(database_id).delete(request.json.get('id'))

        return json({ 'data' : data }, status = 200)

    @app.route('/<database_id:int>/drop', methods = ['GET'])
    @permission('Administrator')
    async def database_drop(request: Request, database_id: int) -> json:
        databaseExist = (await databases.get({ 'id' : int(database_id) }))

        if not databaseExist: return json({ 'description' : 'No database exists!' }, status = 400)

        await databases.delete(database_id)
        
        await Moonlight(database_id).drop()

        return json({}, status = 200)
    
    return app


# get user
# auth
# create user - only for admin