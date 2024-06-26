from sanic.worker.loader  import AppLoader
from sanic                import Sanic
from functools            import partial
from InquirerPy           import prompt
from InquirerPy.validator import NumberValidator
from rich.console         import Console
from rich.table           import Table

from Moonlight.config.config      import config, app_data
from Moonlight.api.api            import create_application
from Moonlight.messages.messages  import t, Style
from Moonlight.cli.decorators     import auth_cli
from Moonlight.core.moonlight     import Moonlight
from Moonlight.core.methods       import Methods
from Moonlight.languages.moonfile import Moonfile
from Moonlight.core.tools         import is_file_exist
from Moonlight.config.paths       import make_moonfile_path

import asyncio
import click

console = Console()

@click.command()
def serve() -> None:
    users: list[dict] = config.get('users')

    if not next((user.get('permissions') == 'administrator' for user in users), None):
        console.print(t('errors.user.need_admin'), style = Style['ERROR'].value)
        return

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
def configure() -> None:
    if is_file_exist(make_moonfile_path(app_data.get('moonfile'))):
        use_moonfile: bool = prompt({
            'type'    : 'confirm',
            'message' : t('prompt.confirm.use_moonfile'),
            'name'    : 'use_moonfile',
            'default' : False
        }).get('use_moonfile')

        if use_moonfile:
            moonfile: Moonfile = Moonfile()
            moonfile.parse_config()
            moonfile.compile()

            console.print('\n' + t('success.application.configured'), style = Style['SUCCESS'].value)
            return

    host = prompt({
        'type'    : 'input',
        'message' :  t('prompt.enter.host'),
        'name'    : 'host',
        'default' : '127.0.0.1'
    }).get('host')

    port = prompt({
        'type'     : 'input',
        'message'  :  t('prompt.enter.port'),
        'name'     : 'port',
        'default'  : '3000',
        'validate' : NumberValidator()
    }).get('port')

    loggers = prompt({
        'type'    : 'checkbox',
        'message' : t('prompt.select.loggers'),
        'choices' : ['Info', 'Success', 'Warning', 'Error'],
        'name'    : 'loggers'
    }).get('loggers')

    Methods.configure(host, port, loggers)

    console.print('\n' + t('success.application.configured'), style = Style['SUCCESS'].value)

@click.command()
def locale() -> None:
    locale = prompt({
        'type'    : 'list',
        'message' : t('prompt.select.locale'),
        'choices' : app_data.get('locales'),
        'name'    : 'locale'
    }).get('locale')

    app_data.set('current_locale', locale)

@click.command()
def create_user() -> None:
    users = config.get('users')

    username = prompt({
        'type'    : 'input',
        'message' :  t('prompt.enter.username'),
        'name'    : 'username'
    }).get('username')

    if any(user.get('username') == username for user in users):
        console.print(t('errors.user.already_exist', username = username))
        return

    password = prompt({
        'type'    : 'password',
        'message' : t('prompt.enter.password'),
        'name'    : 'password'
    }).get('password')

    permissions = prompt({
        'type'    : 'list',
        'message' : t('prompt.select.permissions', username = username),
        'choices' : [t('permissions.viewer'), t('permissions.editor'), t('permissions.admin')],
        'name'    : 'permissions'
    }).get('permissions')
        
    Methods.create_user(username, password, permissions)
    
    console.print(t('success.user.created'))

@click.command()
def delete_user() -> None:
    users = config.get('users')

    if len(users) == 0:
        console.print(t('errors.user.no_one'))
        return

    username = prompt({
        'type'    : 'list',
        'message' : t('prompt.select.user'),
        'choices' : [user.get('username') for user in users],
        'name'    : 'username'
    }).get('username')

    if username == app_data.get('self_admin'):
        console.print(t('errors.user.self_admin', self_admin_name = username), style = Style['ERROR'].value)
        return

    proceed = prompt({
        'type'    : 'confirm',
        'message' : t('prompt.confirm.delete_user', username = username),
        'name'    : 'proceed',
        'default' : False
    }).get('proceed')

    if not proceed: 
        console.print(t('prompt.cancel'))
        return

    Methods.delete_user(username)
    console.print(t('success.user.deleted'))

