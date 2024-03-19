from sanic.worker.loader import AppLoader
from sanic               import Sanic
from functools           import partial

from Moonlight.config import *
from Moonlight.api    import create_application

import secrets
import click

@click.command()
@click.option('--host', default = '127.0.0.1', help = 'database manager IP address')
@click.option('--port', default = 3000,        help = 'database manager port')
def run(host, port):
    loader = AppLoader(factory = partial(create_application))
    
    app = loader.load()

    app.prepare(
        host       = host,
        port       = int(port),
        access_log = False
    )

    Sanic.serve(
        primary = app, 
        app_loader = loader
    )

@click.command()
@click.option('--generate-key', default = True, help = 'generates key for requests on database')
def auth(generate_key):
    config = load_config()
    config['api_key'] = secrets.token_hex(32)

    save_config(config)
    click.echo('API token updated: %s' % config.get('api_key'))

@click.group()
def cli():
    pass

cli.add_command(run)
cli.add_command(auth)

if __name__ == '__main__':
    cli()