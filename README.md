# fastensource

fastensource is a tool for downloading projects sources
from **Maven**, **PyPI**, and **apt**.

## Getting Started

In order to install fastensource run `python setup.py install`.

If you want to install it in a virtual environment execute
the following commands:

```bash
pip install virtualenv
virtualenv --python=python3 env
source env/bin/activate
python setup.py install
```
To run the tests execute `python setup.py test`.

## Options

fastensource provides a command line interface with many abilities.
The first positional parameter must be the language for which you want to
download projects. The fasten source can be used with the following
parameters.

```
fastensource {python,java,c} [-h] [-p PROJECTS] [-o OUTPUT] [-v VERSIONS]
                             [-d REQUESTS_DELAY] [-D COMMANDS_DELAY]
                             mode

```

The next table describes the options and their default values.

| Option         | Shortcut | Default Values    | Description                   |
|----------------|----------|-------------------|-------------------------------|
| help           | -h       |                   | show help message             |
| projects       | -p       | FASTEN projects   | csv with projects to download |
| output         | -o       | Maven/PyPI/Debian | directory to save the sources |
| versions       | -v       | versions.json     | file to save timestamps       |
| requests-delay | -d       | 0, 15 (Maven)     | delay for each request        |
| commands-delay | -D       | 0, 10 (Maven)     | delay for each command        |

### Modes

There are three modes.

1. Downloads current versions of projects and their dependencies.
The format of the corresponding csv is:

    ```
    project1
    project2
    project3
    ```
2. Downloads specified versions of projects and their dependencies.
The format of the corresponding csv is:

    ```
    project1;version
    project2;version
    project3;version
    ```
3. Downloads specified versions of projects and all possible versions
of their dependencies. The format of the corresponding csv is:

    ```
    project1,version;dependency1,version1
    project1,version;dependency1,version2
    project1,version;dependency2,version
    ```

### Versions Example

```json
{
    "packages": {
        "Click": {
            "7.0": "Sep 25, 2018"
        },
        "Django": {
            "2.2": "Apr 1, 2019",
            "2.1.7": "Feb 11, 2019"
        }
    },
    "p_names": {}
}
```

## Support

fastensource works only with Python 3.
We have test fastensource in __Debian__ and __Mac OSX__.
For downloading projects from a package manager, you should have
the specific package manager installed.
In __C__ mode, you should also have
[UDD](https://wiki.debian.org/UltimateDebianDatabase/) installed.
