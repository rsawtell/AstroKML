#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Generates a KML file from Astronaught Photographs covering a user specified region
#
#Usage
#To load a region defined by a shapefile:
#   AstroKML.py -s <Output File> <Shapefile>
#   NOTE: The shapefile must contain a single polygon entry
#
#To load a region defined by a bounding box:
#   AstroKML.py -b <Output File> <MinLon> <MinLat> <MaxLon> <MaxLat>
#
#To use predefined region(s):
#   AstroKML.py -r <Output File> <Region1> ...
#
#See http://eol.jsc.nasa.gov/sseop/technical.htm for the full list of regions
#
#
#Dependencies:
#mechanize 2.0.1 <http://wwwsearch.sourceforge.net/mechanize>
#pykml 0.3 <http://code.google.com/p/pykml>
#
#Optional (only needed if -s option is used)
#
#gdal 1.7.1 <http://trac.osgeo.org/gdal/wiki/GdalOgrInPython>
#shapely 1.2 <http://trac.gispython.org/lab/wiki/Shapely>

import urllib2,sys,mechanize,re
from pykml.factory import KML_ElementMaker as K

#used to find various parts of the webpages that are parsed
pagefinder = re.compile("Page <b>\d+</b> of <b>\d+</b><br>")
trfinder = re.compile("</tr>")
startfinder = re.compile("<th>Quick View</th>")
endfinder = re.compile("</TABLE></CENTER>")
topfinder = re.compile("<TD valign=\"top\">[\-\. a-zA-Z0-9]*</TD>")
targetfinder = re.compile("target=\"_blank\">[ a-zA-Z0-9]*</A></TD>")
tdfinder = re.compile("</TD>")

shape = None

def usage():
    '''Prints script usage'''
    print """
Generates a KML file from Astronaught Photographs
covering a user specified region

To load a region defined by a shapefile:
    python AstroKML.py -s <Output File> <Shapefile>
    NOTE: The shapefile must contain a single polygon entry

To load a region defined by a bounding box:
    python AstroKML.py -b <Output File> <MinLon> <MinLat> <MaxLon> <MaxLat>

To use predefined region(s):
    python AstroKML.py -r <Output File> <Region1> ...

See http://eol.jsc.nasa.gov/sseop/technical.htm for the full list of regions"""

def main():
    '''Handles command line options'''

    br = mechanize.Browser()

    args = sys.argv[1:]

    #The -s option uses a shapefile provided by the user
    if args[0] == '-s':
        if not len(args) == 3:
            usage()
            sys.exit(2)

        #osgeo and shapely are only imported if the -s option is called
        #this allows the other two options to be independent of these modules
        import osgeo.ogr as osr
        import shapely as shp
        from shapely.wkb import loads as ld
        global osgeo
        global shapely
        global loads
        osgeo = osr
        shapely = shp
        loads = ld

        rs = getShape(args[2])
        images = getImages(getBBoxResults(rs.bounds,br),br,rs)
        writeKML(args[1],images)

    #the -b option uses a user specified bounding box of lat/lon coords
    elif args[0] == '-b':
        if not len(args) == 6:
            usage()
            sys.exit(2)
        print (args[2],args[3],args[4],args[5])
        images = getImages(getBBoxResults((args[2],args[3],args[4],args[5]),br),br)
        writeKML(args[1],images)

    #the -r option uses the predefined regions available in NASA's search query form
    elif args[0] == '-r':
        if not len(args) >= 3:
            usage()
            sys.exit(2)
        images = getImages(getLocationResults(args[2:],br),br)
        writeKML(args[1],images)

    #help option
    elif args[0] == "-h" or args[0] == "help":
        usage()
    else:
        usage()
        sys.exit(2)
        

def getShape(shapefile):
    '''Reads the shapefile and computes the bounding box.
The bounding box is needed to narrow the search performed on the NASA site'''

    #load the shapefile
    driver = osgeo.GetDriverByName('ESRI Shapefile')
    dataset = driver.Open(shapefile, 0)

    #quit if the file failed to open
    if dataset == None:
        print "Invalid Shapefile: "+shapefile
        sys.exit()

    layer = dataset.GetLayer()
    
    #Only the first feature is used
    for index in xrange(layer.GetFeatureCount()):
        feature = layer.GetFeature(index)
        geometry = feature.GetGeometryRef()
        newshp = loads(geometry.ExportToWkb())
        return newshp

