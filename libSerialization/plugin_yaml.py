import yaml
import os
import core


class YamlSerializer(core.DictSerializer):
    def export_yaml(self, data, **kwargs):
        data_dict = self.export_dict(data)
        return yaml.dump(data_dict, **kwargs)

    def export_yaml_file(self, data, path, mkdir=True, **kwargs):
        if mkdir:
            core.mkdir(path)

        data_dict = self.export_dict(data)

        with open(path, 'w') as fp:
            yaml.dump(data_dict, fp)

        return True

    def import_yaml(self, str_, **kwargs):
        dicData = yaml.load(str_)
        return self.import_dict(dicData)

    def import_yaml_file(self, path, **kwargs):
        if not os.path.exists(path):
            raise Exception("Can't importFromYamlFile, file does not exist! {0}".format(path))

        with open(path, 'r') as fp:
            data_dict = yaml.load(fp)
            return self.import_dict(data_dict)

#
# Global methods
#
__all__ = ['export_json', 'export_json_file', 'import_json', 'import_json_file']
singleton = YamlSerializer()


def export_yaml(*args, **kwargs):
    global singleton
    singleton.export_yaml(*args, **kwargs)


def export_yaml_file(*args, **kwargs):
    global singleton
    singleton.export_yaml_file(*args, **kwargs)


def import_yaml(*args, **kwargs):
    global singleton
    singleton.import_yaml(*args, **kwargs)


def import_yaml_file(*args, **kwargs):
    global singleton
    singleton.import_yaml_file(*args, **kwargs)
