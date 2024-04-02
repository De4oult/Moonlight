from os.path import dirname, abspath, join
from os      import getcwd

from Moonlight.tools import strip_ext, add_ext

def head_directory() -> str: return dirname(dirname(abspath(__file__)))
def exec_directory() -> str: return getcwd()

head_path: str = head_directory()
exec_path: str = exec_directory()
conf_path: str = join(head_directory(), 'config.json')
data_path: str = join(head_directory(), 'app_data.json')

databases     : str = join(head_directory(), 'databases.json')
databases_path: str = join(exec_directory(), 'database')
logging_path  : str = join(exec_directory(), 'logs')

locales_path: str = join(head_directory(), 'Moonlight', 'locales')

def make_database_path(filename: str) -> str: return join(databases_path, strip_ext(filename, '.json'))
def make_logging_path(filename: str)  -> str: return join(logging_path,   strip_ext(filename, '.log'))
def make_locale_path(locale: str)     -> str: return join(locales_path,   add_ext(locale,   '.json'))