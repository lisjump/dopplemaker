#!/usr/bin/python
#
# dress_picnick.py
# Inkscape extension-Effects-Sewing Patterns-Dress-Pivnick

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

class DressPivnick(inkex.Effect):
    def __init__(self):

        inkex.Effect.__init__(self)

        self.OptionParser.add_option('--m_unit',action='store',type='string',dest='unit',default='Inches')
        self.OptionParser.add_option('--size',action='store',type='string',dest='size',default='8')
        self.OptionParser.add_option('--cup',action='store',type='string',dest='cup',default='B')
        self.OptionParser.add_option('--sleeves',action='store',type='string',dest='sleeves',default='no')
        self.OptionParser.add_option('--extra',action='store',type='string',dest='extra')

        measurementsneededfile = open('dress_pivnick_msmnts.txt', 'r')
        measurementsneeded = list(measurementsneededfile)
        measurementsneededfile.close()
        
        for measurement in measurementsneeded:
          measurement = string.rstrip(measurement, '\n')
          self.OptionParser.add_option(("--" + str(measurement)), action='store', type='float', dest=str(measurement), default=15.0)

    def loadMeasurements(self):
    	
    	global IN, CM, MEASUREMENT_CONVERSION, m_size, DEBUG, SLEEVE
    	
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
        if m.pop('sleeves', None) == "yes":
          SLEEVE = True
        else:
          SLEEVE = False
        
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
        pattern = addLayer(doc, 'Size ' + m_size + ' Dress')
        bodice = addLayer(pattern, 'bodice')
        bodice_front = PatternPiece('bodice front', bodice)
        bodice_back = PatternPiece('bodice back', bodice)
        skirt = addLayer(pattern,'skirt')
        skirt_front = PatternPiece('skirt front', skirt)
        skirt_back = PatternPiece('skirt back', skirt)
        dress = addLayer(pattern,'dress')
        dress_front = PatternPiece('dress front', dress)
        dress_back = PatternPiece('dress back', dress)
        if SLEEVE:
          sleeve = PatternPiece('sleeve', dress)

        layerVisible(bodice, DEBUG)
        layerVisible(skirt, DEBUG)
        
        # pattern notes
        notes=[]
        notes.append('Set Inkscape Preferences/Steps/Outset to 56.25px (5/8 inch seam allowance)')
        notes.append('Create the Seam Allowances: Select the pattern paths & press Ctrl-)')
        notes.append('Remove Points & Gridlines: Press Ctrl-F and type "reference" in the Attribute field, click Find button, press Delete key.')
        notes.append('Print: Save as a PDF file. Open PDF with a PDF document viewer (Adobe, Evince, Okular). Print with the Print Preview option.')

        # Bodice
        BodiceFront(bodice_front, m)
        BodiceBack(bodice_front, bodice_back, m)
        if SLEEVE:
          Sleeve(sleeve, bodice_front, bodice_back, m)
          sleeve.layerVisible(True, DEBUG)
        
        # Skirt
        SkirtBack(skirt_back, bodice_back, m)
        SkirtFront(skirt_front, skirt_back, bodice_front, m)
        
        newSize = distance(skirt_front.pts['L'], skirt_front.pts['J'])
        bodice_front.moveDart(['F', 'E', 'I', 'J'], newSize, ['L', 'M', 'N', 'D'], bodice_front.pts['6'])

        bodice_front.drawSeam()
        skirt_front.drawSeam()
        bodice_back.drawSeam()
        skirt_back.drawSeam()


        bodice_front.movePointToPoint(midPoint(bodice_front.pts['E'], bodice_front.pts['F']), midPoint(skirt_front.pts['J'], skirt_front.pts['L']))
        bodice_back.movePointToPoint(bodice_back.pts['A'], skirt_back.pts['O'])
        
        
        # Dress
        dress_front.addPieces(('bf', bodice_front), ('sf', skirt_front))
        updatePoint(dress_front.pts['sfM'], downPoint(dress_front.pts['bfI'], distance(dress_front.pts['sfM'], dress_front.pts['bfI'])))
        dart_length = distance(dress_front.pts['bfE'], dress_front.pts['bfF'])
        updatePoint(dress_front.pts['bfE'], leftPoint(intersectLines(dress_front.pts['bfI'], dress_front.pts['sfM'], dress_front.pts['bfF'], dress_front.pts['bfE']), dart_length/2))
        updatePoint(dress_front.pts['bfF'], rightPoint(dress_front.pts['bfE'], dart_length))
        dress_front.declareGrainline(bodice_front.grainline[0], bodice_front.grainline[1])
        dress_front.declareSeamFromIds('bfH', 'bf13', 'bfL', 'bfD', 'bfM', 'bf9', 'bf10', 'bf2', 'sfC', 'sfX', 'sf4', 'bf12', 'bfH')
        dress_front.cpoint(dress_front.pts['bf12'], 2, upPoint(dress_front.pts['bf12'], 2*IN))
        dress_front.cpoint(dress_front.pts['bf12'], 1, downPoint(dress_front.pts['bf12'], 2*IN))
        dress_front.cpoint(dress_front.pts['sf4'], 1, intersectLineAtLength(dress_front.pts['sf4'], dress_front.pts['sfX'], 2*IN))
        dress_front.cpoint(dress_front.pts['sf4'], 2, intersectLineAtLength(dress_front.pts['sf4'], dress_front.cpts[dress_front.pts['sf4']][1], -distance(dress_front.pts['sf4'], dress_front.pts['bf12'])/2))
        dress_front.addDart(dress_front.pts['bfM'], dress_front.pts['bfL'], dress_front.pts['bfN'], dress_front.pts['bfD'])
        dress_front.addDart(dress_front.pts['bfE'], dress_front.pts['bfF'], dress_front.pts['bfI'], dress_front.pts['sfM'])
        dress_front.addDart(dress_front.pts['bfE'], dress_front.pts['bfF'], dress_front.pts['sfM'], dress_front.pts['bfI'])
        
        dress_back.addPieces(('bb', bodice_back), ('sb', skirt_back))
        dress_back.declareGrainline(bodice_back.grainline[0], bodice_back.grainline[1])
        dress_back.addDart(dress_back.pts['bbQ'], dress_back.pts['bbS'], dress_back.pts['bbP'], dress_back.pts['bbT'])
        if SLEEVE:
          dress_back.declareSeamFromIds('bb2', 'bb7', 'bbQ', 'bbT', 'bbS', 'bb6', 'bbH', 'bb11', 'sbD', 'sbS', 'bb2')
        else:
          dress_back.declareSeamFromIds('bb2', 'bb7', 'bbQ', 'bbT', 'bbS', 'bb6', 'bbB', 'bbH', 'bb11', 'sbD', 'sbS', 'bb2')
        dress_back.cpoint(dress_back.pts['bb11'], 1, upPoint(dress_back.pts['bb11'], 2*IN))
        dress_back.cpoint(dress_back.pts['bb11'], 2, downPoint(dress_back.pts['bb11'], 2*IN))
        dress_back.cpoint(dress_back.pts['sbD'], 1, dress_back.pts['sb4'])
        updatePoint(dress_back.pts['sbT'], downPoint(dress_back.pts['bbI'], distance(dress_back.pts['bbI'], dress_back.pts['sbT'])))
        dart_length = distance(dress_back.pts['bbF'], dress_back.pts['bbG'])
        updatePoint(dress_back.pts['bbF'], leftPoint(intersectLines(dress_back.pts['bbI'], dress_back.pts['sbT'], dress_back.pts['bbF'], dress_back.pts['bbG']), dart_length/2))
        updatePoint(dress_back.pts['bbG'], rightPoint(dress_back.pts['bbF'], dart_length))
        dress_back.addDart(dress_back.pts['bbF'], dress_back.pts['bbG'], dress_back.pts['sbT'], dress_back.pts['bbI'])
        dress_back.addDart(dress_back.pts['bbF'], dress_back.pts['bbG'], dress_back.pts['bbI'], dress_back.pts['sbT'])
        dress_back.addDart(dress_back.pts['bbQ'], dress_back.pts['bbS'], dress_back.pts['bbP'], dress_back.pts['bbT'])

        dress_back.movePointToXY(dress_back.pts['bb1'], 1*IN, 1*IN)
        dress_front.movePointToPoint(dress_front.pts['sfX'], rightPoint(dress_back.pts['sbD'], 2*IN))
        dress_front.drawSeam()
        dress_back.drawSeam()
        
        if SLEEVE:
          sleeve.movePointToPoint(Point('', sleeve.pts['D'].x, sleeve.pts['A'].y), Point('', dress_front.pts['bf1'].x + 2*IN, 1*IN))
          sleeve.drawSeam()
          

        if SLEEVE:
          resizeDoc(doc, 1*IN, dress_front, dress_back, sleeve)
        else:
          resizeDoc(doc, 1*IN, dress_front, dress_back)
        
        
        
