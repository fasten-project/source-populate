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
from fastensource.commands.command import Command
from fastensource.utils.scrappers import find_version_timestamp_maven
from fastensource.utils.maven import find_last_version, find_dependencies,\
        download_maven_jar, get_pom_xml

class Maven(Command):
    def __init__(self, args):
        # url to download projects
        self.url = 'http://central.maven.org/maven2/'
        # url to find versions
        self.url_v = 'https://mvnrepository.com/artifact/'
        super(Maven, self).__init__(args)

    def _set_package_manager(self):
        self.package_manager = 'mvn'

    def _find_version_timestamp(self, project, version, delay):
        return find_version_timestamp_maven(project, version, delay)

    def _download(self, project, version):
        """Download project and add its dependencies to self.projects.

        This function orchestrates the download process for Maven projects.
        The process consists of the following steps:
            1. Find the last version (if the version is Undefined) of the
                project and check if exists in d_projects
            2. Download the jar
            3. Find downloaded timestamp
            4. Find the dependencies.
            5. Check if a dependency already exists in d_projects.
                If not then add a new dependency to self.projects
            6. Update versions file
        """
        # Step 1
        if version == 'Unspecified':
            version = find_last_version(self.url_v, project,
                                        delay=self.requests_delay)
            if version == 'Not Found':
                self.err('No version found for {}'.format(project))
                return
        if tuple([project, version]) in self.d_projects:
            return
        # Step 2
        download_maven_jar(self.url, project, version,
                           delay=self.requests_delay)
        # Step 3
        timestamp = self._find_version_timestamp(project, version,
                                                 delay=self.requests_delay)
        # Step 4
        pom = get_pom_xml(self.url, project, version,
                          delay=self.requests_delay)
        dependencies = find_dependencies(pom, self.commands_delay)
        # Step 5
        for dep in dependencies:
            if dep not in self.d_projects:
                self.mes('Add {} {} to projects'.format(dep[0], dep[1]))
                self.projects.append(dep)
        # Step 6
        self._update_versions([project], [version], [timestamp])
        self.mes('Successfully downloaded {} {}'.format(project, version))
