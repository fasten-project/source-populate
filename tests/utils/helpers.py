from time import time
from fastensource.utils.helpers import is_program, execute_command,\
        find_name_version_pypi, find_name_version_debian, remove_duplicates,\
        delay


@delay
def use_delay(delay):
    pass


def test_is_program():
    assert is_program('pwd') is True, 'Should be true'
    assert is_program('aadcsdvsdfasa') is False, 'Should be true'


def test_execute_command():
    assert execute_command('pwd') == 0, 'Should be 0'
    assert execute_command('aadcsdvsdfasa') != 0, 'Should not be 0'


def test_find_name_version_pypi():
    projects = {
        'Django-2.2.tar.gz': ('Django', '2.2'),
        'Django-2.1rc1.tar.gz': ('Django', '2.1rc1'),
        'setuptools-41.0.1.zip': ('setuptools', '41.0.1'),
        'pytz-2019.1.tar.gz': ('pytz', '2019.1')
    }
    for key, value in projects.items():
        assert find_name_version_pypi(key) == value,\
            'Should be {}'.format(value)


def test_find_name_version_debian():
    projects = {
        'glibc-2.24': ('glibc', '2.24'),
        'debianutils-4.8.1.1': ('debianutils', '4.8.1.1'),
        'gcc-6-6.3.0': ('gcc-6', '6.3.0'),
        'sensible-utils-0.0.9+deb9u1': ('sensible-utils', '0.0.9+deb9u1'),
        'tar-1.29b': ('tar', '1.29b')
    }
    for key, value in projects.items():
        assert find_name_version_debian(key) == value,\
            'Should be {}'.format(value)


def test_remove_duplicates():
    names = ['Django', 'Django', 'Click']
    versions = ['2.2', '1.11', '7.0']
    versions_dict = {
        'Django': {
            '2.2': 'timestamp'
        },
        'Click': {
            '7.1': 'timestamp'
        }
    }
    new_names = ['Django', 'Click']
    new_versions = ['1.11', '7.0']
    result = (new_names, new_versions)
    assert remove_duplicates(names, versions, versions_dict) == result,\
        'Should be {}'.format(result)


def test_delay():
    start_time = time()
    use_delay(delay=1)
    elapsed_time = time() - start_time
    assert elapsed_time > 1, 'Should be greater that 1'
