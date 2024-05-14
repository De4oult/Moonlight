from sanic          import Sanic, Request
from sanic.response import json, html, HTTPResponse
from datetime       import datetime
from sanic_cors     import CORS
from typing         import Any

from Moonlight.api.decorators       import permission, required_fields, get_database_by_id, required_arguments
from Moonlight.config.config        import config, app_data
from Moonlight.core.tools           import password_hash
from Moonlight.config.documentation import read_docs
from Moonlight.config.paths         import docs_moonlight_path
from Moonlight.core.moonlight       import Moonlight
from Moonlight.core.methods         import Methods
from Moonlight.api.response_codes   import ResponseCodes

def create_application() -> Sanic:
    app: Sanic = Sanic('Moonlight')

    CORS(app)

    @app.route('/moonlight/docs', methods = ['GET'])
    async def moonlight_docs(request: Request) -> HTTPResponse:
        return html(
            await read_docs(docs_moonlight_path),
            status = ResponseCodes['OK'].value
        )

    @app.route('/auth', methods = ['POST'])
    @required_fields('username', 'password')
    async def auth(request: Request) -> HTTPResponse:
        username: str = request.json.get('username')
        password: str = request.json.get('password')

        user: dict[str, Any] = next((user for user in config.get('users') if (user.get('username') == username) and user.get('password') == password_hash(password)), None)
        
        if not user: return json({ 'message' : 'Invalid credentials' }, status = ResponseCodes['UNAUTHORIZED'].value)
        
        token_data: dict[str, str] = Methods.create_token(username)

        return json({ 'data' : token_data }, status = ResponseCodes['OK'].value)

    @app.middleware('request')
    async def validate_auth(request: Request) -> HTTPResponse:
        match request.path:
            case '/auth':           return
            case '/moonlight/docs': return
            case _: pass

        user_token: str = request.headers.get('Authorization')

        token: dict[str, Any] = next((token for token in config.get('api_keys') if token.get('token') == user_token and datetime.fromisoformat(token.get('expires')) > datetime.now()), None)

        if not token: return json({ 'message' : 'Invalid or expired token' }, status = ResponseCodes['UNAUTHORIZED'].value)

        request.ctx.user = next(user for user in config.get('users') if user.get('username') == token.get('author'))

    @app.route('/moonlight/databases', methods = ['GET'])
    @permission('Administrator')
    async def databases_list(request: Request) -> HTTPResponse:
        return json({ 
            'data' : {
                'databases' : config.get('databases')
            }
        }, status = ResponseCodes['OK'].value)
                     
    @app.route('/moonlight/create', methods = ['GET'])
    @permission('Administrator')
    @required_arguments('name')
    async def moonlight_create(request: Request) -> HTTPResponse:
        name: str = request.args.get('name')

        existed_database: dict[str, Any] = next((existed_database for existed_database in config.get('databases') if existed_database.get('name') == name), None)

        if existed_database: return json({ 'data' : { 'id' : existed_database.get('id'), 'message': f'Database with name `{name}` already exists' } }, status = ResponseCodes['CONFLICT'].value)

        database: Moonlight = Moonlight(name, author = request.ctx.user.get('username'), console_show = app_data.get('api').get('console_show'))

        return json({ 
            'data' : { 
                'id'      : database.database_id, 
                'message' : 'The database has been created successfully' 
            } 
        }, status = ResponseCodes['CREATED'].value)

    @app.route('/moonlight/<database_id:int>/push', methods = ['POST'])
    @permission('Editor')
    @get_database_by_id
    @required_fields('query')
    async def moonlight_push(request: Request, database: Moonlight) -> HTTPResponse:
        query: dict[str, Any] = request.json.get('query')

        record_id: int = await database.push(query)

        return json({ 
            'data' : { 
                'id'      : record_id, 
                'message' : 'The record was successfully added to the database', 
                'address' : f'{database.database_id}:{record_id}' 
            } 
        }, status = ResponseCodes['OK'].value)

    @app.route('/moonlight/<database_id:int>/all', methods = ['GET'])
    @permission('Viewer')
    @get_database_by_id
    async def moonlight_all(request: Request, database: Moonlight) -> HTTPResponse:
        records: list[dict[str, Any]] = await database.all()

        return json({ 
            'data' : { 
                'records' : records, 
                'message' : 'The records were successfully received from the database' 
            } 
        }, status = ResponseCodes['OK'].value)

    @app.route('/moonlight/<database_id:int>/get', methods = ['POST'])
    @permission('Viewer')
    @get_database_by_id
    @required_fields('query')
    async def moonlight_get(request: Request, database: Moonlight) -> HTTPResponse:
        query: dict[str, Any] = request.json.get('query')

        records: list[dict[str, Any]] = await database.get(query) 

        return json({
            'data' : {
                'records' : records, 
                'message' : 'The records were successfully received from the database'
            }
        }, status = ResponseCodes['OK'].value)

    @app.route('/moonlight/<database_id:int>/update', methods = ['POST'])
    @permission('Editor')
    @get_database_by_id
    @required_fields('query')
    async def moonlight_update(request: Request, database: Moonlight) -> HTTPResponse:
        query: dict[str, Any] = request.json.get('query')

        record_id: int = await database.update(query)

        return json({
            'data' : {
                'id'      : record_id,
                'message' : 'The database record has been successfully updated'
            }
        }, status = ResponseCodes['OK'].value)

    @app.route('/moonlight/<database_id:int>/delete', methods = ['GET'])
    @permission('Editor')
    @get_database_by_id
    @required_arguments('id')
    async def moonlight_delete(request: Request, database: Moonlight) -> HTTPResponse:
        record_id: int = int(request.args.get('id'))

        await database.delete(record_id)

        return json({
            'data' : {
                'id'      : record_id,
                'message' : 'The record was successfully deleted from the database'
            }
        }, status = ResponseCodes['OK'].value)

    @app.route('/moonlight/<database_id:int>/drop', methods = ['GET'])
    @permission('Administrator')
    @get_database_by_id
    async def moonlight_drop(request: Request, database: Moonlight) -> HTTPResponse:
        await database.drop()

        return json({
            'data' : {
                'id'      : database.database_id,
                'message' : 'The database was successfully deleted'
            }
        }, status = ResponseCodes['OK'].value)

    return app
