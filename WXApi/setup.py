#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='pyweipi',
    version='1.0.6',
    keywords=('weixin', 'weibo', 'api'),
    description='Python 2.x 3.x api for Weixin or Weibo platform',
    long_description='weixin or weibo platform python api for used',
    install_requires=['requests>=2.0'],

    author='Yifei0727',
    author_email='Yifei0727@users.noreply.github.com',

    license='MIT',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'TOPIC :: SOFTWARE DEVELOPMENT :: LIBRARIES',
        'TOPIC :: SOFTWARE DEVELOPMENT :: LIBRARIES :: PYTHON MODULES',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    url='https://github.com/KEDYY/pyweipi',
    packages=find_packages(),
    platforms='any',
)
