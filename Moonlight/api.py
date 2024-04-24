from sanic               import Sanic, Request
from sanic.response      import json, html
from sanic_cors          import CORS
from datetime            import datetime, timedelta
from markdown2           import markdown

from Moonlight.moonlight  import Moonlight
from Moonlight.config     import config, app_data
from Moonlight.tools      import password_hash, generate_token
from Moonlight.decorators import permission, required_fields
from Moonlight.methods    import Methods

def create_application() -> Sanic:
    app: Sanic = Sanic('Moonlight')

    CORS(app)

    @app.route('/docs', methods = ['GET'])
    async def database_docs(request: Request) -> html:
        markdown_docs: str = app_data.get('docs')

        return html(
            f'''
            <div style="text-align: center;">
                {markdown(markdown_docs)}
            </div>
            ''',
            status = 200
        )

    @app.route('/auth', methods = ['POST'])
    @required_fields('username', 'password')
    async def database_auth(request: Request) -> json:
        username: str = request.json.get('username')
        password: str = request.json.get('password')

        user: dict[str, any] = next((user for user in config.get('users') if (user.get('username') == username) and user.get('password') == password_hash(password)), None)
        
        if not user: return json({ 'error' : 'Invalid credentials' }, status = 401)
        
        token_data: dict[str, str] = Methods.create_token(username)

        return json({ 'data' : token_data }, status = 200)

    @app.middleware('request')
    async def validate_auth(request: Request) -> json:
        match request.path:
            case '/auth': return
            case '/docs': return
            case _: pass

        user_token: str = request.headers.get('Authorization')

        token: dict[str, any] = next((token for token in config.get('api_keys') if token.get('token') == user_token and datetime.fromisoformat(token.get('expires')) > datetime.now()), None)

        if not token: return json({ 'error' : 'Invalid or expired token' }, status = 401)

        request.ctx.user = next(user for user in config.get('users') if user.get('username') == token.get('author'))

    # @app.route('/databases', methods = ['GET'])
    # @permission('Administrator')
    # async def databases_list(request: Request) -> json:
    #     databases: dict[str, any] = config.get('databases')

    #     formatted_databases: dict

    @app.route('/create_database', methods = ['POST'])
    @permission('Administrator')
    async def create_database(request: Request) -> json:
        name: str = request.json.get('name')

        if not name: return json({ 'error' : 'Name required!' }, status = 400)

        existed_database: dict[str, any] = next((database for database in config.get('databases') if database.get('name') == name), None)

        if existed_database: return json({ 'data' : { 'id' : existed_database.get('id'), 'message': f'Database with name `{name}` already exists' } }, status = 200)

        Moonlight(name, author = request.ctx.user.get('username'))

        new_database: dict[str, any] = next((database for database in config.get('databases') if database.get('name') == name), None)

        return json({ 'data' : { 'id' : new_database.get('id') } }, status = 201)

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
    
    return app


# get user
# auth
# create user - only for admin