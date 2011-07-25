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