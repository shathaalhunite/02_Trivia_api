# Local imports
from anaconda_navigator.api.external_apps.base import BaseWebApp
from anaconda_navigator.static import images


class IBMWatsonApp(BaseWebApp):
    def __init__(self, **kwargs):
        super(IBMWatsonApp, self).__init__(
            app_name='ibm_watson',
            display_name='IBM Watson Studio Cloud',
            description='IBM Watson Studio Cloud provides you the tools to analyze and visualize data, '
            'to cleanse and shape data, to create and train machine learning models. Prepare data and '
            'build models, using open source data science tools or '
            'visual modeling.',
            image_path=images.IBM_WATSON_ICON_PATH,
            needs_license=False,
            url='http://www.anaconda.com/ibm_wsc_navigator',
            **kwargs
        )
