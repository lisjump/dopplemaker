#!/usr/bin/python
#
# skirt_picnick.py
# Inkscape extension-Effects-Sewing Patterns-Skirt-Pivnick

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
import sys, math, inkex, string
sys.path.append('/usr/share/inkscape/extensions')
from sewing_patterns import *

class SkirtPivnick(inkex.Effect):
    def __init__(self):

        inkex.Effect.__init__(self)

        self.OptionParser.add_option('--m_unit',action='store',type='string',dest='unit',default='Inches')
        self.OptionParser.add_option('--size',action='store',type='string',dest='size',default='8')
        self.OptionParser.add_option('--cup',action='store',type='string',dest='cup',default='B')
        self.OptionParser.add_option('--extra',action='store',type='string',dest='extra')

        measurementsneededfile = open('skirt_pivnick_msmnts.txt', 'r')
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
        cup = m.pop('cup', None)
        m.pop('extra', None)
        
        if m_size != "custom":
          measurementsraw = open('women_measurements.xml', 'r')
          measurementsxml = xml2obj(measurementsraw)
          measurementsraw.close()
          
          try:
            measurementscustomraw = open('women_measurements_custom.xml', 'r')
            measurementscustomxml = xml2obj(measurementscustomraw)
            measurementscustomraw.close()
          except (OSError, IOError):
            measurementscustomxml = measurementsxml
          
          for measurement in measurementsxml.measurement:
            name = str(measurement.name)
            if name in m.keys():
              for size in measurement.sizes.size:
                if str(size.name) == m_size and size.value:
                  m[name] = size.value
          
          for measurement in measurementscustomxml.measurement:
            name = str(measurement.name)
            if name in m.keys():
              for size in measurement.sizes.size:
                if str(size.name) == m_size and size.value:
                  m[name] = size.value

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
        skirt = addLayer(doc,'Size ' + m_size + ' Skirt')
        skirt_front = PatternPiece('Skirt Front', skirt)
        skirt_back = PatternPiece('Skirt Back', skirt)

        # pattern notes
        notes=[]
        notes.append('Set Inkscape Preferences/Steps/Outset to 56.25px (5/8 inch seam allowance)')
        notes.append('Create the Seam Allowances: Select the pattern paths & press Ctrl-)')
        notes.append('Remove Points & Gridlines: Press Ctrl-F and type "reference" in the Attribute field, click Find button, press Delete key.')
        notes.append('Print: Save as a PDF file. Open PDF with a PDF document viewer (Adobe, Evince, Okular). Print with the Print Preview option.')

        # Skirt
        SkirtBack(skirt_back, m)
        SkirtFront(skirt_front, skirt_back, m)

        skirt_back.movePointToXY(Point('', skirt_back.pts['S'].x, skirt_back.pts['U'].y), 1*IN, 1*IN)
        skirt_front.movePointToPoint(skirt_front.pts['X'], rightPoint(skirt_back.pts['D'], 2*IN))

        skirt_back.drawSeam()
        skirt_front.drawSeam()
        
        resizeDoc(doc, 1*IN, skirt_front, skirt_back)

