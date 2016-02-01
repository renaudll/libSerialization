import json
import os
import core

#
# Json Support
#

class JsonSerializer(core.DictSerializer):
    def export_json(self, data, **kwargs):
        data = self.export_dict(data)
        return json.dumps(data, **kwargs)

    def export_json_file(self, data, path, mkdir=True, **kwargs):
        if mkdir:
            core.mkdir(path)

        data_dict = self.export_dict(data)
        with open(path, 'w') as fp:
            json.dump(data_dict, fp, **kwargs)

        return True

    def import_json(self, str_, **kwargs):
        data = json.loads(str_, **kwargs)
        return self.import_dict(data)

    def import_json_file(self, path, **kwargs):
        if not os.path.exists(path):
            raise Exception("Can't importFromJsonFile, file does not exist! {0}".format(path))

        with open(path, 'r') as fp:
            data = json.load(fp, **kwargs)
            return self.import_dict(data)

#
# Global methods
#
__all__ = ['export_json', 'export_json_file', 'import_json', 'import_json_file']
singleton = JsonSerializer()


def export_json(*args, **kwargs):
    global singleton
    singleton.export_json(*args, **kwargs)


def export_json_file(*args, **kwargs):
    global singleton
    singleton.export_json_file(*args, **kwargs)


def import_json(*args, **kwargs):
    global singleton
    singleton.import_json(*args, **kwargs)


def import_json_file(*args, **kwargs):
    global singleton
    singleton.import_json_file(*args, **kwargs)
