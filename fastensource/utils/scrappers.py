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
from lxml import html
from fastensource.utils.helpers import delay, requests_get_handler


def libio_parser(content):
    """From the page content return a list of tuples with
    version, timestamp.
    """
    tree = html.fromstring(content)
    element = '//table[@class="table"]//tr/td//text()'
    elements = tree.xpath(element)
    elements = [e.strip() for e in elements
                if e.strip() != ''
                and e.strip().find('Browse source on')
                and e.strip().find('View diff between')
                ]
    return list(zip(elements[0::2], elements[1::2]))


def get_version_timestamp_libio(pkg_mng, package, version):
    """Return version timestamp using libio.
    """
    url = 'https://libraries.io/{}/{}/versions'.format(pkg_mng, package)
    for i in range(1, 100):
        page = requests_get_handler(url + '?page=' + str(i))
        if page.status_code == 404:
            print('{} not found'.format(package))
            return ""
        elements = libio_parser(page.content)
        for versions in elements:
            if version == versions[0]:
                return versions[1]
        if len(elements) == 0:
            break
    print('{} of {} not found'.format(version, package))
    return ""


def pypi_parser(content):
    """From the page content return a list of tuples with
    version, timestamp.
    """
    tree = html.fromstring(content)
    releases_element = '//p[@class="release__version"]//text()'
    timestamps_element = '//p[@class="release__version-date"]//text()'
    releases = tree.xpath(releases_element)
    timestamps = tree.xpath(timestamps_element)
    releases = [e.strip() for e in releases
                if e.startswith('\n') and e.strip() != '']
    timestamps = [e.strip() for e in timestamps if e.strip() != '']
    return list(zip(releases, timestamps))


@delay
def find_version_timestamp_pypi(package, version, delay):
    """Return version timestamp using PyPI's website.
    """
    url = 'https://pypi.org/project/{}/#history'.format(package)
    page = requests_get_handler(url)
    if page.status_code == 404:
        print('{} not found'.format(package))
        return ""
    elements = pypi_parser(page.content)
    for versions in elements:
        if version == versions[0]:
            return versions[1]
    print('{} of {} not found'.format(version, package))
    return ""


@delay
def find_last_version_pypi(package, delay):
    """Return the last version of a package
    """
    url = 'https://pypi.org/project/{}/#history'.format(package)
    page = requests_get_handler(url)
    if page.status_code == 404:
        print('{} not found'.format(package))
        return ""
    elements = pypi_parser(page.content)
    return elements[0][0]


@delay
def find_version_timestamp_maven(package, version, delay):
    """Return version timestamp using mvnrepository.com.

    In case of error return empty string
    """
    url = 'https://mvnrepository.com/artifact/{}/{}/{}'.format(
         package.split(':')[0], package.split(':')[1], version
    )
    page = requests_get_handler(url)
    if page.status_code == 404:
        print('{} not found'.format(package))
        return ""
    tree = html.fromstring(page.content)
    element = '//table[@class="grid"]//text()'
    elements = tree.xpath(element)
    for i, elem in enumerate(elements):
        if elem == 'Date':
            return elements[i+1].split('(')[1].split(')')[0]
    print('{} of {} not found'.format(version, package))
    return ""


@delay
def find_last_version_maven(package, delay):
    """Return the last version of a package

    In case of error return empty string
    """
    url = 'https://mvnrepository.com/artifact/'
    url = url + package.split(':')[0] + '/' + package.split(':')[1]
    page = requests_get_handler(url)
    if page.status_code == 404:
        return ''
    tree = html.fromstring(page.content)
    element = '//a[@class="vbtn release"]//text()'
    elements = tree.xpath(element)
    if len(elements) == 0:
        return ""
    return elements[0]
