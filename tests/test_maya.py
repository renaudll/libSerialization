import os
import mayaunittest
from maya import cmds
import pymel.core as pymel
import libSerialization

def open_scene(path_local):
    def deco_open(f):
        def f_open(*args, **kwargs):
            m_path_local = path_local # make mutable

            path = os.path.join(os.path.dirname(__file__), m_path_local)
            if not os.path.exists(path):
                raise Exception("File does not exist on disk! {0}".format(path))

            cmds.file(path, open=True, f=True)
        return f_open
    return deco_open

# Note that we need to define the class used in the UnitTest in the global module score
# for them to be accessible by libSerialization.
class OldStyleClass:
    pass


class A(object):
    pass


class B(object):
    pass


class C(B, A):
    pass


class SampleTests(mayaunittest.TestCase):

    def test_old_style_class(self):
        """
        Python old-style class are not supported.
        This ensure that a NotImplementedError is raised if we try to use an old-style class.
        :return:
        """
        inst = OldStyleClass()

        try:
            libSerialization.export_dict(inst)
            raise Exception
        except Exception, e:
            self.assertTrue(isinstance(e, NotImplementedError))

    def test_new_style_class_mro(self):
        inst = C()

        result = libSerialization.export_dict(inst)
        self.assertTrue(result['_class'] == 'C')
        self.assertTrue(result['_class_namespace'] == 'C.B.A')

    def test_export_network(self, epsilon=0.00001):
        pynode_a = pymel.createNode('transform')
        pynode_b = pymel.createNode('transform')

        old_instance = A()
        old_instance.ex_int = 42
        old_instance.ex_float = 3.14159
        old_instance.ex_str = 'Hello World'
        old_instance.ex_None = None
        old_instance.ex_list_pynode = [None, pynode_a, None, pynode_b]

        #
        # Ensure consistency when exporting to network
        #
        n = libSerialization.export_network(old_instance)
        network_ex_int = n.ex_int.get()
        network_ex_float = n.ex_float.get()
        network_ex_str = n.ex_str.get()
        self.assertTrue(network_ex_int == old_instance.ex_int)
        self.assertTrue(abs(network_ex_float- old_instance.ex_float) < epsilon)
        self.assertTrue(network_ex_str == old_instance.ex_str)

        # Note: libSerialization will NEVER export a None value since the type cannot be resolved.
        self.assertTrue(not n.hasAttr('ex_None'))

        #
        # Ensure consistency when importing from network
        #
        new_instance = libSerialization.import_network(n)
        self.assertTrue(network_ex_int == new_instance.ex_int)
        self.assertTrue(abs(network_ex_float- new_instance.ex_float) < epsilon)
        self.assertTrue(network_ex_str == new_instance.ex_str)


