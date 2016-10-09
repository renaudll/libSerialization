import yaml
import os
import core

def export_yaml(data, **kwargs):
	dicData = core.export_dict(data)
	return yaml.dump(dicData, **kwargs)

def export_yaml_file(data, path, mkdir=True, **kwargs):
	if mkdir: 
		_handle_dir_creation(path)

	dicData = _export_basicData(data)

	with open(path, 'w') as fp:
		yaml.dump(dicData, fp)

	return True

def import_yaml(str_, **kwargs):
	data = yaml.load(str_)
	return core.import_dict(data)

def import_yaml_file(path, **kwargs):
	if not os.path.exists(path):
		raise Exception("Can't importFromYamlFile, file does not exist! {0}".format(path))

	with open(path, 'r') as fp:
		data = yaml.load(fp)
	return core.import_dict(data)