def SkirtFront(sf, sb, m):
	# pattern points
	aE = sf.point('E', rightPoint(sb.pts['E'], 3*IN))
	a4 = sf.point('4', rightPoint(sb.pts['4'], 3*IN))
	a5 = sf.point('5', rightPoint(sb.pts['5'], 3*IN))
	aD = sf.point('D', rightPoint(sb.pts['D'], 3*IN))
	aB = sf.point('B', rightPoint(a4, m['hip_arc_front']/2))
	aC = sf.point('C', rightPoint(aD, distance(a4, aB)))
	a3 = sf.point('3', upPoint(aB, m['waist_hip_front']))
	aF = sf.point('F', downPoint(a3, distance(aE, a5)))
	aH = sf.point('H', intersectLineAtLength(aF, a5, m['abdomen_front']/2))
	aI = sf.point('I', intersectLines(a4, aH, aE, a3))
	dart = (distance(aI, a3) - m['waist_arc_front']/2)/4
	a6 = sf.point('6', intersectLineAtLength(aI, a3, dart*2))
	aJ = sf.point('J', midPoint(a3, a6))
	aK = sf.point('K', intersectLineAtLength(aJ, aI, dart))
	aL = sf.point('L', intersectLineAtLength(aK, aI, dart))
	aM = sf.point('M', intersectLines(aK, intersectLineAtLength(aK, aJ, 2*IN, 90), aF, a5))
	aW = sf.point('W', intersectLineAtLength(aC, aD, distance(sb.pts['D'], sb.pts['S'])))
	aX = sf.point('X', intersectLineAtLength(a4, aW, distance(a4, aD)))
	aY = sf.point('Y', intersectLineAtLength(aK, aM, -3.0/8*IN))

	# control points
	aL.c1 = sf.cpoint(aL, 1, intersectLineAtLength(aL, aM, distance(aL, a6)/3, 90))
	aJ.c2 = sf.cpoint(aJ, 2, intersectLineAtLength(aJ, aM, distance(aL, aL.c1), -90))
	a4.c2 = sf.cpoint(a4, 2, aH)
	a6.c1 = sf.cpoint(a6, 1, aH)
	a6.c2 = sf.cpoint(a6, 2, intersectLineAtLength(a6, aH, distance(a6, aL)/3, -90))
	aX.c1 = sf.cpoint(aX, 1, intersectLineAtLength(aX, a4, distance(aX, aC)/2, 90))
	aC.c2 = sf.cpoint(aC, 2, intersectLineAtLength(aC, a3, distance(aX, aC)/8, -90))

	# grainline, darts, and seams
	aG1 = leftPoint(aF, 2*IN)
	aG2 = downPoint(aG1, m['waist_hip_front'])
	sf.declareGrainline(aG1, aG2)
	sf.declareSeam(a6, aL, aY, aJ, a3, aC, aX, a4, a6)
	sf.addDart(aL, aJ, aM, aY)
        
def SkirtBack(sb, m):
	bE = sb.pointXY('E', m['hip_arc_back']/2 + 2*IN, 1*IN)
	b5 = sb.point('5', downPoint(bE, m['waist_hip_front']*3/8))
	b4 = sb.point('4', downPoint(bE, m['waist_hip_side']))
	bD = sb.point('D', downPoint(bE, m['waist_knee']))
	b2 = sb.point('2', leftPoint(b4, m['hip_arc_back']/2))
	b1 = sb.point('1', leftPoint(bD, distance(b2, b4)))
	bA = sb.point('A', upPoint(b2, m['waist_hip_back']))
	bG = sb.point('G', downPoint(bA, distance(bE, b5)))
	dart = (distance(bA, bE) - m['waist_arc_back']/2)/4
	bN = sb.point('N', intersectLineAtLength(bE, bA, dart))
	bO = sb.point('O', intersectLineAtLength(bA, bE, dart))
	bS = sb.point('S', intersectLineAtLength(bO, b2, distance(bA, b1)))
	bP = sb.point('P', midPoint(bO, bN))
	bQ = sb.point('Q', intersectLineAtLength(bP, bE, dart))
	bR = sb.point('R', intersectLineAtLength(bQ, bE, dart))
	bT = sb.point('T', intersectLineAtLength(bQ, bP, m['waist_hip_back']*11/16, -90))
	bU = sb.point('U', intersectLineAtLength(bQ, bT, -3.0/8*IN))

	# control points
	bP.c1 = sb.cpoint(bP, 1, intersectLineAtLength(bP, bT, distance(bP, bO)/3, 90))
	bR.c1 = sb.cpoint(bR, 2, intersectLineAtLength(bR, bT, distance(bN, bR)/3, -90))
	bN.c2 = sb.cpoint(bN, 2, b4)
	bD.c1 = sb.cpoint(bD, 1, b4)
	bO.c1 = sb.cpoint(bO, 2, intersectLineAtLength(bO, bS, distance(bO, bP)/3, -90))
	bN.c1 = sb.cpoint(bN, 1, intersectLineAtLength(bN, b4, distance(bN, bR)/3, 90))
	bS.c1 = sb.cpoint(bS, 1, intersectLineAtLength(bS, bO, distance(bS, bD)/2, 90))
	bD.c1 = sb.cpoint(bD, 2, intersectLineAtLength(bD, b4, distance(bS, bD)/8, -90))

	# grainline, darts, and seams
	bG1 = rightPoint(bG, 2*IN)
	bG2 = downPoint(bG1, m['waist_hip_back'])
	sb.declareGrainline(bG1, bG2)
	sb.declareSeam(bO, bP, bU, bR, bN, bD, bS, bO)
	sb.addDart(bP, bR, bT, bU)

        
        
        

effect=SkirtPivnick()
effect.affect()

