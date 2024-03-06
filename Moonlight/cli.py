import click

from api import app

@click.command()
@click.option('--host', default = '127.0.0.1', help = 'database manager IP address')
@click.option('--port', default = 3000, help = 'database manager port')
def run(host, port):
    app.run(
        host       = host,
        port       = int(port),
        access_log = False
    )

if __name__ == '__main__':
    run()