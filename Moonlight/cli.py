from sanic.worker.loader import AppLoader
from sanic               import Sanic
from functools           import partial
from InquirerPy          import prompt
from rich.console        import Console

from Moonlight.config     import config, app_data
from Moonlight.tools      import password_hash, generate_uuid, get_now_datetime
from Moonlight.api        import create_application
from Moonlight.messages   import t
from Moonlight.decorators import auth_cli
from Moonlight.moonlight  import Moonlight

import click

console = Console()

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
@click.option('--logging/--no-logging', default = True,        type = bool, help = 'on logging')
def configure(host: str, port: int, logging: bool) -> None:
    config.set('host',      host)
    config.set('port',      port)
    config.set('need_logs', logging)

    if(logging):
        config.set('loggers', prompt({
            'type'    : 'checkbox',
            'message' : t('prompt.select', 'loggers'),
            'choices' : ['Info', 'Success', 'Warning', 'Error'],
            'name'    : 'loggers'
        }).get('loggers'))


    console.print(t('success.application', 'configured'))

@click.command()
def locale() -> None:
    locale = prompt({
        'type'    : 'list',
        'message' : t('prompt.select', 'locale'),
        'choices' : app_data.get('locales'),
        'name'    : 'locale'
    }).get('locale')

    app_data.set('current_locale', locale)

@click.command()
def create_user() -> None:
    users = config.get('users')

    username = prompt({
        'type'    : 'input',
        'message' :  t('prompt.enter', 'username'),
        'name'    : 'username'
    }).get('username')

    if any(user.get('username') == username for user in users):
        console.print(t('errors.user', 'already_exist', username=username))
        return

    password = prompt({
        'type'    : 'password',
        'message' : t('prompt.enter', 'password'),
        'name'    : 'password'
    }).get('password')

    new_user: dict[str, any] = {
        'username' : username,
        'password' : password_hash(password)
    }

    new_user['permissions'] = prompt({
        'type'    : 'list',
        'message' : t('prompt.select', 'permissions', username = username),
        'choices' : [t('permissions', 'viewer'), t('permissions', 'editor'), t('permissions', 'admin')],
        'name'    : 'permissions'
    }).get('permissions').lower()
        
    config.push('users', new_user)
    console.print(t('success.user', 'created'))

@click.command()
def delete_user() -> None:
    users = config.get('users')

    if len(users) == 0:
        console.print(t('errors.user', 'no_one'))
        return

    username = prompt({
        'type'    : 'list',
        'message' : t('prompt.select', 'user'),
        'choices' : [user.get('username') for user in users],
        'name'    : 'username'
    }).get('username')

    proceed = prompt({
        'type'    : 'confirm',
        'message' : t('prompt.confirm', 'delete_user', username = username),
        'name'    : 'proceed',
        'default' : False
    }).get('proceed')

    if not proceed: 
        console.print(t('prompt', 'cancel'))
        return

    config.delete('users', 'username', username)
    console.print(t('succes.user', 'deleted'))

@click.command()
@auth_cli()
def create_database(username: str) -> None:
    database_name = prompt({
        'type'    : 'input',
        'message' :  t('prompt.enter', 'database_name'),
        'name'    : 'database_name'
    }).get('database_name')
    
    if any(database.get('name') == database_name for database in config.get('databases')):
        console.print('\n' + t('errors.database', 'already_exist', database_name = database_name), style = 'bold red')
        return

    database = Moonlight(database_name)

    config.push('databases', {
        'id'         : generate_uuid(),
        'name'       : database_name,
        'path'       : database.filename,
        'logs_path'  : database.logs_path,
        'created_at' : get_now_datetime(),
        'author'     : username
    })

    console.print('\n' + t('success.database', 'created'), style = 'bold green')


@click.group()
def cli() -> None: ...

cli.add_command(serve)
cli.add_command(configure)
cli.add_command(locale)
cli.add_command(create_user)
cli.add_command(delete_user)
cli.add_command(create_database)

if __name__ == '__main__':
    cli()