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
import os
import tempfile
import shutil
from fastensource.commands.command import Command
from fastensource.utils.udd import find_version_timestamp_udd,\
        find_dependencies
from fastensource.utils.helpers import execute_command,\
        find_name_version_debian


class Debian(Command):
    """In Debian we need to handle not only the projects (packages)
       but also the sources. Specifically, when we try to download
       the sources of a package, apt will detect the sources that produce
       this package, and it will download the sources. For instance,
       in the case of libc6 it will download the glibc source. Thus,
       we need to override the _initialize_d_projects method.
    """
    def __init__(self, args):
        self.cmd = 'apt-get source '
        super(Debian, self).__init__(args)

    def _set_package_manager(self):
        self.package_manager = 'apt-get'

    def _initialize_d_projects(self):
        """In d_projects set we need the values from p_names and not
        from versions dict because in the versions are the downloaded sources
        info and not the info of the projects.

        """
        for project, versions in self.p_names.items():
            for version in versions:
                self.d_projects.add(tuple([project, version]))

    def _update_p_names(self, project, version):
        """Update the p_names in versions file.

        """
        if project in self.p_names.keys() and \
           version not in self.p_names[project]:
            self.p_names[project].append(version)
            self.write_versions_file()
        elif project not in self.p_names.keys():
            self.p_names[project] = [version]

    def _find_name_version(self, project):
        return find_name_version_debian(project)

    def _find_version_timestamp(self, project, version, delay):
        return find_version_timestamp_udd(project, version)

    def _download(self, project, version):
        """Download project and add its dependencies to self.projects.

         This function orchestrates the download process for Debian projects.
         The process consists of the following steps:
             1. Download project and its dependencies.
             2. Find downloaded version, timestamp
             3. Update versions file
             4. Find dependencies and add them in self.projects
                - Check if a dependency already exists in versions file

        Args:
            project (str): Project name
            version (str): Project version

        """
        if version == 'Unspecified':
            cmd = self.cmd + ' ' + project
        else:
            cmd = self.cmd + ' ' + project + '=' + version
            # Update the p_names only if a specific version is given.
            self._update_p_names(project, version)
        prevdir = os.getcwd()
        with tempfile.TemporaryDirectory() as dirpath:
            os.chdir(dirpath)
            # Step 1
            exit_code = execute_command(cmd, self.messages, self.errors)
            if exit_code == 0:
                project_dir_name = next(os.walk('.'))[1][0]
                # Step 2
                name, version = self._find_name_version(project_dir_name)
                # Check if project-version already exists
                if name not in self.versions.keys() or\
                   version not in self.versions[name].keys():
                    timestamp = self._find_version_timestamp(name, version,
                                                            delay=0)
                    # Step 3
                    os.chdir(prevdir)
                    self._update_versions([name], [version], [timestamp])
                    os.chdir(dirpath)
                # Move to parent directory
                project_dir_new_path = prevdir + '/' + project_dir_name
                if not os.path.isdir(project_dir_new_path):
                    os.makedirs(project_dir_new_path)
                    files = os.listdir('.')
                    for f in files:
                        shutil.move(f, project_dir_new_path)
                # Step 4
                dependencies = find_dependencies(name, version)
                # Add dependencies to projects
                for dep in dependencies:
                    if dep not in self.d_projects:
                        self.projects.append(dep)
        os.chdir(prevdir)
