from sanic.worker.loader import AppLoader
from sanic               import Sanic
from functools           import partial

from Moonlight.api import create_application

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

@click.group()
def cli():
    pass

cli.add_command(run)

if __name__ == '__main__':
    cli()