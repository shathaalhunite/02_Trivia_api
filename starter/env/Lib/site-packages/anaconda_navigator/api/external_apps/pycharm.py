# Standard library imports
import json
import os
import webbrowser

# Local imports
from anaconda_navigator.api.external_apps.base import BaseInstallableApp
from anaconda_navigator.config import BITS_32, BITS_64, LINUX, MAC
from anaconda_navigator.static import images
from anaconda_navigator.utils.logs import logger


class BasePyCharmApp(BaseInstallableApp):
    def __init__(self, edition, **kwargs):
        self.edition = edition

        super(BasePyCharmApp,
              self).__init__(filename='pycharm', windows_folder_name='JetBrains', needs_license=False, **kwargs)

        self.is_available = BITS_64

    def get_version_from_product_info_file(self):
        # for LINUX and WIN 'product-info.json' is located in app root directory, for MAC - not
        path = os.path.join('Contents', 'Resources') if MAC else ''
        version_path = os.path.join(self.app_directory_path, path, "product-info.json")
        if os.path.exists(version_path):
            with open(version_path, "r") as file:
                return json.load(file)['version']
        else:
            logger.debug('Can\'t find PyCharm version file by path: {0}'.format(version_path))
            return ''

    @property
    def executable(self) -> str:
        """Return an executable command to launch the app."""

        if MAC:
            executable_file = os.path.join(self.app_directory_path, "Contents", "MacOS", self.filename)
            executable_command = f'"{executable_file}"'
        elif LINUX:
            executable_file = os.path.join(self.app_directory_path, "bin", self.filename + ".sh")
            executable_command = f'sh "{executable_file}"'
        else:
            filename = f'{self.filename}{"32" if BITS_32 else "64"}.exe'
            executable_file = os.path.join(self.app_directory_path, "bin", filename)
            executable_command = f'"{executable_file}"'

        if os.path.exists(executable_file):
            return executable_command

        return ''

    def _get_linux_installation_directory(self) -> str:
        root_dirs = ['/opt']

        if os.path.exists('/snap'):
            root_dirs.append('/snap')

        for root in root_dirs:
            for dir_name in os.listdir(root):
                if dir_name.startswith(f'{self.filename}-{self.edition}'):
                    # using Snap user can install several versions, 'current' is a link to newest
                    return os.path.join(root, dir_name, 'current' if root == '/snap' else '')
        return ''

    def _get_windows_installation_directory(self) -> str:
        from anaconda_navigator.external.knownfolders import FOLDERID, get_folder_path

        edition_dir_map = {'professional': 'PyCharm 20', 'community': 'PyCharm Community'}

        if BITS_32:
            program_file_dir = get_folder_path(FOLDERID.ProgramFilesX86)[0]
        else:
            program_file_dir = get_folder_path(FOLDERID.ProgramFilesX64)[0]

        jet_brains_dir = os.path.join(program_file_dir, self.windows_folder_name)

        if os.path.exists(jet_brains_dir):
            for dir_name in os.listdir(jet_brains_dir):
                if dir_name.startswith(edition_dir_map[self.edition]):
                    return os.path.join(jet_brains_dir, dir_name)

        return ''

    def _get_dummy_worker(self):
        return self._process_api.create_process_worker(['python', '--version'])

    @property
    def versions(self):
        """Return the currently installed version of the application."""
        # for the case when app is not installed, but is available to install
        if not self.is_installed:
            return ['']

        return [self.get_version_from_product_info_file()]

    def update_config(self, prefix):
        pass

    def install_extensions(self):
        return self._get_dummy_worker()


class PyCharmProApp(BasePyCharmApp):
    def __init__(self, **kwargs):
        super(PyCharmProApp, self).__init__(
            app_name='pycharm_pro',
            mac_name='PyCharm.app',
            display_name='PyCharm Professional',
            description='A full-fledged IDE by JetBrains for both Scientific '
            'and Web Python development. Supports HTML, JS, and SQL.',
            image_path=images.PYCHARM_ICON_1024_PATH,
            edition='professional',
            is_installation_enabled=True,
            **kwargs
        )

    def install(self):
        webbrowser.open_new_tab('https://www.anaconda.com/pycharm_navigator')


class PyCharmCEApp(BasePyCharmApp):
    def __init__(self, **kwargs):
        super(PyCharmCEApp, self).__init__(
            app_name='pycharm_ce',
            mac_name='PyCharm CE.app',
            display_name='PyCharm Community',
            description='An IDE by JetBrains for pure Python development. '
            'Supports code completion, listing, and debugging.',
            image_path=images.PYCHARM_CE_ICON_1024_PATH,
            edition='community',
            is_installation_enabled=False,
            **kwargs
        )
