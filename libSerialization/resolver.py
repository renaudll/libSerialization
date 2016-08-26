import logging
import decorators
import sys
import functools

def get_class_def(class_name, base_class=object):
    """
    Using a base class, scan recursively all inherited class until a specific class
    :param class_name:
    :param base_class:
    :return:
    """
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

    # Ensure we have the latest defined class definition.
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


#
# legacy methods
#


def iter_subclasses_recursive(cls):
    yield cls

    try:
        for sub_cls in cls.__subclasses__():
            for x in iter_subclasses_recursive(sub_cls):
                yield x
    except TypeError:  # This will fail when encountering the 'type' datatype.
        pass

def get_class_module_root(cls):
    return next(iter(cls.__module__.split('.')), None)


def iter_module_subclasses_recursive(module_root, cls):
    for sub_cls in iter_subclasses_recursive(cls):
        cur_module_root = get_class_module_root(sub_cls)
        if module_root == cur_module_root:
            yield sub_cls

@decorators.memoized
def find_class_by_name(class_name, base_class=object, module=None):
    if module is None:
        iterator = iter_subclasses_recursive(base_class)
    else:
        #module = sys.modules[module]
        iterator = iter_module_subclasses_recursive(module, base_class)

    for cls in iterator:
        if cls.__name__ == class_name:
            return cls

def find_class_by_namespace(class_namespace, base_class=object, module=None):
    try:
        for cls in base_class.__subclasses__():
            # Compare the absolute class namespace
            cls_path = get_class_namespace(cls)
            if cls_path == class_namespace:
                return cls

            t = find_class_by_namespace(class_namespace, base_class=cls)
            if t is not None:
                return t
    except Exception as e:
        pass
        #logging.warning("Error obtaining class definition for {0}: {1}".format(class_name, e))
    return None


def get_cls_cache(base_class=object, module=None):
    """
    Store all subclasses of provided base class.
    :param base_class: The base class to inspect.
    :param module: If provided, all results will be class of provided module name.
    :return: A dictionary where the key is the class name and the value is the class definition.
    """
    # TODO: Use generators to halt iteration as soon as we get the data.
    result = {}
    iter = iter_subclasses_recursive if module is None else functools.partial(iter_module_subclasses_recursive, module)
    for cls in iter(base_class):
        key = cls.__name__
        result[key] = cls
    return result



