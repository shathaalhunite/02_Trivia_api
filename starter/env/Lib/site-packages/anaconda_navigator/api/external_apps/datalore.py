# Local imports
from anaconda_navigator.api.external_apps.base import BaseWebApp
from anaconda_navigator.static import images


class DataloreApp(BaseWebApp):
    def __init__(self, **kwargs):
        super(DataloreApp, self).__init__(
            app_name='datalore',
            display_name='Datalore',
            description='Online Data Analysis Tool with smart coding assistance by JetBrains. '
            'Edit and run your Python notebooks in the cloud and share them with your team.',
            image_path=images.DATALORE_ICON_1024_PATH,
            needs_license=False,
            url='http://www.anaconda.com/datalore_navigator',
            **kwargs
        )