def SkirtFront(sf, sb, bf, m):
	# pattern points
	aE = sf.point('E', rightPoint(sb.pts['E'], 3*IN))
	a4 = sf.point('4', rightPoint(sb.pts['4'], 3*IN))
	a5 = sf.point('5', rightPoint(sb.pts['5'], 3*IN))
	aD = sf.point('D', rightPoint(downPoint(sb.pts['E'], distance(sb.pts['E'], sb.pts['D'])), 3*IN))
	aB = sf.point('B', rightPoint(a4, m['hip_arc_front']/2))
	aC = sf.point('C', rightPoint(aD, distance(a4, aB)))
	a3 = sf.point('3', upPoint(aB, m['waist_hip_front']))
	aF = sf.point('F', downPoint(a3, distance(aE, a5)))
	aH = sf.point('H', intersectLineAtLength(aF, a5, m['abdomen_front']/2))
	aI = sf.point('I', intersectLines(a4, aH, aE, a3))
	dart = (distance(aI, a3) - m['waist_arc_front']/2)/4
	a6 = sf.point('6', intersectLineAtLength(aI, a3, 0))
	aJ = sf.point('J', intersectLineAtLength(a3, a6, distance(bf.pts['A'], bf.pts['E'])))
	aK = sf.point('K', intersectLineAtLength(aJ, aI, dart*2))
	aL = sf.point('L', intersectLineAtLength(aK, aI, dart*2))
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
        
