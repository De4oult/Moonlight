from os.path import dirname, abspath, join
from os      import getcwd

from Moonlight.core.tools import add_ext, get_filename_from_path


head_path: str = dirname(dirname(abspath(__file__)))
exec_path: str = getcwd()

databases_path: str = join(exec_path, 'databases')
logging_path:   str = join(exec_path, 'logs')
locales_path:   str = join(head_path, 'locales')

conf_path: str = join(exec_path, 'config.json')
data_path: str = join(head_path, 'sources', 'app_data.json')

def make_database_path(filename: str) -> str:
    '''Creates the full path to the database file based on the file name'''
    return join(databases_path, add_ext(get_filename_from_path(filename), '.json'))

def make_logging_path(filename: str) -> str:
    '''Creates the full path to the logging file based on the file name.'''    
    return join(logging_path, add_ext(get_filename_from_path(filename), '.log'))

def make_locale_path(locale: str) -> str:
    '''Creates the full path to the localization file based on the selected locale.'''    
    return join(locales_path, add_ext(locale, '.json'))

def make_moonfile_path(moonfile: str) -> str:
    '''Creates the full path to the Moonlight file based on the file name.'''    
    return join(exec_path, moonfile)