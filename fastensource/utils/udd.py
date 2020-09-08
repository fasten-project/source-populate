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
import psycopg2

def find_version_timestamp_udd(package, version, dbname='udd',
                               uname='schaliasos', passwd='udd'):
    """Find the release timestamp of a debian project

    Args:
        project (str): name of project
        version (str): version of project

    Returns:
        data (str): timestamp in the format: Month Date, Year
        (e.g. Apr 17, 2017)

    """
    conn = psycopg2.connect(dbname=dbname, user=uname, password=passwd)
    cursor = conn.cursor()
    cursor.execute("SELECT sources.source, upload_history.version, "
                   "upload_history.date FROM sources INNER JOIN "
                   "upload_history ON upload_history.source = sources.source "
                   "WHERE sources.source = '{}' AND upload_history.version "
                   "= '{}' ORDER BY date DESC LIMIT 1;".format(
                       package, version)
                   )
    rows = cursor.fetchall()
    date = ''
    if len(rows) == 1:
        date = rows[0][2].strftime("%b %d, %Y")
    return date


def resolve_dependency(dependency):
    """Resolve a dependency to a specific version or Unspecified.

    We return Unspecified if we need the last version of a project.

    Args:
        dependency (str): e.g. "gcc-6-base (= 6.3.0-18+deb9u1)"

    Returns:
        results (list): of tuples with package names, and version

    """
    dependency = dependency.strip()
    if '(' in dependency:
        project = dependency[:dependency.find('(')-1]
        comparison = dependency[dependency.find("(")+1:dependency.find(")")]
        symbol = comparison.split(' ')[0]
        version = comparison.split(' ')[1]
        if symbol == '>=':
            return project, 'Unspecified'
        elif symbol == '<=' or symbol == '=':
            return project, version
    else:
        return dependency, 'Unspecified'


def resolve_dependencies(dependencies):
    """Resolve a set of dependencies to a specific versions or Unspecified.

    You can find more for the syntax of Debian dependencies relationships
    here https://www.debian.org/doc/debian-policy/ch-relationships.html

    Args:
        dependencies (str): string with dependencies
        (e.g. "('gcc-6-base (= 6.3.0-18+deb9u1), libc6 (>= 2.11),")

    Returns:
        results (list): of tuples with package names, and version

    """
    results = list()
    if dependencies is not None:
        for dependency in dependencies.split(','):
            dependency = dependency.strip()
            if '|' in dependency:
                results.append(resolve_dependency(dependency.split('|')[0]))
                results.append(resolve_dependency(dependency.split('|')[1]))
            else:
                results.append(resolve_dependency(dependency))
    return results


def find_dependencies(project, version, dbname='udd', uname='schaliasos',
                      passwd='udd'):
    """Find the dependencies of a project

    Args:
        project (str): name of project
        version (str): version of project

    Returns:
        dependencies (list): of tuples with package names, and version

    """
    conn = psycopg2.connect(dbname=dbname, user=uname, password=passwd)
    cursor = conn.cursor()
    cursor.execute("SELECT depends FROM all_packages WHERE "
                   "source = '{}' AND source_version = '{}' LIMIT 1;".format(
                       project, version)
                   )
    rows = cursor.fetchall()
    if len(rows) > 0 and len(rows[0]) > 0:
        dependencies = resolve_dependencies(rows[0][0])
        return dependencies
    return []