def getBBoxResults(bbox,br):
    '''Fills out the search form using a bounding box to narrow the results

Returns: search results response'''
    br.open("http://eol.jsc.nasa.gov/sseop/technical.htm")

    br.select_form(name="sqlform")
    br["minlat"] = repr(float(bbox[1]))
    br["maxlat"] = repr(float(bbox[3]))
    br["minlon"] = repr(float(bbox[0]))
    br["maxlon"] = repr(float(bbox[2]))
    print br["minlon"]
    print br["maxlon"]
    print br["minlat"]
    print br["maxlat"]
    br["imagesize"] = ["any"]
    response = br.submit()

    return response

def getLocationResults(locations,br):
    '''Fills out the search form using predefined regions to narrow the results

Returns: search results response'''
    br.open("http://eol.jsc.nasa.gov/sseop/technical.htm")

    br.select_form(name="sqlform")

    br["geoncb"] = ['on']
    br["geon"] = locations

    br["imagesize"] = ["any"]
    response = br.submit()
    return response

def getImages(response,br,shape=None):
    '''Parses search results

Returns: list of [Mission, Roll, Frame]'''

    doc =  response.read()
    print ">",doc
    #extract the number of pages of results
    pages =  pagefinder.search(doc).group()
    pages = pages[pages.find("of")+6:]
    pages = pages[:pages.find("<")]
    pages = int(pages)

    curpage = 1

    images = []

    print "Processing " + repr(pages) + " pages of results"

    #process each page of results
    while curpage<=pages:
        sys.stdout.write(repr(curpage)+" ")
        sys.stdout.flush()

        if doc == None:
            doc = response.read()

        #trim the start and end of the page surrounding the table to make finding results easier
        doc = doc[startfinder.search(doc).end(0):]

        doc = doc[:endfinder.search(doc).start(0)]
        
        #cut out the column headers
        loc = trfinder.search(doc).start(0)
        img = doc[:loc]
        doc = doc[loc+5:]
        loc = trfinder.search(doc).start(0)

        #process each item in the table
        while True:
            img = doc[:loc]
            doc = doc[loc+5:]

            try:
                loc = trfinder.search(doc).start(0)
            except:
                break

            #extract the mission number
            imgdc = {}
            loc2 = topfinder.search(img)
            imgdc["Mission"] = img[loc2.start(0)+17:loc2.end(0)-5].replace(" ","")
            img = img[loc2.end(0):]

            #extract the roll number
            loc2 = topfinder.search(img)
            imgdc["Roll"] = img[loc2.start(0)+17:loc2.end(0)-5].replace(" ","")
            img = img[loc2.end(0):]

            #extract the frame number
            loc2 = targetfinder.search(img)
            imgdc["Frame"] = img[loc2.start(0)+16:loc2.end(0)-9].replace(" ","")

            imgdc["Page"] = curpage

            #If appropriate, remove results that don't fall within the geometry
            #defined by the shapefile
            if not shape == None:

                img = img[loc2.end(0):]
                img = img[tdfinder.search(img).end(0):]
                img = img[tdfinder.search(img).end(0):]

                #extract latitude
                loc2 = topfinder.search(img)
                lat = img[loc2.start(0)+17:loc2.end(0)-5]
                img = img[loc2.end(0):]
                
                #extract longitude
                loc2 = topfinder.search(img)
                lon = img[loc2.start(0)+17:loc2.end(0)-5]
                img = img[loc2.end(0):]

                
                #if the image isn't in the region, don't include it in the results
                if not(lat == "") and not(lon == "") and shape.contains(shapely.geometry.Point(float(lon),float(lat))):
                    #print lat,lon
                    images += [imgdc]

            else:
                images += [imgdc]

        doc = None
        curpage += 1

        #advance to the next page of results
        if curpage <= pages:
            br.select_form("GoToPage")
            br["page"] = repr(curpage)
            response = br.submit()

    return images

