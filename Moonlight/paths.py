from os.path import dirname, abspath, join
from os      import getcwd

def head_directory() -> str: return dirname(dirname(abspath(__file__)))
def exec_directory() -> str: return getcwd()

head_path: str = head_directory()
exec_path: str = exec_directory()
conf_path: str = join(head_directory(), 'config.json')

databases     : str = join(head_directory(), 'databases.json')
databases_path: str = join(head_directory(), 'databases')
logging_path  : str = join(head_directory(), 'logging')
