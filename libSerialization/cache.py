from decorators import memoized
from .core import iter_subclasses_recursive, iter_module_subclasses_recursive, get_class_namespace

class Cache(object):
    def __init__(self):
        self.classes = None
        self._cache_import_by_id = {}
        self._cache_networks_by_id = {}  # todo: merge with _cache_import_by_id

    @memoized
    def _get_cls_cache_by_module(self, module_name, base_class=object):
        i = iter_module_subclasses_recursive(module_name, base_class)
        result = {}
        for cls in i:
            result[cls.__name__] = cls
        return result

    @memoized
    def _get_cls_cache(self, base_class=object):
        i = iter_subclasses_recursive(base_class)
        result = {}
        for cls in i:
            result[cls.__name__] = cls
        return result

    def get_class_by_name(self, cls_name, module_name=None, base_class=object):
        if module_name is None:
            cache = self._get_cls_cache(base_class=base_class)
        else:
            cache = self._get_cls_cache_by_module(module_name=module_name, base_class=base_class)
        return cache.get(cls_name, None)

    def get_class_by_namespace(self, cls_namespace, module_name=None, base_class=object):
        if module_name is None:
            cache = self._get_cls_cache(base_class=base_class)
        else:
            cache = self._get_cls_cache_by_module(base_class=base_class)
        for cls in cache.values():
            cls_namespace = get_class_namespace(cls)
            if cls_namespace == cls_namespace:
                return cls

    def get_import_value_by_id(self, id, default=None):
        return self._cache_import_by_id.get(id, default)

    def set_import_value_by_id(self, id, val):
        self._cache_import_by_id[id] = val

    def get_network_by_id(self, id, default=None):
        return self._cache_networks_by_id.get(id, default)

    def set_network_by_id(self, id, net):
        self._cache_networks_by_id[id] = net