# Standard library imports
import ctypes
import datetime
import io
import json
import os

# Local imports
from anaconda_navigator.api.external_apps.base import BaseInstallableApp
from anaconda_navigator.config import BITS_32, CONF_PATH, LINUX, MAC
from anaconda_navigator.static import images
from anaconda_navigator.utils.conda import run_process
from anaconda_navigator.utils.logs import logger
from anaconda_navigator.utils.py3compat import PY3


class VSCodeApp(BaseInstallableApp):
    def __init__(self, **kwargs):
        super(VSCodeApp, self).__init__(
            app_name='vscode',
            filename='code',
            windows_folder_name='Microsoft VS Code',
            mac_name='Visual Studio Code.app',
            display_name='VS Code',
            description=(
                'Streamlined code editor with support for '
                'development operations like debugging, task '
                'running and version control.'
            ),
            image_path=images.VSCODE_ICON_1024_PATH,
            needs_license=False,
            is_installation_enabled=False,
            **kwargs
        )

        self._vscode_version_value = None

    @property
    def executable(self) -> str:
        """Return an executable command to launch the app."""
        if MAC:
            executable = os.path.join(self.app_directory_path, 'Contents', 'Resources', 'app', 'bin', self.filename)
        elif LINUX:
            if 'share' in self.app_directory_path:
                executable = os.path.join(self.app_directory_path, 'bin', self.filename)
            else:
                executable = os.path.join(self.app_directory_path, 'usr', 'share', 'code', 'bin', self.filename)
        else:
            executable = os.path.join(self.app_directory_path, 'bin', f'{self.filename}.cmd')

        if os.path.exists(executable):
            return f'"{executable}"'

        return ''

    def _get_linux_installation_directory(self) -> str:
        root_dirs = ['/usr/share/']

        if os.path.exists('/snap'):
            root_dirs.append('/snap')

        for root in root_dirs:
            if os.path.exists(os.path.join(root, self.filename)):
                # using Snap user can install several versions, 'current' is a link to newest
                return os.path.join(root, self.filename, 'current' if root == '/snap' else '')
        return ''

    def _get_windows_installation_directory(self) -> str:
        from anaconda_navigator.external.knownfolders import get_folder_path, FOLDERID

        _kernel32 = ctypes.windll.kernel32
        _windir = ctypes.create_unicode_buffer(1024)
        _kernel32.GetWindowsDirectoryW(_windir, 1024)
        _windrive = _windir.value[:3]

        if BITS_32:
            program_files_dir = get_folder_path(FOLDERID.ProgramFilesX86)[0]
        else:
            program_files_dir = get_folder_path(FOLDERID.ProgramFilesX64)[0]

        local_data_dir = get_folder_path(FOLDERID.LocalAppData)[0]
        program_files_64_dir = (
            get_folder_path(FOLDERID.ProgramFilesX64)[0] or os.path.join(_windrive, 'Program Files')
        )

        if os.path.exists(os.path.join(program_files_dir, self.windows_folder_name)):
            application_path = os.path.join(program_files_dir, self.windows_folder_name)
        elif os.path.exists(os.path.join(program_files_64_dir, self.windows_folder_name)):
            application_path = os.path.join(program_files_64_dir, self.windows_folder_name)
        else:
            application_path = os.path.join(local_data_dir, self.windows_folder_name)
            if not os.path.isdir(application_path):
                application_path = os.path.join(local_data_dir, 'Programs', self.windows_folder_name)

        return application_path

    @property
    def versions(self):
        if self._vscode_version_value is None and self.is_installed:
            stdout, _, _ = run_process([self.executable[1:-1], '--version'])
            # self.executable[1:-1] to remove unnecessary ""
            if stdout:
                version = stdout.split('\n')[0]
                self._vscode_version_value = version
        return [self._vscode_version_value]

    def install_extensions(self):
        """Install app extensions."""
        wm = self._process_api
        logger.debug('Installing vscode extensions')
        cmd = [
            '{}'.format(self.executable),
            '--install-extension',
            'ms-python.anaconda-extension-pack',
            # ms-python-anaconda-extension
            # ms-python.python
        ]
        logger.debug(' '.join(cmd))
        worker = wm.create_process_worker(cmd)
        return worker

    def update_config(self, prefix):
        logger.debug('Update app config to use prefix {}'.format(prefix))
        try:
            _config = os.path.join(
                CONF_PATH,
                'Code',
                'User',
                'settings.json',
            )
            _config_dir = os.path.dirname(_config)

            try:
                if not os.path.isdir(_config_dir):
                    os.makedirs(_config_dir)
            except Exception as e:
                logger.error(e)

            config_update = {'python.pythonPath': prefix}

            if os.path.isfile(_config):
                try:
                    with io.open(_config, 'r', encoding='utf-8') as f:
                        data = f.read()

                    self.create_config_backup(data)

                    config_data = json.loads(data)
                    for key, val in config_update.items():
                        config_data[key] = val
                except Exception:
                    # If there is any error, don't overwrite app config
                    return False
            else:
                config_data = config_update.copy()

            mode = 'w' if PY3 else 'wb'
            with io.open(_config, mode) as f:
                json.dump(
                    config_data,
                    f,
                    sort_keys=True,
                    indent=4,
                )
        except Exception as e:
            logger.error(e)
            return False

        return True

    def create_config_backup(self, data):
        """
        Create a backup copy of the app configuration file `data`.

        Leave only the last 10 backups.
        """
        now = datetime.datetime.now()
        date = now.strftime('%Y%m%d%H%M%S')
        _config_dir = os.path.join(
            CONF_PATH,
            'Code',
            'User',
        )
        _config_bck = os.path.join(
            _config_dir,
            'bck.{date}.navigator.settings.json'.format(date=date),
        )

        # Make the backup
        logger.debug('Creating backup app config file: {}' ''.format(_config_bck))
        with io.open(_config_bck, 'w', encoding='utf-8') as f_handle:
            f_handle.write(data)

        # Only keep the latests 10 backups
        files = os.listdir(_config_dir)
        fpaths = [
            os.path.join(_config_dir, f)
            for f in files
            if f.startswith('bck.') and f.endswith('.navigator.settings.json')
        ]

        fpaths_remove = list(sorted(fpaths, reverse=True))[10:]
        for fpath in fpaths_remove:
            try:
                os.remove(fpath)
            except Exception:
                pass
