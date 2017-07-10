#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from os import path


here = path.abspath(path.dirname(__file__))
exec(open(path.join(here, 'azion/version.py')).read())


def readme():
    with open(path.join(here, 'README.md'), encoding='utf-8') as f:
        return f.read()


setup(
        name='azion',
    packages=["azion"],
    version=__version__,
    description='AZION API SDK',
    url='https://github.com/mtulio/azion-sdk-python',
    download_url='https://github.com/mtulio/azion-sdk-python/archive/%s.tar.gz' % __version__,
    author='Marco Tulio R Braga',
    author_email='braga@mtulio.eng.br',
    license='Apache-2.0',
    keywords=['AZOIN', 'SDK'],
    install_requires=[
        'requests',
    ]
)
