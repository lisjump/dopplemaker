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
    	
        DEBUG = True
        
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
        leggings.drawSeam()
        resizeDoc(doc, 1*IN, leggings)  

def Leggings(l, m):
	# Leggings Front
	# pattern points
	A = l.pointXY('A', 0, 0)
	B = l.point('B', downPoint(A, m['waist_waistband_side']))
	C = l.point('C', downPoint(A, m['waist_hip_side']))
	D = l.point('D', downPoint(A, m['crotch_depth']))
	E = l.point('E', downPoint(A, m['waist_knee']))
	F = l.point('F', downPoint(A, m['waist_ankle']))
	
	C1 = l.point('C1', leftPoint(C, m['hip_arc_back']/2))
	C2 = l.point('C2', rightPoint(C, m['hip_arc_front']/2))
	
	E1 = l.point('E1', leftPoint(E, m['knee']/2))
	E2 = l.point('E2', rightPoint(E, m['knee']/2))

	F1 = l.point('F1', leftPoint(F, m['ankle']/2))
	F2 = l.point('F2', rightPoint(F, m['ankle']/2))
	
	B1 = l.point('B1', highest(intersectCircles(B, m['waistband_arc_back']/2, C1, m['waist_hip_back'] - m['waist_waistband_back'])))
	B2 = l.point('B2', highest(intersectCircles(B, m['waistband_arc_front']/2, C2, m['waist_hip_front'] - m['waist_waistband_front'])))

	A1 = l.point('A1', highest(intersectCircles(A, m['waist_arc_back']/2, B1, m['waist_waistband_back'])))
	A2 = l.point('A2', highest(intersectCircles(A, m['waist_arc_front']/2, B2, m['waist_waistband_front'])))
	
	D1 = l.point('D1', leftmost(intersectCircleAtY(C1, m['waist_crotch_back'] - m['waist_hip_back'], D.y)))
	D2 = l.point('D2', rightmost(intersectCircleAtY(C2, m['waist_crotch_front'] - m['waist_hip_front'], D.y)))
	D3 = l.point('D3', leftPoint(D, m['thigh']/2))
	D4 = l.point('D4', rightPoint(D, m['thigh']/2))

# 	a2 = bf.point('2', upPoint(aA, m['torso_center_front']))
# 	a3 = bf.point('3', leftPoint(a1, m['across_shoulder_front']/2))
# 	a4 = bf.point('4', leftPoint(a1, m['across_chest']/2))
# 	aB = bf.point('B', highest(intersectCircleAtX(aA, m['shoulder_slope_front'], a3.x)))
# 	aC = bf.point('C', highest(intersectCircleAtY(aB, m['shoulder_length'], a3.y)))
# 	a6 = bf.point('6', leftPoint(aA, m['bust_arc']/2))
# 	aE = bf.point('E', upPoint(a6, m['side_length']))
# 	aF = bf.point('F', downPoint(a2, distance(a1, a2)/2))
# 	aG = bf.point('G', leftPoint(aF, m['across_chest']/2))

# 
# 	# Armhole Curve
# 	aB.c1 = bf.cpoint(aB, 1, intersectLineAtLength(aB, aC, distance(aB, aG)/3, 90))
# 	aG.c1 = bf.cpointXY(aG, 1, aG.x, aE.y + (aG.y-aE.y)/5)
# 	aG.c2 = bf.cpoint(aG, 2, intersectLineAtLength(aG, aG.c1, -distance(aB, aB.c1)))
# 	aE.c2 = bf.cpoint(aE, 2, intersectLineAtLength(aE, aD, (aG.c1.x-aE.x)*4.0/8, -90))

	# grainline, darts, and seams
	aG1 = downPoint(leftPoint(B, 2*IN), (m['waist_ankle'] - m['waist_waistband_side'])*1/3)
	aG2 = downPoint(aG1, (m['waist_ankle'] - m['waist_waistband_side'])/3)
	l.declareGrainline(aG1, aG2)
	l.declareSeam(A, B)
# 	bf.addDart(aF, aE, aI, aJ)
# 	if DEBUG:
# 	  writeSomething(bf.layer, "bf: " + str(bf.lengthOfCurve([aH, a13, aD, a9])/90), 0, -2*IN)


effect=LeggingsChildren()
effect.affect()