def ParsePlacemark(url):
    '''Extracts metadata necessary to build a placemark'''
    plmrk = urllib2.urlopen(url)

    lines = []

    for line in plmrk:
        lines += [line]

    if not "<Placemark>" in lines[0]:
        return

    attr = {}

    attr["MRF"]                 = lines[2][lines[2].find("<name>")+6:lines[2].find("</name>")]
    attr["Color"]               = lines[6][lines[6].find("<color>")+7:lines[6].find("</color")]
    attr["Elevation"]           = "3000"
    attr["Tilt"]                = "0"
    attr["Longitude"]           = lines[15][lines[15].find("<longitude>")+11:lines[15].find("</longitude")]
    attr["Latitude"]            = lines[16][lines[16].find("<latitude>")+10:lines[16].find("</latitude")]
    attr["IMG"]                 = lines[20][lines[20].find("src=")+5:lines[20].find(".JPG")+4]
    attr["Features"]            = lines[23][lines[23].find(": ")+2:lines[23].find("</P>")]
    attr["YYYYMMDD"]            = lines[24][lines[24].find(": ")+2:lines[24].find(" (")]
    attr["HHMMSS"]              = lines[24][lines[24].find("DD), ")+4:lines[24].find(" (HH")]

    cline = lines[25]

    attr["Camera Tilt"]         = cline[cline.find(": ")+2:cline.find("&nbsp")]
    cline = cline[cline.find(";")+1:]

    attr["Camera Lens"]         = cline[cline.find(": ")+2:cline.find("&nbsp")]
    cline = cline[cline.find(";")+1:]

    attr["Camera"]              = cline[cline.find(": ")+2:cline.find("</P>")]
    cline = cline[cline.find(";")+1:]

    cline = lines[26]
    attr["Sun Azimuth"]         = cline[cline.find(": ")+2:cline.find("&nbsp")]
    cline = cline[cline.find(";")+1:]

    attr["Sun Elevation"]       = cline[cline.find(": ")+2:cline.find("&nbsp")]
    cline = cline[cline.find(";")+1:]

    attr["Spacecraft Altitude"] = cline[cline.find(": ")+2:cline.find(" nau")]
    cline = cline[cline.find(";")+1:]

    attr["DB Entry"]            = lines[27][lines[27].find("='")+2:lines[27].find("'>")]

    return attr


