# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='Segue',
    version='1.0.0dev',
    description='Maya and Houdini geometry transfer helper.',
    packages=[
        'segue',
    ],
    package_dir={
        '': 'source'
    },
    author='Martin Pengelly-Phillips',
    author_email='martin@4degrees.ltd.uk',
    license='Apache License (2.0)',
    long_description=open('README.rst').read(),
    url='https://gitlab.com/4degrees/segue',
    keywords='maya,houdini,transfer,cache'
)

