"""
Usage:
/usr/autodesk/maya2016/bin/mayapy ~/packages/libSerialization/9.9.9/tests/run_all.py
"""
import os
import sys
import mayaunittest

path_module_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(path_module_dir)

if __name__ == '__main__':
    mayaunittest.run_tests_from_commandline(directories=[os.path.dirname(__file__)])

