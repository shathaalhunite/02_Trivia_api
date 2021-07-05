# Local imports
from .datalore import DataloreApp
from .ibm_watson import IBMWatsonApp
from .pycharm import PyCharmCEApp, PyCharmProApp
from .vscode import VSCodeApp

apps = {'vscode': VSCodeApp, 'pycharm_pro': PyCharmProApp, 'pycharm_ce': PyCharmCEApp}
web_apps = {'datalore': DataloreApp, 'ibm_watson': IBMWatsonApp}
