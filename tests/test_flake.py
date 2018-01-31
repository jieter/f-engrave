import os
import unittest

# from flake8.engine import get_style_guide
# flake8.api.legacy.get_style_guide(**kwargs)
# http://flake8.pycqa.org/en/latest/user/python-api.html

import flake8.api.legacy


def get_style_guide(**kwargs):
    return flake8.api.legacy.get_style_guide(**kwargs)


flake8 = get_style_guide(
    ignore=(
        'E501',  # Line too long
        'F403',  # 'import *'
        'E128',  # continuation line under-indented for visual indent?
        # 'E221',  # Multiple spaces before operator
        # 'E222',  # Multiple spaces after operator

    ),
    report=None,
    exclude=[
        # old files
        'f-engrave-140.py',
        'py2exe_setup.py',

        # new files, to be cleaned up:
        'gui.py',
        'model.py',
        'nurbs.py',
        'bspline.py',
        # 'linearcfitter.py',
        'dxf_class.py',
    ]
)


def base_directory():
    current = os.path.dirname(os.path.realpath(__file__))

    return os.path.join(current, '..')


class Flake8Test(unittest.TestCase):
    def test_flake8(self):
        report = flake8.check_files([
            base_directory()
        ])

        self.assertEqual(report.get_statistics('E'), [],
                         'Flake8 reports errors')
