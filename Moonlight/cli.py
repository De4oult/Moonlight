from sanic.worker.loader import AppLoader
from sanic               import Sanic
from functools           import partial
from InquirerPy          import prompt

from Moonlight.config     import config, app_data
from Moonlight.tools      import password_hash
from Moonlight.api        import create_application
from Moonlight.messages   import t
from Moonlight.decorators import auth_cli
from Moonlight.moonlight  import Moonlight

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


    print(t('success.application', 'configured'))

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

    for user in users:
        if user.get('username') == username:
            print(t('errors.user', 'already_exist', username = username))
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
        
    config.set('users', [*users, new_user])
    print(t('success.user', 'created'))

@click.command()
def delete_user() -> None:
    users = config.get('users')

    if len(users) == 0:
        print(t('errors.user', 'no_one'))
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
        print(t('prompt', 'cancel'))
        return

    config.set('users', [user for user in users if user.get('username') != username])

@click.command()
# @auth_cli()
def create_database() -> None:
    print('Woho!')

    database = Moonlight('torvus')

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