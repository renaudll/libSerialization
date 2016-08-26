"""
TODO: Improve the 'plugin' system.
Maybe plugins should only implement a simple import and export method.
This would mean than json and json_file are two different plugins.
"""
from core import export_dict, import_dict
import plugin_json
import plugin_maya
from plugin_json import *
from plugin_maya import *


def _reload():
    reload(core)
    reload(plugin_json)
    reload(plugin_maya)
