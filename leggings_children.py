#!/usr/bin/python
#
# leggings_picnick.py
# Inkscape extension-Effects-Sewing Patterns-Leggings-Children

'''
Licensing paragraph:

1. CODE LICENSE: GPL 2.0+
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License,or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not,write to the Free Software
Foundation,Inc.,59 Temple Place,Suite 330,Boston,MA  02111-1307  USA

2. PATTERN LICENSE: CC BY-NC 3.0
The output of this code is a pattern and is considered a
visual artwork. The pattern is licensed under
Attribution-NonCommercial 3.0 (CC BY-NC 3.0)
<http://creativecommons.org/licenses/by-nc/3.0/>
Items made from the pattern may be sold;
the pattern may not be sold.

End of Licensing paragraph.
'''

from xmlparser import *
import sys,subprocess,math,inkex,gettext,string
sys.path.append('/usr/share/inkscape/extensions')
from simplestyle import *
from sewing_patterns import *

class LeggingsChildren(inkex.Effect):
    def __init__(self):

        inkex.Effect.__init__(self)

        self.OptionParser.add_option('--m_unit',action='store',type='string',dest='unit',default='Inches')
        self.OptionParser.add_option('--size',action='store',type='string',dest='size',default='8')
        self.OptionParser.add_option('--extra',action='store',type='string',dest='extra')

        measurementsneededfile = open('leggings_children_msmnts.txt', 'r')
        measurementsneeded = list(measurementsneededfile)
        measurementsneededfile.close()
        
        for measurement in measurementsneeded:
          measurement = string.rstrip(measurement, '\n')
          self.OptionParser.add_option(("--" + str(measurement)), action='store', type='float', dest=str(measurement), default=15.0)

    def loadMeasurements(self):
    	
    	global IN, CM, MEASUREMENT_CONVERSION, m_size, DEBUG
    	
        DEBUG = False
        
        INCH_to_PX=90.0 #inkscape uses 90 pixels per 1 inch
        CM_to_INCH=1/2.54
        CM_to_PX=CM_to_INCH*INCH_to_PX
        CM=CM_to_PX # CM - shorthand when using centimeters
        IN=INCH_to_PX # IN - shorthand when using inches

        #all measurements must be converted to px
        (options, args) = self.OptionParser.parse_args()
        m = vars(options)

        if m.pop('unit')=='Centimeters':
            MEASUREMENT_CONVERSION=CM
        else:
            MEASUREMENT_CONVERSION=IN
            
        m_size = str(m.pop('size', None))
        m.pop('extra', None)
        
        if m_size != "custom":
          measurementsraw = open('children_measurements.xml', 'r')
          measurementsxml = xml2obj(measurementsraw)
          measurementsraw.close()
          
          for measurement in measurementsxml.measurement:
            name = str(measurement.name)
            if name in m.keys():
              for size in measurement.sizes.size:
                if str(size.name) == m_size and size.value:
                  m[name] = size.value
          
          try:
            measurementscustomraw = open('children_measurements_custom.xml', 'r')
            measurementscustomxml = xml2obj(measurementscustomraw)
            measurementscustomraw.close()
            for measurement in measurementscustomxml.measurement:
              name = str(measurement.name)
              if name in m.keys():
                for size in measurement.sizes.size:
                  if str(size.name) == m_size and size.value:
                    m[name] = size.value
          except (OSError, IOError):
            pass

        #convert measurements
        for key in m.keys():
          try:
            m[key] = float(m[key]) * MEASUREMENT_CONVERSION
          except TypeError:
            pass
        
        return m 

    def effect(self):
        m = self.loadMeasurements()
        doc=self.document.getroot() # self.document is the canvas seen in Inkscape

        # create layers
        leggings = PatternPiece('Size ' + m_size + ' Leggings', doc)
        layerVisible(leggings.draft, DEBUG)
          

        # pattern notes
        notes=[]
        notes.append('Set Inkscape Preferences/Steps/Outset to 56.25px (5/8 inch seam allowance)')
        notes.append('Create the Seam Allowances: Select the pattern paths & press Ctrl-)')
        notes.append('Remove Points & Gridlines: Press Ctrl-F and type "reference" in the Attribute field, click Find button, press Delete key.')
        notes.append('Print: Save as a PDF file. Open PDF with a PDF document viewer (Adobe, Evince, Okular). Print with the Print Preview option.')

        # Leggings
        Leggings(leggings, m)
        if not DEBUG:
          leggings.movePointToXY(Point('', leggings.pts['D1'].x, leggings.pts['B1'].y), 1*IN, 1*IN)
        leggings.drawSeam()
        resizeDoc(doc, 1*IN, leggings)  