def SkirtBack(sb, bb, m):
	bE = sb.pointXY('E', m['hip_arc_back']/2 + 2*IN, 1*IN)
	b5 = sb.point('5', downPoint(bE, m['waist_hip_front']*3/8))
	b4 = sb.point('4', downPoint(bE, m['waist_hip_side']))
	bD = sb.point('D', downPoint(bE, m['waist_knee']))
	b2 = sb.point('2', leftPoint(b4, m['hip_arc_back']/2))
	b1 = sb.point('1', leftPoint(bD, distance(b2, b4)))
	bA = sb.point('A', upPoint(b2, m['waist_hip_back']))
	bG = sb.point('G', downPoint(bA, distance(bE, b5)))
	dart = (distance(bA, bE) - m['waist_arc_back']/2)
	bN = sb.point('N', intersectLineAtLength(bE, bA, dart - distance(bb.pts['F'], bb.pts['G'])))
	bO = sb.point('O', intersectLineAtLength(bA, bE, 0))
	bS = sb.point('S', intersectLineAtLength(bO, b2, distance(bA, b1)))
	bP = sb.point('P', rightPoint(bO, distance(bb.pts['F'], bb.pts['A'])))
	bQ = sb.point('Q', intersectLineAtLength(bP, bE, distance(bb.pts['F'], bb.pts['G'])/2))
	bR = sb.point('R', intersectLineAtLength(bQ, bE, distance(bb.pts['F'], bb.pts['G'])/2))
	bT = sb.point('T', intersectLineAtLength(bQ, bP, m['waist_hip_back']*11/16, -90))
	bU = sb.point('U', intersectLineAtLength(bQ, bT, -3.0/8*IN))
	bD = sb.point('D', intersectLineAtLength(leftPoint(bE, dart/4), b4, distance(bE, bD)))

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

