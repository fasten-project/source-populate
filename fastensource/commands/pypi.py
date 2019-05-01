from fastensource.commands.command import Command
from fastensource.utils.scrappers import find_version_timestamp_pypi
from fastensource.utils.helpers import execute_command,\
        find_name_version_pypi, remove_duplicates


class Pypi(Command):
    def __init__(self, args):
        self.cmd = 'pip download --no-binary=:all: '
        super(Pypi, self).__init__(args)

    def _set_package_manager(self):
        self.package_manager = 'pip'

    def _find_name_version(self, project):
        return find_name_version_pypi(project)

    def _find_version_timestamp(self, project, version, delay):
        return find_version_timestamp_pypi(project, version,
                                          delay=self.requests_delay)

    def _download(self, project, version):
        """Download project and its dependencies.

         This function orchestrates the download process for PyPI projects.
         The process consists of the following steps:
             1. Download project and its dependencies.
             2. Find downloaded versions, timestamps
             3. Update versions file

        - PyPI handles the dependencies
        - PyPI automatically checks if a project has already been downloaded.

        Args:
            project (str): Project name
            version (str): Project version

        """
        # Step 1
        if version == 'Unspecified':
            cmd = self.cmd + ' ' + project
        else:
            cmd = self.cmd + ' ' + project + '==' + version
        execute_command(cmd, self.messages, self.errors)
        # Step 2
        projects = self._find_downloaded_projects()
        # Checks if any projects has downloaded.
        if len(projects) == 0:
            return
        names, versions = self._find_projects_names_versions(projects)
        # Remove the versions of projects that already exists in versions file.
        names, versions = remove_duplicates(names, versions, self.versions)
        timestamps = self._find_timestamps(names, versions)
        # Step 3
        self._update_versions(names, versions, timestamps)
