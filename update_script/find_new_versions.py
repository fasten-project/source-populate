#! /usr/bin/env python
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

"""Find new versions for packages downloaded by fastensource
using versions.json
"""


import sys
import argparse
import json
import csv
from datetime import datetime
from fastensource.utils.scrappers import find_last_version_maven,\
        find_last_version_pypi


def check_if_package_exists(package, packages):
    """Check if a package exist in the given packages

    If packages is equals to False then return always True because it means
    that the user did not provide packages to specify from which packages
    wants to find new versions.

    Returns:
        bool
    """
    if not packages:
        return True
    if package in packages:
        return True
    return False


def find_youngest_version(versions):
    versions_datetimes = [datetime.strptime(timestamp, '%b %d, %Y')
                          for timestamp in versions.values()]
    # Youngest timestamp
    youngest = min(versions_datetimes).strftime('%b %-d, %Y')
    # Return the version of youngest timestamp
    return list(versions.keys())[list(versions.values()).index(youngest)]


def find_new_versions(versions, packages, find_last_version, delay):
    # keys are the packages and values are dicts with version: timestamp
    results = set()
    for key, value in versions.items():
        if check_if_package_exists(key, packages):
            youngest_version = find_youngest_version(value)
            last_version = find_last_version(key, delay=delay)
            if youngest_version != last_version:
                results.add((key, last_version))
    return results


def main():
    parser = argparse.ArgumentParser(description=(
                                     'Find new versions of packages '
                                     'downloaded by fastensource.'))
    parser.add_argument('versions', help='JSON file with versions timestamps')
    parser.add_argument('language', help='python, java, or c')
    parser.add_argument('-p', '--packages',
                        help='List of packages to check for new versions')
    parser.add_argument('-o', '--output',
                        help='Filename to save new versions')
    parser.add_argument('-d', '--delay',
                        help='Seconds to wait before each request',
                        default=5)
    args = parser.parse_args()

    if args.language not in ('java', 'python', 'c'):
        print('Please give java, python, or c as language')
        sys.exit(1)
    else:
        language = args.language

    with open(args.versions, 'r') as f:
        versions = json.load(f)
        versions = versions['packages']

    if args.packages:
        with open(args.packages) as f:
            packages = f.readlines()
            packages = [x.strip() for x in packages]
    else:
        packages = False

    # We could use attr here
    if language == 'java':
        find_last_version = find_last_version_maven
    elif language == 'python':
        find_last_version = find_last_version_pypi
    else:
        raise NotImplementedError

    new_versions = find_new_versions(versions, packages, find_last_version,
                                     args.delay)

    if args.output:
        with open(args.output, 'w') as f:
            csv_output = csv.writer(f, delimiter=';')
            for row in new_versions:
                csv_output.writerow(row)
    else:
        for row in new_versions:
            print('{},{}'.format(row[0], row[1]))


if __name__ == '__main__':
    main()