def BodiceFront(bf, m):
	# Bodice Front
	# pattern points
	aA = bf.pointXY('A', m['bust_arc'] + 2*IN, m['torso_full_front'] + 1*IN)
	a1 = bf.point('1', upPoint(aA, m['torso_full_front']))
	a2 = bf.point('2', upPoint(aA, m['torso_center_front']))
	a3 = bf.point('3', leftPoint(a1, m['across_shoulder_front']/2))
	a4 = bf.point('4', leftPoint(a1, m['across_chest']/2))
	a5 = bf.point('5', downPoint(a1, m['neck_bust']))
	a6 = bf.point('6', leftPoint(a5, m['bust_span']/2))
	aB = bf.point('B', upPoint(a5, 2*IN))
	a7 = bf.point('7', rightPoint(aB, m['bust_width']/2 - m['full_width_front']/2))
	a8 = bf.point('8', intersectLineAtLength(a6, a5, -(m['bust_width']/2 - distance(a5, a6)), -(1.0/slopeOfLine(a7, a5))*180/math.pi))
	a9 = bf.point('9', highest(intersectCircleAtX(aA, m['shoulder_slope_front'], a3.x)))
	a10 = bf.point('10', rightmost(intersectCircleAtY(a9, m['shoulder_length'], a3.y)))
	a11 = bf.point('11', intersectLines(a10, intersectLineAtLength(a10, a9, 2*IN, 90), a2, leftPoint(a2, 5*IN)))
	aD = bf.point('D', lowest(intersectCircleAtX(a9, m['shoulder_side_front']/4, a4.x)))
	a12 = bf.point('12', lowest(intersectLineCircle_old(aD, m['shoulder_side_front'] - distance(a9, aD), a8, intersectLineAtLength(a8, a6, 2*IN, 90))))
	if SLEEVE:
	  a13 = bf.point('13', intersectLineAtLength(a12, a8, m['side_length']-3.0/8*IN))
	  aG = bf.point('G', intersectLineAtLength(a13, a12, (3.0/4)*IN, 90))
	else:  
	  a13 = bf.point('13', intersectLineAtLength(a12, a8, m['side_length']))
	  aG = bf.point('G', intersectLineAtLength(a13, a12, 0, 90))
	aH = bf.point('H', intersectLineAtLength(a12, aG, distance(a12, a13)))
	a14 = bf.point('14', leftPoint(aA, distance(a5, a6)))
	dart = distance(aA, a14) + distance(a14, a12) - m['waist_arc_front']/2
	aE = bf.point('E', intersectLineAtLength(a14, aA, dart/4))
	aF = bf.point('F', intersectLineAtLength(a14, a12, dart*3.0/4))
	aF = bf.point('F', intersectLineAtLength(a6, aF, distance(a6, aE)))
	aI = bf.point('I', intersectLineAtLength(a6, midPoint(aE, aF), 3.0/8*IN))
	aJ = bf.point('J', intersectLineAtLength(aI, midPoint(aE, aF), distance(a6, aE)))

	# Armhole Curve
	a9.c1 = bf.cpoint(a9, 1, intersectLineAtLength(a9, a10, distance(a9, aD)/3, 90))
	aD.c1 = bf.cpointXY(aD, 1, aD.x, a13.y)
	aD.c2 = bf.cpoint(aD, 2, intersectLineAtLength(aD, aD.c1, -distance(a9, a9.c1)))
	a13.c2 = bf.cpoint(a13, 2, intersectLineAtLength(a13, a12, (aD.c1.x-a13.x)*4.0/8, -90))

	# Neck Curve
	a10.c2 = bf.cpoint(a10, 2, intersectLineAtLength(a10, a11, distance(a10, a11)*2.0/3))
	a2.c1 = bf.cpoint(a2, 1, intersectLineAtLength(a2, a11, distance(a2, a11)*2.0/3))

	# Dart Curves
	aF.c2 = bf.cpoint(aF, 2, intersectLineAtLength(aF, aI, distance(aF, a12)/3, -90))
	aE.c1 = bf.cpoint(aE, 1, intersectLineAtLength(aE, aI, distance(aE, aA)/3, 90))
	a12.c1 = bf.cpoint(a12, 1, intersectLineAtLength(a12, aH, distance(aF, a12)/3, 90))
	aA.c2 = bf.cpoint(aA, 2, intersectLineAtLength(aA, a2, distance(aE, aA)/3, -90))
	a9.c2 = bf.cpoint(a9, 2, intersectLineAtLength(midPoint(a9, a10), a9, 3.0/16*IN, -90))

	# grainline, darts, and seams
	aG1 = upPoint(midPoint(aA, aE), m['torso_center_front']*2/3)
	aG2 = downPoint(aG1, m['torso_center_front']/3)
	bf.declareGrainline(aG1, aG2)
	bf.declareSeam(aA, aE, aJ, aF, a12, aH, a13, aD, a9, a10, a2, aA)
	bf.addDart(aF, aE, aI, aJ)


