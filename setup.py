#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file is part of fish-bundles..
# https://github.com/fish-bundles/fish-bundles-web

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2014 Bernardo Heynemann heynemann@gmail.com


from setuptools import setup, find_packages
from fish_bundles_web import __version__

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
    name='fish-bundles-web',
    version=__version__,
    description='fish-bundles-web is the website for fish-bundles',
    long_description='''
fish-bundles-web is the website for fish-bundles.
''',
    keywords='fish shell repository share',
    author='Bernardo Heynemann',
    author_email='heynemann@gmail.com',
    url='https://github.com/fish-bundles/fish-bundles-web',
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
        'Flask==0.10.1',
        'alembic==0.6.6',
        'mysql-python==1.2.5',
        'GitHub-Flask==1.1.1',
        'Flask-SQLAlchemy==1.0',
        'flask-coffee==0.3',
        'Flask-Compass==0.2',
        'Flask-Assets==0.10',
        'jsmin==2.0.11',
        'cssmin==0.2.0',
        'ujson==1.33',
        'awesome-slugify==1.6',
        'markdown==2.4.1',
        'semantic_version==2.3.0',
        'derpconf==0.7.2',
    ],
    extras_require={
        'tests': tests_require,
    },
    entry_points={
        'console_scripts': [
            'fish-bundles-web=fish_bundles_web.app:main',
        ],
    },
)
