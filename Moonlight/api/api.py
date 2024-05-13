from sanic          import Sanic, Request
from sanic.response import json, html
from datetime       import datetime
from sanic_cors     import CORS

from Moonlight.api.decorators       import permission, required_fields
from Moonlight.config.config        import config, app_data
from Moonlight.core.tools           import password_hash
from Moonlight.config.documentation import read_docs
from Moonlight.core.paths           import docs_moonlight_path
from Moonlight.core.moonlight       import Moonlight
from Moonlight.core.methods         import Methods

def create_application() -> Sanic:
    app: Sanic = Sanic('Moonlight')

    CORS(app)

    @app.route('/moonlight/docs', methods = ['GET'])
    async def moonlight_docs(request: Request) -> html:
        return html(
            await read_docs(docs_moonlight_path),
            status = 200
        )

    @app.route('/auth', methods = ['POST'])
    @required_fields('username', 'password')
    async def auth(request: Request) -> json:
        username: str = request.json.get('username')
        password: str = request.json.get('password')

        user: dict[str, any] = next((user for user in config.get('users') if (user.get('username') == username) and user.get('password') == password_hash(password)), None)
        
        if not user: return json({ 'error' : 'Invalid credentials' }, status = 401)
        
        token_data: dict[str, str] = Methods.create_token(username)

        return json({ 'data' : token_data }, status = 200)

    @app.middleware('request')
    async def validate_auth(request: Request) -> json:
        match request.path:
            case '/auth':           return
            case '/moonlight/docs': return
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

    @app.route('/moonlight/create', methods = ['GET'])
    @permission('Administrator')
    async def moonlight_create(request: Request) -> json:
        name: str = request.args.get('name')

        if not name: return json({ 'error' : 'Name required!' }, status = 400)

        existed_database: dict[str, any] = next((database for database in config.get('databases') if database.get('name') == name), None)

        if existed_database: return json({ 'data' : { 'id' : existed_database.get('id'), 'message': f'Database with name `{name}` already exists' } }, status = 409)

        database: Moonlight = Moonlight(name, author = request.ctx.user.get('username'), console_show = app_data.get('api').get('console_show'))

        return json({ 'data' : { 'id' : database.database_id } }, status = 201)

    @app.route('/moonlight/<database_id:int>/push', methods = ['POST'])
    @permission('Editor')
    async def moonlight_push(request: Request, database_id: int) -> json:
        pass

    @app.route('/moonlight/<database_id:int>/all', methods = ['GET'])
    @permission('Viewer')
    async def moonlight_all(request: Request, database_id: int) -> json:
        pass

    @app.route('/moonlight/<database_id:int>/get', methods = ['POST'])
    @permission('Viewer')
    async def moonlight_get(request: Request, database_id: int) -> json:
        pass

    @app.route('/moonlight/<database_id:int>/update', methods = ['POST'])
    @permission('Editor')
    async def moonlight_update(request: Request, database_id: int) -> json:
        pass

    @app.route('/moonlight/<database_id:int>/delete', methods = ['GET'])
    @permission('Editor')
    async def moonlight_delete(request: Request, database_id: int) -> json:
        id: str = request.args.get('id')

        pass

    @app.route('/moonlight/<id:int>/drop', methods = ['GET'])
    @permission('Administrator')
    async def moonlight_drop(request: Request, id: int) -> json:
        pass

    return app


# get user
# auth
# create user - only for admin