def BodiceBack(bf, bb, m):
	#Bodice Back
	#Pattern Points
	bA = bb.point('A', rightPoint(bf.pts['A'], 1.5*IN))
	b1 = bb.point('1', upPoint(bA, m['torso_full_back']))
	b2 = bb.point('2', upPoint(bA, m['torso_center_back']))
	b3 = bb.point('3', rightPoint(b1, m['across_shoulder_back']/2))
	b4 = bb.point('4', rightPoint(b1, m['across_back']/2))
	b5 = bb.point('5', rightPoint(b1, m['full_width_back']/2))
	b6 = bb.point('6', highest(intersectCircleAtX(bA, m['shoulder_slope_back'], b3.x)))
	b7 = bb.point('7', rightmost(intersectCircleAtY(b2, m['neck_back']/2, b3.y)))
	b8 = bb.point('8', intersectLines(b7, intersectLineAtLength(b7, b6, 2*IN, 90), b2, rightPoint(b2, 2*IN)))
	bB = bb.point('B', lowest(intersectCircleAtX(b6, m['shoulder_side_back']/4, b4.x)))
	b9 = bb.point('9', lowest(intersectCircleAtX(bB, m['shoulder_side_back'] - distance(b6, bB), b5.x)))
	b10 = bb.point('10', upPoint(b9, distance(bf.pts['12'], bf.pts['13'])))
	if SLEEVE:
	  bC = bb.point('C', rightPoint(b10, 3.0/4*IN))
	else:
	  bC = bb.point('C', rightPoint(b10, 0*IN))
	bD = bb.point('D', intersectLineAtLength(b9, bA, (distance(bA, b9) - m['waist_arc_back']/2)/2))
	bE = bb.point('E', midPoint(bA, bD))
	bF = bb.point('F', intersectLineAtLength(bE, bA, distance(bD, b9)/2))
	bG = bb.point('G', intersectLineAtLength(bE, b9, distance(bD, b9)/2))
	b11 = bb.point('11', intersectLineAtLength(bB, bD, distance(bB, b9)))
	bH = bb.point('H', intersectLineAtLength(b11, bC, distance(b10, b9)))
	bM = bb.pointXY('M', bA.x, bH.y)
	bI = bb.point('I', rightPoint(bM, distance(bA, bE)))
	bR = midPoint(b7, b6)
	bP = bb.point('P', intersectLineAtLength(bR, bI, distance(b6,bB)*2.0/3))
	bQ = bb.point('Q', intersectLineAtLength(bR, b7, (distance(b7, b6) - m['shoulder_length'])/2))
	bS = intersectLineAtLength(bR, b6, distance(bR, bQ))
	bS = bb.point('S', intersectLineAtLength(bP, bS, distance(bP, bQ)))
	bR = midPoint(bS, bQ)
	bT = bb.point('T', intersectLineAtLength(bR, bP, -1.0/8*IN))
	bN = bb.point('N', downPoint(bE, 3.0/8*IN)) 

	# Control Points
	b2.c2 = bb.cpoint(b2, 2, rightPoint(b2, distance(b2, b8)/2))
	b7.c1 = bb.cpoint(b7, 1, b8)
	shortof180 = (180-angleOfVector(bP, bQ, b7)*180.0/math.pi) + angleOfVector(bP, bS, b6)*180.0/math.pi
	bQ.c1 = bb.cpoint(bQ, 1, intersectLineAtLength(bQ, b7, distance(bQ, b7)/2, -shortof180/2))
	bS.c2 = bb.cpoint(bS, 2, intersectLineAtLength(bS, b6, distance(bS, b6)/2, shortof180/2))
	if SLEEVE:
	  b6.c2 = bb.cpoint(b6, 2, intersectLineAtLength(b6, bS, distance(b6, bB)*2.0/3, -90))
	  bH.c1 = bb.cpoint(bH, 1, intersectLineAtLength(bH, b11, (bH.x-b6.c2.x), 90))
	else:
	  b6.c2 = bb.cpoint(b6, 2, intersectLineAtLength(b6, bS, distance(b6, bB)/4, -90))
	  bB.c1 = bb.cpoint(bB, 1, intersectLineAtLength(bB, b6.c2, distance(b6, b6.c2)))
	  bB.c2 = bb.cpoint(bB, 2, intersectLineAtLength(bB, bB.c1, -distance(bB, bB.c1)))
	  bH.c1 = bb.cpoint(bH, 1, intersectLineAtLength(bH, b11, (bH.x-bB.c1.x)*3.0/4, 90))
	bF.c2 = bb.cpoint(bF, 2, intersectLineAtLength(bF, bI, distance(bF, bA)/3, -90))
	bG.c1 = bb.cpoint(bG, 1, intersectLineAtLength(bG, bI, distance(bG, b11)/3, 90))
	bA.c1 = bb.cpoint(bA, 1, intersectLineAtLength(bA, b2, distance(bF, bA)/3, 90))
	b11.c2 = bb.cpoint(b11, 2, intersectLineAtLength(b11, bH, distance(bG, b11)/3, -90))
	

	# grainline, darts, and seams
	bG1 = upPoint(midPoint(bA, bF), m['torso_center_back']*2/3)
	bG2 = downPoint(bG1, m['torso_center_back']/3)
	bb.declareGrainline(bG1, bG2)
	if SLEEVE:
	  bb.declareSeam(bA, b2, b7, bQ, bT, bS, b6, bH, b11, bG, bN, bF, bA)
	else:
	  bb.declareSeam(bA, b2, b7, bQ, bT, bS, b6, bB, bH, b11, bG, bN, bF, bA)
	bb.addDart(bF, bG, bI, bN)
	bb.addDart(bQ, bS, bP, bT)
	if DEBUG:
	  writeSomething(bb.layer, "bb: " + str(bb.lengthOfCurve([b6, bH])/90), 0, -3*IN)

