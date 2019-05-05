import sys
from subprocess import Popen, PIPE
from datetime import datetime
from shutil import which
import requests

def get_libio_datetime(dt):
    dt = dt[:dt.find(',')][:-2] + dt[dt.find(','):]
    return datetime.strptime(dt, '%B %d, %Y %H:%M')


def is_program(program):
    """Check whether `program` is on PATH and marked as executable.

    Args:
        program (str): program to check if exists

    Returns:
        bool

    """
    return which(program) is not None


def execute_command(cmd, mes_logs=sys.stdout, err_logs=sys.stderr):
    """Execute a command.

    Log errors in err_logs, and messages to mes_logs.

    Returns:
        exit_code (int): command's exit code
    """
    process = Popen(cmd, shell=True, stdout=PIPE)
    mes = process.communicate()
    exit_code = process.wait()
    mes = mes[0].decode('utf-8')
    if exit_code == 0:
        mes_logs.write(mes + '\n')
    else:
        err_logs.write(mes + '\n')
    return exit_code


def find_name_version_pypi(project):
    """Find the name and the version of a PyPI project.

    Args:
        project (str): project name with version (e.g. Django-1.11)

    Returns:
        name, version (tuple): name and version (e.g. Django,1.11)

    """
    if project.endswith('.zip'):
        project = project[:-4]
    elif project.endswith('.tar.gz'):
        project = project[:-7]
    name = project[:project[:project.find('.')].rfind('-')]
    version = project[project[:project.find('.')].rfind('-') + 1:]
    return (name, version)


def find_name_version_debian(project):
    """Find the name and the version of a Debian project.

    Args:
        project (str): project name with version (e.g. dpkg-1.18.25)

    Returns:
        name, version (tuple): name and version (e.g. dpkg,1.18.25)

    """
    name = project[:project[:project.find('.')].rfind('-')]
    version = project[project[:project.find('.')].rfind('-') + 1:]
    return (name, version)


def remove_duplicates(names, versions, versions_dict):
    """Remove the versions that exist in versions_dict.

    Args:
        names (list): A list with names
        versions (list): A list with versions
        versions_dict (dict): A dict names as keys

    versions_dict example:
        {'name': {'version': 'foo', ...}, ...}

    Returns:
        new_names (list): A list with names
        new_versions (list): A list with versions

    """
    new_names = list()
    new_versions = list()
    for proj in zip(names, versions):
        if proj[0] in versions_dict.keys() and\
           proj[1] in versions_dict[proj[0]].keys():
            continue
        new_names.append(proj[0])
        new_versions.append(proj[1])
    return new_names, new_versions


def requests_get(url):
    """Make a get request using requests package.

    Args:
        url (str): url to do the request

    Raises:
        ConnectionError: If a RequestException occurred.

    Returns:
        response (str): the response from the get request

    """
    try:
        r = requests.get(url)
    except requests.exceptions.RequestException:
        raise ConnectionError
    return r


def requests_get_handler(url):
    """Handle requests get request.

    Args:
        url (str): url to do the request

    Returns:
        response (str): the response from the get request

    """
    try:
        r = requests_get(url)
    except ConnectionError:
        print(('A connection error occurred. '
              'Please check your internet connection!'))
        sys.exit(1)
    return r


def delay(fn):
    """Decorator function to delay the execution of a function.

    The function that use this decorator must have delay as a keyword
    argument.

    """
    def wrapper(*args, **kwargs):
        import time
        seconds = kwargs.get('delay', 0)
        time.sleep(seconds)
        return fn(*args, **kwargs)
    return wrapper


class Error(Exception):
    """Base class for other exceptions"""

class ConnectionError(Error):
    """Raised when a connection error occurred"""
