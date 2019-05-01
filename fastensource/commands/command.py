"""Module that provides the abstraction for the commands (python, java, c).
"""
import sys
import os
import csv
import json
from pkg_resources import resource_filename
from abc import ABC, abstractmethod
from fastensource.utils.helpers import is_program


class Command(ABC):
    def __init__(self, args):
        self.package_manager = ''
        # Logs
        self.errors = sys.stderr
        self.messages = sys.stdout
        # User arguments
        self.mode = ''
        self.versions_filename = ''
        self.requests_delay = 0
        self.commands_delay = 0
        self.projects_file = ''
        self.output = ''
        # Projects to download
        self.projects = list()
        # Versions file
        self.versions = dict()
        self.p_names = dict()
        # Set of tuples that contain pairs of project, version that we already
        # tried to download. If unspecified provided as a version,
        # then the package manager handles which version to download.
        self.d_projects = set()
        # Execution
        self._set_package_manager()
        if not is_program(self.package_manager):
            self.err('Error: cannot find {}'.format(self.package_manager))
            sys.exit(1)
        self._parse_args(args)
        self.read_versions_file()
        self._initialize_d_projects()
        self._execute()

    @abstractmethod
    def _set_package_manager(self):
        """Make sure that the package manager is declared."""
        pass

    def err(self, error):
        """Method to log erros.

        Args:
            error (str): error message

        """
        self.errors.write(error + '\n')

    def mes(self, message):
        """Method to log messages.

        Args:
            message (str)

        """
        self.messages.write(message + '\n')

    def read_versions_file(self):
        """Read the versions file.

        In case of Debian projects, save the packages sources versions to
        self.versions, and the packages names to self.p_names.
        In PyPI, and Java projects ignore the self.p_names.

        """
        path = os.getcwd() + '/' + self.output + '/' + self.versions_filename
        if os.path.isfile(path):
            with open(path, 'r') as f:
                data = json.load(f)
                self.versions = data['packages']
                self.p_names = data['p_names']

    def write_versions_file(self):
        """Write the versions file.

        """
        path = os.getcwd() + '/' + self.versions_filename
        data = {'packages': self.versions, 'p_names': self.p_names}
        with open(path, 'w') as f:
            json.dump(data, f)

    def _initialize_d_projects(self):
        """Initialize d_projects set with the projects and versions from
        versions file.

        """
        for project, versions in self.versions.items():
            for version,_ in versions.items():
                self.d_projects.add(tuple([project, version]))

    def _parse_args(self, args):
        """Parse user's arguments.

        """
        self.mode = args.mode
        if self.mode not in ('1', '2', '3'):
            self.err('Error: Invalid mode (Valid modes: 1, 2, 3)')
            sys.exit(1)
        self.mode = int(self.mode)
        self.projects_file = args.projects
        self.versions_filename = args.versions
        self.output = args.output
        self.requests_delay = args.requests_delay
        self.commands_delay = args.commands_delay
        self._get_projects()

    def _get_projects(self):
        """Parse the projects to download from projects_file.

        We parse the projects based on the specified mode.

        """
        # Default projects
        if self.projects_file.endswith('.dat'):
            path = resource_filename('fastensource',
                                     'data/' + self.projects_file)
        else:
            path = self.projects_file
        with open(path, 'r') as f:
            if self.mode == 1:
                self.projects = [tuple([row[0], 'Unspecified'])
                                 for row in csv.reader(f, delimiter=';')]
            elif self.mode == 2:
                self.projects = [tuple([row[0], row[1]])
                                 for row in csv.reader(f, delimiter=';')]
            elif self.mode == 3:
                for row in csv.reader(f, delimiter=';'):
                   self.projects.append(
                       tuple([row[0].split(',')[0], row[0].split(',')[1]])
                   )
                   self.projects.append(
                       tuple([row[1].split(',')[0], row[1].split(',')[1]])
                   )

    def _find_name_version(self, project):
        """Find project name and version from a string that contains both of
           them.

        Args:
            project (str): variable that contains both the project and the
                version (e.g. Django-1.11)

        Returns:
            name (str): project name (e.g. Django)
            version (str): project version (e.g. 1.11)

        """
        raise NotImplementedError

    @abstractmethod
    def _find_version_timestamp(self, name, version, delay):
        """Find the timestamp of a specific version of a project.

        Args:
            name (str): project name
            version (str): project version
            delay (int): seconds to sleep

        Returns:
            timestamp (str): release timestamp (e.g. Apr 05, 2019)

        """
        pass

    def _find_downloaded_projects(self):
        """Find the downloaded projects in the current directory.

        Returns:
            projects (str): downloaded projects (e.g. Django-11.1)

        """
        projects = os.listdir('.')
        if self.versions_filename in projects:
            projects.remove(self.versions_filename)
        return projects

    def _find_projects_names_versions(self, projects):
        """For each project find the name, and version.

        Args:
            projects (list): List of projects names-versions (e.g. Django-1.11)

        Returns:
            names (list): List of projects names (e.g. Django)
            versions (list): List of projects versions (e.g. 1.11)
        """
        names_versions = list(zip(*[self._find_name_version(proj)
                                    for proj in projects]))
        return names_versions[0], names_versions[1]

    def _find_timestamps(self, names, versions):
        """For each project version find the release timestamp.

        Args:
            names (list): List of projects names (e.g. Django)
            versions (list): List of projects versions (e.g. 1.11)

        Returns:
            timestamps (list): List of projects versions release timestamps
                (e.g. Apr 02, 2019)

        """
        return [self._find_version_timestamp(proj[0], proj[1],
                                            delay=self.requests_delay)
                for proj in zip(names, versions)]

    def _update_versions(self, names, versions, timestamps):
        """Update the versions file.

        Args:
            names (list): List of projects names (e.g. Django)
            versions (list): List of projects versions (e.g. 1.11)
            timestamps (list): List of projects versions release timestamps

        """
        for entry in zip(names, versions, timestamps):
            # Check if project already exists
            if entry[0] not in self.versions.keys():
                self.versions[entry[0]] = {
                    entry[1]: entry[2]
                }
            # Check if version already exists
            elif entry[1] not in self.versions[entry[0]].keys():
                self.versions[entry[0]][entry[1]] = entry[2]
        self.write_versions_file()

    @abstractmethod
    def _download(self, project, version):
        """Download project and handle its dependencies.

        Args:
            project (str): Project name
            version (str): Project version

        """
        pass

    def _execute(self):
        """Download the chosen projects.

        This will:
            - Create a dir to save the projects if does not exists.
            - Change working directory to that directory.
            - Before trying to download a project check if already exists.
            - The self.projects list will be updated by _download method.

        """
        if not os.path.exists(self.output):
            os.makedirs(self.output)
        os.chdir(self.output)
        while len(self.projects) > 0:
            project = self.projects.pop()
            if project not in self.d_projects:
                self._download(project[0], project[1])
                self.d_projects.add(project)
                self.mes('')
