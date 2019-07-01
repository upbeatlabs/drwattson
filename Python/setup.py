#!/usr/bin/env python

from setuptools import setup

classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 2.7',
    'Topic :: Software Development',
    'Topic :: System :: Hardware'
    ]

setup(name='UpbeatLabs_MCP39F521',
      version='1.1',
      description='Python Distribution Utilities',
      long_description='',
      author='Sridhar Rajagopal',
      author_email='sridhar@upbeatlabs.com',
      url='https://github.com/upbeatlabs/wattson',
      license = 'BSD License',
      classifiers = classifiers,
      packages=['UpbeatLabs_MCP39F521'],
      install_requires=[
          'smbus2',
          ]
     )
