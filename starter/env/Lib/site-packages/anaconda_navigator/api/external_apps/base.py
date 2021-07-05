# Standard library imports
from abc import ABC, abstractmethod
import os
import webbrowser

# Local imports
from anaconda_navigator.config import LINUX, MAC, WIN
from anaconda_navigator.utils.constants import AppType


class BaseApp(ABC):
    def __init__(self, config, app_name, display_name, description, image_path, needs_license, non_conda, app_type):
        self.config = config
        self.app_name = app_name
        self.display_name = display_name
        self.description = description
        self.image_path = image_path
        self.needs_license = needs_license
        self.non_conda = non_conda
        self.app_type = app_type
        self.is_available = True


class BaseWebApp(BaseApp, ABC):
    def __init__(self, url, **kwargs):
        super(BaseWebApp, self).__init__(app_type=AppType.WEB, non_conda=True, **kwargs)

        self.url = url

    def launch(self):
        """Launch the application."""
        webbrowser.open_new_tab(self.url)


class BaseInstallableApp(BaseApp, ABC):
    def __init__(self, filename, windows_folder_name, mac_name, is_installation_enabled, process_api, **kwargs):
        super(BaseInstallableApp, self).__init__(app_type=AppType.INSTALLABLE, non_conda=True, **kwargs)

        self.filename = filename
        self.windows_folder_name = windows_folder_name
        self.mac_name = mac_name
        self.is_installation_enabled = is_installation_enabled
        self.app_directory_path = ''

        self._process_api = process_api

        self.set_up_app_directory_path()

    def set_up_app_directory_path(self):
        """Set up valid app_directory_path."""
        config_app_directory_path = self.config.get('main', f'{self.app_name}_path', '')

        if config_app_directory_path and os.path.exists(config_app_directory_path):
            self.app_directory_path = config_app_directory_path
        else:
            if MAC:
                self.app_directory_path = self._get_macos_installation_directory()
            elif LINUX:
                self.app_directory_path = self._get_linux_installation_directory()
            elif WIN:
                self.app_directory_path = self._get_windows_installation_directory()

            self.config.set('main', f'{self.app_name}_path', self.app_directory_path)

    @property
    @abstractmethod
    def executable(self):
        """Return executable command."""
        raise NotImplementedError

    @property
    def is_installed(self):
        """Return whether the app is installed."""
        return bool(self.executable)

    def _get_macos_installation_directory(self) -> str:
        for root in ('/Applications', os.path.join(os.path.expanduser('~'), 'Applications')):
            if os.path.exists(os.path.join(root, self.mac_name)):
                return os.path.join(root, self.mac_name)
        return ''

    @abstractmethod
    def _get_linux_installation_directory(self):
        raise NotImplementedError

    @abstractmethod
    def _get_windows_installation_directory(self):
        raise NotImplementedError

    @abstractmethod
    def update_config(self, prefix):
        """Update user config to use selected Python prefix interpreter."""
        raise NotImplementedError

    @abstractmethod
    def install_extensions(self):
        """Install app extensions."""
        raise NotImplementedError

    def install(self):
        """Install app."""
        # this method should be implement only if self.install_enabled == True
        raise NotImplementedError
