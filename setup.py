#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup

setup (name = 'AstroKML',
       version = '1.0',
       author = 'Reid Sawtell',
       author_email='rwsawtel@mtu.edu',
       url='http://github.com/rsawtell/AstroKML',
       download_url='https://github.com/rsawtell/AstroKML/tarball/master',
       keywords=['kml','nasa','astronaut','pykml'],
       install_requires=[
            "mechanize>=2.0.1",
            "pykml==0.3"
       ],
       description = 'Compile Astronaut photographs from a specified region into a single KML',
       scripts=['AstroKML.py'],
       classifiers = [
            "Programming Language :: Python",
            "Programming Language :: Python :: 2.7",
            "Operating System :: OS Independent",
            "Development Status :: 4 - Beta",
            "Environment :: Web Environment",
            "Intended Audience :: Science/Research",
            "License :: Freely Distributable",
            "Natural Language :: English",
            "Topic :: Multimedia :: Graphics :: Viewers",
            "Topic :: Scientific/Engineering :: GIS",
            "Topic :: Scientific/Engineering :: Visualization",
       ],
       long_description = "See README.txt"
      )
