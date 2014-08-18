#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file is part of fish-hooks.
# https://github.com/heynemann/fish-hooks

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2014 Bernardo Heynemann heynemann@gmail.com


from setuptools import setup, find_packages
from fishhooks import __version__

tests_require = [
    'mock',
    'nose',
    'coverage',
    'yanc',
    'preggy',
    'tox',
    'ipdb',
    'coveralls',
    'sphinx',
]

setup(
    name='fish-hooks',
    version=__version__,
    description='fish-hooks is a repository for fish shell functions',
    long_description='''
fish-hooks is a repository for fish shell functions
''',
    keywords='fish shell repository share',
    author='Bernardo Heynemann',
    author_email='heynemann@gmail.com',
    url='https://github.com/heynemann/fish-hooks',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Unix',
        "Programming Language :: Python :: 2.7",
        'Operating System :: OS Independent',
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # add your dependencies here
        # remember to use 'package-name>=x.y.z,<x.y+1.0' notation (this way you get bugfixes)
        'flask',
        'alembic',
        'mysql-python',
        'GitHub-Flask',
        'Flask-SQLAlchemy',
        'flask-coffee',
        'Flask-Compass',
        'Flask-Assets',
        'jsmin',
        'cssmin',
        'ujson',
        'awesome-slugify',
        'markdown',
        'cliff',
        'semantic_version',
    ],
    extras_require={
        'tests': tests_require,
    },
    entry_points={
        'console_scripts': [
            # add cli scripts here in this form:
            'fish-hooks-api=fishhooks.app:main',
            'fb=fishhooks.cli:main',
        ],
        'fb': [
            'install = fishhooks.cli.install:Install',
        ],
    },
)