def placeMaker(attr):
    '''Uses pyKML to produce a placemark for an image
    
The use of pyKML isn't actually necessary,
you could do just as well appending the placemarks from the NASA
KML files into a single document, but the intention was to
give an example usage of pyKML.'''

    try:
        placemark = K.Placemark(
                        K.open(0),
                        K.name(attr['MRF']),
                        K.styleUrl("#sm_style"),
                        K.Point(
                            K.altitudeMode('relativeToGround'),
                            K.coordinates(",".join([attr["Longitude"],attr["Latitude"],attr["Elevation"]]))
                        ),
                        K.LookAt(
                            K.tilt(attr["Tilt"]),
                            K.longitude(attr["Longitude"]),
                            K.latitude(attr["Latitude"]),
                            K.range(40000)
                        ),
                        K.Snippet("<![CDATA[<P>"+attr["MRF"]+"</P>]]>",maxLines="0"),
                        K.description(
        """<![CDATA[<P><IMG alt="%(MRF)s image" src="%(IMG)s" align=top></P>

        <P>&nbsp;</P>

        <P><STRONG><FONT size=4>Astronaut Photograph</FONT></STRONG></P>

        <P><STRONG>Features</STRONG>: %(Features)s</P>

        <P><STRONG>Acquired</STRONG>: %(YYYYMMDD)s (YYYYMMDD), %(HHMMSS)s (HHMMSS) GMT</P>

        <P><STRONG>Camera Tilt</STRONG>: %(Camera Tilt)s&nbsp; <STRONG>Camera Lens</STRONG>: %(Camera Lens)s&nbsp; <STRONG>Camera</STRONG>: %(Camera)s</P>

        <P><STRONG>Sun Azimuth</STRONG>: %(Sun Azimuth)s&nbsp; <STRONG>Sun Elevation</STRONG>: %(Sun Elevation)s&nbsp;<STRONG>Spacecraft Altitude</STRONG>: %(Spacecraft Altitude)s nautical miles</P>

        <P><STRONG>Database Entry Page</STRONG>: <FONT face=Arial><A href='%(DB Entry)s'>%(DB Entry)s</A></FONT></P>

        <P><STRONG><FONT color="red">Astronaut photographs are not georectified, and therefore have orientation and scale independent from Google Earth base imagery.</FONT></STRONG></P>

        <P>&nbsp;</P>

        <P align=center><FONT face=Arial>&nbsp;Image Science and Analysis Laboratory, NASA-Johnson Space Center. "The Gateway to Astronaut Photography of Earth." <BR><A href="http://eol.jsc.nasa.gov/"><IMG height=71 alt="Crew Earth Observations" src="http://eol.jsc.nasa.gov/images/CEO.jpg" width=82 align=left border=0></A> <A href="http://www.nasa.gov/" target=_blank><IMG height=71 alt="NASA meatball" src="http://eol.jsc.nasa.gov/images/NASA.jpg" width=82 align=right border=0></A> <!--{PS..3}--><!--{PS..4}--><!--{PS..6}--><BR>Send questions or comments to the NASA Responsible Official at <A href="mailto:jsc-earthweb@mail.nasa.gov">jsc-earthweb@mail.nasa.gov</A><BR>Curator: <A onclick="window.open('/credits.htm', 'win1', config='height=598, width=500')" href="http://eol.jsc.nasa.gov/#" alt="Web Team">Earth Sciences Web Team</A><BR>Notices: <A href="http://www.jsc.nasa.gov/policies.html" target=_blank>Web Accessibility and Policy Notices, NASA Web Privacy Policy</A><BR><!--{PS..5}--></FONT></P>]]>""" %attr
                        )
                        
                    )
    except:
        return None
    return placemark

def writeKML(fileName,images):
    '''Writes the search results out as a kml file containing placemarks'''
    ct = 0
    kmlfile = open(fileName,'w')
    placemarks = []
    
    print "\nWriting " + repr(len(images)) + " images to kml"

    #make a placemark for each image
    for image in images:
        attr = None
        try:
            attr = ParsePlacemark("http://eol.jsc.nasa.gov/scripts/sseop/PhotoKML.pl?photo=%(Mission)s-%(Roll)s-%(Frame)s"%image)
        except Exception:
            print "Failed to open URL<%(Page)s>: http://eol.jsc.nasa.gov/scripts/sseop/PhotoKML.pl?photo=%(Mission)s-%(Roll)s-%(Frame)s"%image
            print Exception
        if attr == None:
            print "Error Parsing URL<%(Page)s>: http://eol.jsc.nasa.gov/scripts/sseop/PhotoKML.pl?photo=%(Mission)s-%(Roll)s-%(Frame)s"%image
        else:
            placemarks += [placeMaker(attr)]
        ct += 1
        if ct%10 == 0:
            sys.stdout.write(".")
            sys.stdout.flush()

    #create the kml file
    doc =  K.kml(
                K.Document(
                            K.Style(
                                    K.LabelStyle(K.scale("0")),
                                    id="sn_style"
                            ),
                            K.Style(
                                    K.LabelStyle(K.scale("1.1")),
                                    id="sh_style"
                            ),
                            K.StyleMap(
                                    K.Pair(
                                        K.key("normal"),
                                        K.styleUrl("#sn_style")
                                    ),
                                    K.Pair(
                                        K.key("normal"),
                                        K.styleUrl("#sh_style")
                                    ),
                                    id="sm_style"
                            ),
                            *placemarks
                            )
                )
    from lxml import etree
    kmlfile.write(etree.tostring(doc))

    print "\nDone!"


if __name__=="__main__":
    main()
    