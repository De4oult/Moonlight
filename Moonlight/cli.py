from sanic.worker.loader import AppLoader
from sanic               import Sanic
from functools           import partial
from InquirerPy          import prompt

from Moonlight.config import config
from Moonlight.tools  import password_hash
from Moonlight.api    import create_application

import secrets
import click

@click.command()
def serve() -> None:    
    loader: AppLoader = AppLoader(factory = partial(create_application))
    
    app: Sanic = loader.load()

    app.prepare(
        host       = config.get('host'),
        port       = config.get('port'),
        access_log = False
    )

    Sanic.serve(
        primary = app, 
        app_loader = loader
    )

@click.command()
@click.option('-h', '--host',           default = '127.0.0.1', type = str,  help = 'database manager IP address')
@click.option('-p', '--port',           default = 3000,        type = int,  help = 'database manager port')
@click.option('--auth/--no-auth',       default = False,       type = bool, help = 'need auth, if true returns you api key')
@click.option('--logging/--no-logging', default = True,        type = bool, help = 'on logging')
def configure(host: str, port: int, auth: bool, logging: bool) -> None:
    config.set('host',      host)
    config.set('port',      port)
    config.set('need_logs', logging)

    if(logging):
        config.set('loggers', prompt({
            'type'    : 'checkbox',
            'message' : 'Select loggers:',
            'choices' : ['Info', 'Success', 'Warning', 'Error'],
            'name'    : 'loggers'
        }).get('loggers'))


    print('APP configured!') #!!!

    if(auth): print('New API token: %s' % config.get('api_key')) #!!!

@click.command()
@click.option('-u', '--username', required = True, type = str, help = 'username')
@click.option('-p', '--password', type = str, help = 'password')
def create_user(username: str, password: str) -> None:
    users = config.get('users')

    for user in users:
        if user.get('username') == username:
            print('!!! User already exist. Delete id before create new') #!!!
            return
        
    new_user: dict[str, any] = {
        'username' : username,
        'password' : password_hash(password),
        'api_key'  : secrets.token_hex(32)
    }

    new_user['permissions'] = prompt({
        'type'    : 'list',
        'message' : 'Select permissions level:',
        'choices' : ['Viewer', 'Editor', 'Administrator'],
        'name'    : 'permissions'
    }).get('permissions')
        
    config.set('users', [*users, new_user])
    print('User successfully added \nToken: %s' % new_user.get('api_key'))

@click.command()
def delete_user() -> None:
    users = config.get('users')

    if len(users) == 0:
        print('No users!')
        return

    username = prompt({
        'type'    : 'list',
        'message' : 'Select user to delete:',
        'choices' : [user.get('username') for user in users],
        'name'    : 'username'
    }).get('username')

    proceed = prompt({
        'type'    : 'confirm',
        'message' : f'Delete user {username}',
        'name'    : 'proceed',
        'default' : False
    }).get('proceed')

    if not proceed: 
        print('Cancel')
        return

    config.set('users', [user for user in users if user.get('username') != username])

@click.group()
def cli() -> None: ...

cli.add_command(serve)
cli.add_command(configure)
cli.add_command(create_user)
cli.add_command(delete_user)

if __name__ == '__main__':
    cli()