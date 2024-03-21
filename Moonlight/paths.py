from os.path import dirname, abspath, join
from os      import getcwd

def head_directory() -> str: return dirname(dirname(abspath(__file__)))
def exec_directory() -> str: return getcwd()

head_path: str = head_directory()
exec_path: str = exec_directory()
conf_path: str = join(head_directory(), 'config.json')

databases     : str = join(head_directory(), 'databases.json')
databases_path: str = join(exec_directory(), 'database')
logging_path  : str = join(exec_directory(), 'logs')

def make_database_path(filename: str) -> str: return join(databases_path, filename + '' if filename.endswith('.json') else filename + '.json')
def make_logging_path(filename: str)  -> str: return join(logging_path,   filename + '' if filename.endswith('.log')  else filename + '.log')