def Sleeve(sl, bf, bb, m):
  sA = sl.pointXY('A', 0, 0)
  sB = sl.point('B', downPoint(sA, m['shoulder_wrist']))
  sC = sl.point('C', upPoint(sB, m['underarm']))
  s4 = sl.point('4', downPoint(sA, m['shoulder_elbow']))
  s5 = sl.point('5', leftPoint(s4, m['elbow']/2))
  s6 = sl.point('6', rightPoint(s4, distance(s4, s5)))
  sD = sl.point('D', leftPoint(sC, (m['upperarm_width'] + 1*IN)/2 + m['upperarm_width']/32))
  sE = sl.point('E', rightPoint(sC, (m['upperarm_width'] + 1*IN) - distance(sC, sD)))
  sJ = sl.point('J', leftPoint(sB, (m['wrist'] + 1.0/2*IN)/2))
  sK = sl.point('K', rightPoint(sB, distance(sB, sJ)))
  sF = sl.point('F', rightPoint(sD, distance(sD, sC)/4))
  sG = sl.point('G', leftPoint(sE, distance(sE, sC)/8))
  sH = sl.point('H', rightPoint(sA, distance(sF, sD) + distance(sG, sE)))
  sL = sl.point('L', leftPoint(sA, distance(sF, sD)*2))
  s1 = sl.point('1', intersectLineAtLength(sF, sL, distance(sF, sD)))
  s2 = sl.point('2', intersectLineAtLength(sG, sH, distance(sG, sE)))
  s3 = sl.point('3', intersectLineAtLength(sH, sG, distance(sH, sA)))
  
  sA.c2 = sl.cpoint(sA, 2, intersectLineAtLength(sA, sH, distance(sA, sH)/2))
  s3.c1 = sl.cpoint(s3, 1, intersectLineAtLength(s3, sH, distance(s3, sH)/2))
  s2.c2 = sl.cpoint(s2, 2, intersectLineAtLength(s2, sG, distance(s2, sG)/2))
  sE.c1 = sl.cpoint(sE, 1, intersectLineAtLength(sE, sG, distance(sE, sG)/2))
  
  sD.c2 = sl.cpoint(sD, 2, intersectLineAtLength(sD, sF, distance(sD, sF)/2))
  s1.c1 = sl.cpoint(s1, 1, intersectLineAtLength(s1, sF, distance(s1, sF)/2))
  s1.c2 = sl.cpoint(s1, 2, intersectLineAtLength(s1, sL, distance(s1, sL)*2/3))
  sA.c1 = sl.cpoint(sA, 1, intersectLineAtLength(sA, sL, distance(sA, sL)*2/3))

  if DEBUG:
    writeSomething(sl.layer, "sb: " + str(sl.lengthOfCurve([sA, s3, s2, sE])/90), 0, -5*IN)
    writeSomething(sl.layer, "sf: " + str(sl.lengthOfCurve([sD, s1, sA])/90), 0, -4*IN)
  
  sl.declareSeam(sA, s3, s2, sE, s6, sK, sJ, s5, sD, s1, sA)
  sl.declareGrainline(rightPoint(sC, 1*IN), rightPoint(s4, 1*IN))



effect=DressPivnick()
effect.affect()

