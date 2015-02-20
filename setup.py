# -*- coding: utf-8 -*-
'''Utility to generate data from a schema'''
import sys

from setuptools import setup
from setuptools.command.test import test


class Tox(test):
    def initialize_options(self):
        test.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        test.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import tox
        sys.exit(tox.cmdline())


if __name__ == '__main__':
    setup(
        name='jsonvalidate.py',
        version='0.1',
        description='Utility to valdiate json from a schema',
        url='https://github.com/axado/jsonvalidate.py',
        author='Augusto F. Hack',
        author_email='augusto@axado.com.br',
        license='MIT',

        py_modules=['jsonvalidate'],
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.4',
        ],
        keywords='data validation json',
        install_requires=['multidispatch', 'simplejson'],
        tests_require=['tox'],
        cmdclass={'test': Tox},
    )