def Leggings(l, m):
	# Leggings Front
	# pattern points
	a = l.pointXY('A', 0, 0)
	b = l.point('B', downPoint(a, m['waist_waistband_side']))
	hipcrotchratio = 0.8
	if (m['waist_hip_side']/m['crotch_depth']) > hipcrotchratio:
	  c = l.point('C', downPoint(a, m['crotch_depth'] * hipcrotchratio))
	  m['waist_hip_front'] = m['waist_hip_front'] - (m['waist_hip_side'] - m['crotch_depth'] * hipcrotchratio)
	  m['waist_hip_back'] = m['waist_hip_back'] - (m['waist_hip_side'] - m['crotch_depth'] * hipcrotchratio)
	else:
	  c = l.point('C', downPoint(a, m['waist_hip_side']))
	d = l.point('D', downPoint(a, m['crotch_depth']))
	e = l.point('E', downPoint(a, m['waist_knee']))
	f = l.point('F', downPoint(a, m['waist_ankle']))
	g = l.point('G', downPoint(d, distance(d, e)/4))
	
	c1 = l.point('C1', leftPoint(c, m['hip_arc_back']/2))
	c2 = l.point('C2', rightPoint(c, m['hip_arc_front']/2))
	
	e1 = l.point('E1', leftPoint(e, m['knee']/2))
	e2 = l.point('E2', rightPoint(e, m['knee']/2))

	f1 = l.point('F1', leftPoint(f, m['ankle']/2))
	f2 = l.point('F2', rightPoint(f, m['ankle']/2))
	
	b1 = l.point('B1', highest(intersectCircles(b, m['waistband_arc_back']/2, c1, m['waist_hip_back'] - m['waist_waistband_back'])))
	b2 = l.point('B2', highest(intersectCircles(b, m['waistband_arc_front']/2, c2, m['waist_hip_front'] - m['waist_waistband_front'])))

	a1 = l.point('A1', highest(intersectCircles(a, m['waist_arc_back']/2, b1, m['waist_waistband_back'])))
	a2 = l.point('A2', highest(intersectCircles(a, m['waist_arc_front']/2, b2, m['waist_waistband_front'])))
	
	d1 = l.point('D1', leftPoint(d, m['hip_arc_back']*2/3))
	d2 = l.point('D2', rightPoint(d, m['hip_arc_front']*2/3))
	
	g1 = l.point('G1', leftPoint(g, m['thigh']/2 + (m['hip_arc_back']/2 - m['hip_arc_front']/2)/2))
	g2 = l.point('G2', rightPoint(g, m['thigh'] - distance(g, g1)))

	# Crotch Curve
 	d1.c2 = l.cpoint(d1, 2, intersectLineAtLength(d1, g1, (c1.x - d1.x)/3, -90))
 	c1.c2 = l.cpoint(c1, 2, intersectLineAtLength(c1, b1, distance(c1, b1)/2))
 	c1.c1 = l.cpoint(c1, 1, intersectLineAtLength(c1, c1.c2, (c1.y - d1.c2.y)*2/3))

 	d2.c1 = l.cpoint(d2, 1, intersectLineAtLength(d2, g2, (d2.x - c2.x)/2, 90))
 	c2.c1 = l.cpoint(c2, 1, intersectLineAtLength(c2, b2, distance(c2, b2)/2))
 	c2.c2 = l.cpoint(c2, 2, intersectLineAtLength(c2, c2.c1, (c2.y - d2.c1.y)*2/3))

	# grainline, darts, and seams
	aG1 = downPoint(leftPoint(c, 2*IN), (m['waist_ankle'] - m['waist_waistband_side'])*1/3)
	aG2 = downPoint(aG1, (m['waist_ankle'] - m['waist_waistband_side'])/3)
	l.declareGrainline(aG1, aG2)
	l.declareSeam(b2, c2, d2, g2, e2, f2, f1, e1, g1, d1, c1, b1, b, b2)
	l.addGuide(b, f)
	l.addGuide(e1, e2)
	l.addGuide(g1, g2)
	l.smoothPoint(g1, .33)
	l.smoothPoint(e1, .33)
	l.smoothPoint(g2, .33)
	l.smoothPoint(e2, .33)
	l.smoothPoint(b, .33)


effect=LeggingsChildren()
effect.affect()

