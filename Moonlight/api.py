from sanic               import Sanic, Request
from sanic.response      import json
from sanic_cors          import CORS
from Moonlight.moonlight import Moonlight

databases: Moonlight = Moonlight(
    'databases.json', 
    show_messages = (
        'success',
        'warning',
        'error'
    )
)

def create_application():
    app = Sanic('Moonlight')

    CORS(app)

    @app.route('/init', methods = ['POST'])
    async def database_init(request: Request) -> json:
        filename     : str   = str(request.json.get('name'))            if request.json.get('name')          else None
        primary_key  : str   = str(request.json.get('primary_key'))     if request.json.get('primary_key')   else 'id'
        show_messages: tuple = tuple(request.json.get('show_messages')) if request.json.get('show_messages') else ('warning', 'error')

        if not filename:
            return json({
                'status'      : 500,
                'description' : 'Name of database required!'
            })

        if await databases.contains('filename', filename):
            return json({
                'status' : 200,
                'data'   : {
                    'id' : (await databases.get({ 'filename' : filename }))[0].get('id'),
                    'msg': f'Database with name `{filename}` already exists'
                }
            })

        id = await databases.push({
            'filename'      : filename,
            'primary_key'   : primary_key, 
            'show_messages' : show_messages
        })

        Moonlight(f'{id}.json', primary_key, show_messages)

        return json({
            'status' : 200,
            'data'   : {
                'id' : id
            }
        })

    @app.route('/<database_id:int>/push', methods = ['POST'])
    async def database_push(request: Request, database_id: int) -> json:
        databaseExist = (await databases.get({ 'id' : int(database_id) }))

        if not databaseExist:
            return json({
                'status' : 500,
                'description' : 'No database exists!'
            })

        id = await Moonlight(database_id).push(request.json)

        return json({
            'status' : 200,
            'data'   : {
                'id' : id
            }
        })

    @app.route('/<database_id:int>/all', methods = ['GET'])
    async def database_all(request: Request, database_id: int) -> json:
        databaseExist = (await databases.get({ 'id' : int(database_id) }))

        if not databaseExist:
            return json({
                'status' : 500,
                'description' : 'No database exists!'
            })
        
        data = await Moonlight(database_id).all()

        return json({
            'status' : 200,
            'data'   : data
        })

    @app.route('/<database_id:int>/get', methods = ['POST'])
    async def database_get(request: Request, database_id: int) -> json:
        databaseExist = (await databases.get({ 'id' : int(database_id) }))

        if not databaseExist:
            return json({
                'status' : 500,
                'description' : 'No database exists!'
            })
        
        data = await Moonlight(database_id).get(request.json)

        return json({
            'status' : 200,
            'data'   : data
        })

    @app.route('/<database_id:int>/update', methods = ['POST'])
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

        return json({
            'status' : 200,
            'body'   : data
        })

    @app.route('/<database_id:int>/delete', methods = ['POST'])
    async def database_delete(request: Request, database_id: int) -> json:
        databaseExist = (await databases.get({ 'id' : int(database_id) }))

        if not databaseExist:
            return json({
                'status' : 500,
                'description' : 'No database exists!'
            })

        data = await Moonlight(database_id).delete(request.json.get('id'))

        return json({
            'status' : 200,
            'data'   : data
        })

    @app.route('/<database_id:int>/drop', methods = ['GET'])
    async def database_drop(request: Request, database_id: int) -> json:
        databaseExist = (await databases.get({ 'id' : int(database_id) }))

        if not databaseExist:
            return json({
                'status' : 500,
                'description' : 'No database exists!'
            })

        await databases.delete(database_id)
        
        await Moonlight(database_id).drop()

        return json({
            'status' : 200
        })
    
    return app