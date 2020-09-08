"""CLI arguments definition.
"""
#
# Copyright (c) 2018-2020 FASTEN.
#
# This file is part of FASTEN
# (see https://www.fasten-project.eu/).
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
import argparse
import importlib
import sys


def get_parser():
    """Set parser arguments for fastensource.

    Returns:
        parser
    """
    parser = argparse.ArgumentParser(description=(
                                     'fastensource is a tool for downloading '
                                     'packages from package managers '
                                     '(PyPY -- Python, Maven -- Java, apt - C) '
                                     'for FASTEN project. '
                                     'It provides a CLI with many abilities. '
                                     'For more information use the -h option.')
    )
    # languages -- package managers, you must provide at least one.
    subparsers = parser.add_subparsers(title='languages')
    python = subparsers.add_parser('python',
                                   description=(
                                    'Download packages from PyPI (python). '
                                    'It will download the tarballs of the '
                                    'given projects.'
                                   )
    )
    java = subparsers.add_parser('java',
                                   description=(
                                    'Download packages from Maven (Java). '
                                    'It will download the jars of the given '
                                    'projects.'
                                    'Only java packages will be downloaded. '
                                   )
    )
    c = subparsers.add_parser('c',
                                   description=(
                                    'Download packages from apt (C). '
                                    'It will download the debian sources '
                                    ' of the given projects.'
                                    'Only c packages will be downloaded. '
                                   )
    )
    for subcommand in [('python', 'PyPI'), ('java', 'Maven'), ('c', 'Debian')]:
        locals()[subcommand[0]].add_argument('mode',
                        help=(
                         'There are three modes.\n'
                         '1. Downloads current versions of projects and their '
                         'dependencies.\n'
                         '2. Downloads specified versions of projects and '
                         'their dependencies.'
                         '3. Downloads specified versions of projects and '
                         'all possible versions of their dependencies.'
                        )
        )
        locals()[subcommand[0]].add_argument('-p', '--projects',
                        default=subcommand[1] + '.dat',
                        help=(
                         'Specify which projects to download using a '
                         'csv file with a specific format.'
                         'For more information about the format please '
                         'check the README.'
                        )
        )
        locals()[subcommand[0]].add_argument('-o', '--output',
                        default=subcommand[1],
                        help=(
                         'Directory to save the downloaded sources.'
                        )
        )
        locals()[subcommand[0]].add_argument('-v', '--versions',
                        default='versions.json',
                        help=(
                         'File to save timestamps.'
                        )
        )
        requests_delay = 15 if subcommand[1] == 'Maven' else 0
        commands_delay = 10 if subcommand[1] == 'Maven' else 0
        locals()[subcommand[0]].add_argument('-d', '--requests-delay',
                        default=requests_delay,
                        help=(
                         'Delay for each request.'
                        )
        )
        locals()[subcommand[0]].add_argument('-D', '--commands-delay',
                        default=commands_delay,
                        help=(
                         'Delay for each command.'
                        )
        )
        module = importlib.import_module(
            'fastensource.commands.' + subcommand[1].lower()
        )
        _func = getattr(module, subcommand[1].capitalize())
        locals()[subcommand[0]].set_defaults(func=_func)
    return parser
