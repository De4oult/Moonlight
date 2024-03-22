from sanic               import Sanic, Request
from sanic.response      import json
from sanic_cors          import CORS
from functools           import wraps
from datetime            import datetime, timedelta

from Moonlight.moonlight  import Moonlight
from Moonlight.config     import config
from Moonlight.tools      import password_hash, generate_token
from Moonlight.decorators import permission

# databases: Moonlight = Moonlight(
#     'databases.json', 
#     show_messages = (
#         'info',
#         'success',
#         'warning',
#         'error'
#     )
# )

def create_application() -> Sanic:
    app: Sanic = Sanic('Moonlight')

    CORS(app)

    @app.route('/auth', methods = ['POST'])
    async def database_auth(request: Request) -> json:
        username: str = request.json.get('username')
        password: str = password_hash(request.json.get('password'))

        users: list[dict[str, any]] = config.get('users')

        user: dict[str, any] = next((user for user in users if (user.get('username') == username) and user.get('password') == password), None)
        
        if not user: return json({ 'error' : f'User `{username}`: invalid credentials' }, status = 401)

        token:   str = generate_token()
        expires: str = (datetime.now() + timedelta(hours = 3)).isoformat()
        created: str = datetime.now().isoformat()
        
        config.push('api_keys', {
            'author'     : username,
            'token'      : token,
            'expires'    : expires,
            'created'    : created,
            'permissions': user.get('permissions')
        })

        return json({ 'token' :  token }, status = 200)

    @app.middleware('request')
    async def validate_auth(request: Request) -> json:
        match request.path:
            case '/auth': return
            case _: pass

        user_token = request.headers.get('Authorization')

        token = next((token for token in config.get('api_keys') if token.get('token') == user_token and datetime.fromisoformat(token.get('expires')) > datetime.now()), None)

        if not token: return json({ 'error' : 'Invalid or expired token' }, status = 401)

        request.ctx.user = next(user for user in config.get('users') if user.get('username') == token.get('author'))

    return app

    # @app.route('/init', methods = ['POST'])
    # @permission('Administrator')
    # async def database_init(request: Request) -> json:
    #     filename     : str   = str(request.json.get('name'))            if request.json.get('name')          else None
    #     primary_key  : str   = str(request.json.get('primary_key'))     if request.json.get('primary_key')   else 'id'
    #     show_messages: tuple = tuple(request.json.get('show_messages')) if request.json.get('show_messages') else ('warning', 'error')

    #     if not filename: return json({ 'description' : 'Name of database required!' }, status = 400)

    #     if await databases.contains('filename', filename): return json({ 'data' : { 'id' : (await databases.get({ 'filename' : filename }))[0].get('id'), 'msg': f'Database with name `{filename}` already exists' } }, status = 200)

    #     id = await databases.push({
    #         'filename'      : filename,
    #         'primary_key'   : primary_key, 
    #         'show_messages' : show_messages
    #     })

    #     Moonlight(f'{id}.json', primary_key, show_messages)

    #     return json({ 'data' : { 'id' : id } }, status = 200)

    # @app.route('/<database_id:int>/push', methods = ['POST'])
    # @permission('Editor')
    # async def database_push(request: Request, database_id: int) -> json:
    #     databaseExist = (await databases.get({ 'id' : int(database_id) }))

    #     if not databaseExist: return json({ 'description' : 'No database exists!' }, status = 400)

    #     id = await Moonlight(database_id).push(request.json)

    #     return json({ 'data' : { 'id' : id } }, status = 200)

    # @app.route('/<database_id:int>/all', methods = ['GET'])
    # @permission('Viewer')
    # async def database_all(request: Request, database_id: int) -> json:
    #     databaseExist = (await databases.get({ 'id' : int(database_id) }))

    #     if not databaseExist: return json({ 'description' : 'No database exists!' }, status = 400)
        
    #     data = await Moonlight(database_id).all()

    #     return json({ 'data' : data }, status = 200)

    # @app.route('/<database_id:int>/get', methods = ['POST'])
    # @permission('Viewer')
    # async def database_get(request: Request, database_id: int) -> json:
    #     databaseExist = (await databases.get({ 'id' : int(database_id) }))

    #     if not databaseExist:
    #         return json({
    #             'status' : 500,
    #             'description' : 'No database exists!'
    #         })
        
    #     data = await Moonlight(database_id).get(request.json)

    #     return json({ 'data' : data }, status = 200)

    # @app.route('/<database_id:int>/update', methods = ['POST'])
    # @permission('Editor')
    # async def database_update(request: Request, database_id: int) -> json:
    #     databaseExist = (await databases.get({ 'id' : int(database_id) }))

    #     if not databaseExist:
    #         return json({
    #             'status'      : 500,
    #             'description' : 'No database exists!'
    #         })
        
    #     if not request.json.get('id'):
    #         return json({
    #             'status'      : 500,
    #             'description' : 'No `id` specified!'
    #         })

    #     data = await Moonlight(database_id).update(request.json)

    #     return json({ 'data' : data }, status = 200)

    # @app.route('/<database_id:int>/delete', methods = ['POST'])
    # @permission('Editor')
    # async def database_delete(request: Request, database_id: int) -> json:
    #     databaseExist = (await databases.get({ 'id' : int(database_id) }))

    #     if not databaseExist: return json({ 'description' : 'No database exists!' }, status = 400)

    #     data = await Moonlight(database_id).delete(request.json.get('id'))

    #     return json({ 'data' : data }, status = 200)

    # @app.route('/<database_id:int>/drop', methods = ['GET'])
    # @permission('Administrator')
    # async def database_drop(request: Request, database_id: int) -> json:
    #     databaseExist = (await databases.get({ 'id' : int(database_id) }))

    #     if not databaseExist: return json({ 'description' : 'No database exists!' }, status = 400)

    #     await databases.delete(database_id)
        
    #     await Moonlight(database_id).drop()

    #     return json({}, status = 200)
    
    # return app


# get user
# auth
# create user - only for admin