import os
import sys
import consts
import logging as _logging

logging = _logging.getLogger()
logging.setLevel(_logging.WARNING)

import resolver

class DictSerializer(object):
    def __init__(self, base_class=object, module=None):
        """
        The Serializer in memory a cache of class definition for better performances.
        :param base_class: The base class to initialize the cache from.
        """
        self.cache = resolver.get_cls_cache(base_class=base_class, module=module)
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
        return any(filter(lambda x: isinstance(_data, x), (iter(self.TYPES_BASIC))))

    #
    # Define list datatypes
    #

    TYPES_LIST = [list, tuple]

    def is_data_list(self, _data):
        return any(filter(lambda x: isinstance(_data, x), (iter(self.TYPES_LIST))))

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
                '_class': resolver.get_class_namespace(data.__class__),
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

    def _get_class_by_name(self, class_name, class_module=None):
        """
        Return the latest defined class matching the provided requirements.
        :param class_name:
        :param class_module:
        :return:
        """
        # In the past, class where stored as namespaces. (ex: ParentClass.ChildClass)
        # instead of using only the class name and the module name.
        # We still support this method, however in the future it might be
        # desirable to break compatibility to increase speed.
        if '.' in class_name:
            logging.warning("Deprecated data is affecting performance. Please update data for class {0}".format(
                class_name
            ))
            class_definition = resolver.find_class_by_namespace(class_name)
        else:
            # TODO: Use cache lookup!
            #class_definition = resolver.find_class_by_name(class_name, module=class_module)
            class_definition = self.cache.get(class_name, None)


        if class_definition is None:
            logging.warning("Cannot find definition for '{0}', is it imported?".format(
                class_name
            ))
        else:
            # Ensure we have the latest defined class definition.
            class_definition = getattr(sys.modules[class_definition.__module__], class_definition.__name__)

        return class_definition

    def import_dict(self, data, **args):
        """
        Rebuild any instance of a python object instance that have been serialized using export_dict.

        Args:
            data: A dict instance containing only basic data types.
            **args:

        Returns:

        """
        assert (data is not None)
        if isinstance(data, dict) and '_class' in data:
            # Handle Serializable object
            class_path = data['_class']
            class_name = class_path.split('.')[-1]
            instance = resolver.create_class_instance(class_name)
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

# Expose core methods for backward compatibility.
# TODO: Remove this.
from resolver import find_class_by_name

__all__ = ['export_dict', 'import_dict', 'find_class_by_name']


def export_dict(data, base_class=object, module=None, **kwargs):
    s = DictSerializer(base_class=base_class, module=module)
    s.export_dict(data, **kwargs)

def import_dict(data, base_class=object, module=None, **kwargs):
    s = DictSerializer(base_class=base_class, module=module)
    return s.import_dict(data, **kwargs)