@click.command()
@auth_cli('administrator')
def create_database(username: str) -> None:
    database_name = prompt({
        'type'    : 'input',
        'message' :  t('prompt.enter.database_name'),
        'name'    : 'database_name'
    }).get('database_name')
    
    if any(database.get('name') == database_name for database in config.get('databases')):
        console.print('\n' + t('errors.database.already_exist', database_name = database_name), style = Style['ERROR'].value)
        return

    Moonlight(database_name, username)

    console.print('\n' + t('success.database.created'), style = Style['SUCCESS'].value)

@click.command()
@auth_cli('administrator')
def delete_database(username: str) -> None:
    databases: list[dict] = config.get('databases')

    if len(databases) == 0:
        console.print('\n' + t('errors.database.no_one'), style = Style['ERROR'].value)
        return

    database_name = prompt({
        'type'    : 'list',
        'message' : t('prompt.select.database'),
        'choices' : [database.get('name') for database in databases],
        'name'    : 'database_name'
    }).get('database_name')

    database_to_delete = next((database for database in databases if database.get('name') == database_name), None)

    if database_to_delete.get('author') not in (username, app_data.get('self_admin')):
        console.print('\n' + t('errors.database.not_author', database_name = database_name), style = Style['ERROR'].value)
        return

    proceed = prompt({
        'type'    : 'confirm',
        'message' : t('prompt.confirm.delete_database', database_name = database_name),
        'name'    : 'proceed',
        'default' : False
    }).get('proceed')

    if not proceed: 
        console.print(t('prompt.cancel'))
        return

    database = Moonlight(database_name)

    database.logger.stop()

    Methods.delete_database(database_name, database.filename, database.logs_path)
    
    console.print('\n' + t('success.database.deleted'), style = Style['SUCCESS'].value)

@click.command()
def databases() -> None:
    databases: list[dict] = config.get('databases')

    if len(databases) == 0:
        console.print('\n' + t('errors.database.no_one'), style = Style['ERROR'].value)
        return

    table = Table(
        title = t('tables.databases.title'), 
        expand = True,
        show_lines = True,
        padding = 1
    )

    table.add_column(t('tables.databases.id'),         justify = 'center', style = Style['ID_FIELD'].value)
    table.add_column(t('tables.databases.name'),       justify = 'center', style = Style['SUCCESS'].value)
    table.add_column(t('tables.databases.author'),     justify = 'center', style = Style['AUTHOR_FIELD'].value)
    table.add_column(t('tables.databases.created_at'), justify = 'center', style = Style['CREATED_AT_FIELD'].value)

    for database in databases:
        table.add_row(
            str(database.get('id')), 
            str(database.get('name')), 
            str(database.get('author')),
            str(database.get('created_at'))
        )

    console.print(table)

@click.command()
@auth_cli('viewer')
def database(username: str) -> None:
    databases: list[dict] = config.get('databases')

    if len(databases) == 0:
        console.print('\n' + t('errors.database.no_one'), style = Style['ERROR'].value)
        return

    database_name = prompt({
        'type'    : 'list',
        'message' : t('prompt.select.database'),
        'choices' : [database.get('name') for database in databases],
        'name'    : 'database_name'
    }).get('database_name')

    database_to_show = next((database for database in databases if database.get('name') == database_name), None)

    table = Table(
        title = database_to_show.get('name'), 
        expand = True,
        show_lines = True,
        padding = 1
    )

    data_to_show = asyncio.run(Moonlight(database_to_show.get('name')).all())

    if len(data_to_show) == 0:
        console.print('\n' + t('info.database.empty'), style = Style['INFO'].value)
        return

    columns = ['id'] + sorted({ key for data in data_to_show for key in data.keys() if key != 'id' })

    for column in columns:      table.add_column(column, justify = 'center', style = Style['DEFAULT_FIELD'].value)
    for record in data_to_show: table.add_row(*[str(record.get(column, f'[bold red]None')) for column in columns])

    console.print(table)

@click.command()
@auth_cli('viewer')
def create_key(username: str) -> None:
    token_data: dict[str, str] = Methods.create_token(username)

    console.print_json(data = token_data)

@click.group()
def cli() -> None: ...

cli.add_command(serve)
cli.add_command(configure)
cli.add_command(locale)
cli.add_command(create_user)
cli.add_command(delete_user)
cli.add_command(create_database)
cli.add_command(delete_database)
cli.add_command(databases)
cli.add_command(database)
cli.add_command(create_key)

if __name__ == '__main__':
    cli()