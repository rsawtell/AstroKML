#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup (name = 'AstroKML',
       version = '1.0.1',
       author = 'Reid Sawtell',
       author_email='rwsawtel@mtu.edu',
       url='http://github.com/rsawtell/AstroKML',
       download_url='https://github.com/rsawtell/AstroKML/archives/master',
       keywords=['kml','nasa','astronaut','pykml'],
       install_requires=[
            "mechanize>=0.2.5",
            "pykml==0.0.3"
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
       long_description = """\
=========
AstroKML
=========
Generates a KML file from Astronaught Photographs covering a user specified region

Note: this is a script, not a module

---------
Dependencies
---------

mechanize 2.0.1 <http://wwwsearch.sourceforge.net/mechanize>
pykml 0.3 <http://code.google.com/p/pykml>

Optional (only needed if -s option is used)

gdal 1.7.1 <http://trac.osgeo.org/gdal/wiki/GdalOgrInPython>
shapely 1.2 <http://trac.gispython.org/lab/wiki/Shapely>

---------
Installation
---------

$ sudo easy_install astrokml

---------
Usage
---------

To load a region defined by a shapefile:
   AstroKML.py -s <Output File> <Shapefile>
   NOTE: The shapefile must contain a single polygon entry

To load a region defined by a bounding box:
   AstroKML.py -b <Output File> <MinLon> <MinLat> <MaxLon> <MaxLat>

To use predefined region(s):
   AstroKML.py -r <Output File> <Region1> ...

See http://eol.jsc.nasa.gov/sseop/technical.htm for the full list of regions
"""
      )
