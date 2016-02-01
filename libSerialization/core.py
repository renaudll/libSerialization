import os
import sys
import consts
import logging as _logging

logging = _logging.getLogger()
logging.setLevel(_logging.WARNING)


def get_class_def(class_name, base_class=object):
    try:
        for cls in base_class.__subclasses__():
            cls_path = get_class_namespace(cls)
            if cls_path == class_name:
                return cls
            else:
                t = get_class_def(class_name, base_class=cls)
                if t is not None:
                    return t
    except Exception as e:
        pass
        #logging.warning("Error obtaining class definition for {0}: {1}".format(class_name, e))
    return None


def create_class_instance(class_name):
    cls = get_class_def(class_name)

    if cls is None:
        logging.warning("Can't find class definition '{0}'".format(class_name))
        return None

    class_def = getattr(sys.modules[cls.__module__], cls.__name__)
    assert (class_def is not None)

    try:
        return class_def()
    except Exception as e:
        logging.error("Fatal error creating '{0}' instance: {1}".format(class_name, str(e)))
        return None


def get_class_namespace(classe):
    if not isinstance(classe, object):
        return None  # Todo: throw exception
    tokens = []
    while classe is not object:
        tokens.append(classe.__name__)
        classe = classe.__bases__[0]
    return '.'.join(reversed(tokens))


class DictSerializer(object):
    #
    # Define basic datatypes
    #

    TYPES_BASIC = [int, float, bool]

    # Python3 support
    try:
        TYPES_BASIC.append(basestring)
    except NameError:
        pass
        TYPES_BASIC.append(str)

    def is_data_basic(self, _data):
        global TYPES_BASIC
        return any(filter(lambda x: isinstance(_data, x), (iter(TYPES_BASIC))))

    #
    # Define list datatypes
    #

    TYPES_LIST = [list, tuple]

    def is_data_list(self, _data):
        global TYPES_LIST
        return any(filter(lambda x: isinstance(_data, x), (iter(TYPES_LIST))))

    #
    # Define complex datatypes
    #

    # We consider a data complex if it's a class instance.
    # Note: We check for __dict__ because isinstance(_data, object) return True for basic types.
    TYPES_COMPLEX = [dict]

    def is_data_complex(self, _data):
        return any(filter(lambda x: isinstance(_data, x), (iter(self.TYPES_COMPLEX)))) or hasattr(_data, '__dict__')

    def get_data_type(self, data):
        if self.is_data_basic(data):
            return consts.DataTypes.TYPE_BASIC
        if self.is_data_list(data):
            return consts.DataTypes.TYPE_LIST
        if self.is_data_complex(data):
            return consts.DataTypes.TYPE_COMPLEX

        raise IOError("Unsupported object type {0} ({1})".format(data, type(data)))

    def export_dict(self, data, skip_None=True, recursive=True, **args):
        """
        Export an object instance (data) into a dictionary of basic data types (including pymel.Pynode and pymel.Attribute).

        Args:
            data: An instance of the build-in python class object.
            skip_None: Don't store an attribute if is value is None.
            recursive: Export recursively embedded instances of object in (excluding protected and private properties).
            **args:

        Returns: A dict instance containing only basic data types.

        """
        data_type = self.get_data_type(data)
        # object instance
        if data_type == consts.DataTypes.TYPE_COMPLEX:
            data_dict = {
                '_class': get_class_namespace(data.__class__),
                '_uid': id(data)
            }
            for key, val in (data.items() if isinstance(data, dict) else data.__dict__.items()):  # TODO: Clean
                if '_' not in key[0]:
                    if not skip_None or val is not None:
                        if (data_type == consts.DataTypes.TYPE_COMPLEX and recursive is True) or data_type == consts.DataTypes.TYPE_LIST:
                            val = self.export_dict(val, skip_None=skip_None, recursive=recursive, **args)
                        if not skip_None or val is not None:
                            data_dict[key] = val

            return data_dict

        # Handle other types of data
        elif data_type == consts.DataTypes.TYPE_BASIC:
            return data

        # Handle iterable
        elif data_type == consts.DataTypes.TYPE_LIST:
            return [self.export_dict(v, skip_None=skip_None, **args) for v in data if not skip_None or v is not None]

        elif data_type == consts.DataTypes.TYPE_DAGNODE:
            return data

        logging.warning("[exportToBasicData] Unsupported type {0} ({1}) for {2}".format(type(data), data_type, data))
        return None

    def import_dict(self, data, **args):
        """
        Rebuild any instance of a python object instance that have been serialized using export_dict.

        Args:
            _data: A dict instance containing only basic data types.
            **args:

        Returns:

        """
        assert (data is not None)
        if isinstance(data, dict) and '_class' in data:
            # Handle Serializable object
            class_path = data['_class']
            class_name = class_path.split('.')[-1]
            instance = create_class_instance(class_name)
            if instance is None or not isinstance(instance, object):
                logging.error("Can't create class instance for {0}, did you import to module?".format(class_path))
                # TODO: Log error
                return None
            for key, val in data.items():
                if key != '_class':
                    instance.__dict__[key] = self.import_dict(val, **args)
            return instance
        # Handle array
        elif self.is_data_list(data):
            return [self.import_dict(v, **args) for v in data]
        # Handle other types of data
        else:
            return data

# TODO: Move to a lib?
def mkdir(path):
    path_dir = os.path.dirname(path)

    # Create destination folder if needed
    if not os.path.exists(path_dir):
        os.makedirs(path_dir)

#
# Global methods
#
__all__ = ['export_dict', 'import_dict']
singleton = DictSerializer()


def export_dict(*args, **kwargs):
    global singleton
    singleton.export_dict(*args, **kwargs)


def import_dict(*args, **kwargs):
    global singleton
    singleton.import_dict(*args, **kwargs)