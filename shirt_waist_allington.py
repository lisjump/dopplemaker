# !/usr/bin/python
#
# shirt_waist_allington.py
# Inkscape extension-Effects-Sewing Patterns-Shirt Waist Allington
# Copyright (C) 2010,2011,2012 Susan Spencer,Steve Conklin <www.taumeta.org>

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

import sys,subprocess,math,inkex,gettext
sys.path.append('/usr/share/inkscape/extensions')
from simplestyle import *
from sewing_patterns import *

class ShirtWaistAllington(inkex.Effect):
    def __init__(self):

        inkex.Effect.__init__(self)

        self.OptionParser.add_option('--m_unit',action='store',type='string',dest='unit',default='Inches',help='Centimeters or Inches?')
        self.OptionParser.add_option('--m_front_waist_length',action='store',\
                                     type='float',dest='m_front_waist_length',default='15.0',help='Front Waist Length')
        self.OptionParser.add_option('--m_back_waist_length',action='store',\
                                     type='float',dest='m_back_waist_length',default='15.5',help='Back Waist Length')
        self.OptionParser.add_option('--m_neck_circumference',action='store',\
                                     type='float',dest='m_neck_circumference',default='13.5',help='Neck Circumference')
        self.OptionParser.add_option('--m_bust_circumference',action='store',\
                                     type='float',dest='m_bust_circumference',default='39.0',help='Bust Circumference')
        self.OptionParser.add_option('--m_waist_circumference',action='store',\
                                     type='float',dest='m_waist_circumference',default='25.0',help='Waist Circumference')
        self.OptionParser.add_option('--m_armscye_circumference',action='store',\
                                     type='float',dest='m_armscye_circumference',\
                                     default='15.0',help='Armscye circumference')
        self.OptionParser.add_option('--m_across_back',action='store',\
                                     type='float',dest='m_across_back',default='13.5',help='Across Back')
        self.OptionParser.add_option('--m_side',action='store',\
                                     type='float',dest='m_side',default='7.75',help='Side')
        self.OptionParser.add_option('--m_upper_front_height',action='store',\
                                     type='float',dest='m_upper_front_height',default='10.75',help='Upper Front Height')



    def effect(self):

        def printPoint(pnt):
            debug('  %s = %f, %f')%pnt.id,pnt.x,pnt.y

        INCH_to_PX=90.0 #inkscape uses 90 pixels per 1 inch
        CM_to_INCH=1/2.54
        CM_to_PX=CM_to_INCH*INCH_to_PX
        CM=CM_to_PX # CM - shorthand when using centimeters
        IN=INCH_to_PX # IN - shorthand when using inches

        #all measurements must be converted to px
        munit=self.options.unit
        if munit=='Centimeters':
            MEASUREMENT_CONVERSION=CM
        else:
            MEASUREMENT_CONVERSION=IN

        #convert measurements
        front_waist_length=self.options.m_front_waist_length * MEASUREMENT_CONVERSION
        neck_circumference=self.options.m_neck_circumference * MEASUREMENT_CONVERSION
        bust_circumference=self.options.m_bust_circumference * MEASUREMENT_CONVERSION
        waist_circumference=self.options.m_waist_circumference * MEASUREMENT_CONVERSION
        armscye_circumference=self.options.m_armscye_circumference * MEASUREMENT_CONVERSION
        across_back=self.options.m_across_back * MEASUREMENT_CONVERSION
        side=self.options.m_side * MEASUREMENT_CONVERSION
        upper_front_height=self.options.m_upper_front_height * MEASUREMENT_CONVERSION

        #constants
        ANGLE90=angleOfDegree(90)
        ANGLE180=angleOfDegree(180)
        SEAM_ALLOWANCE=(5/8.0)*IN
        BORDER=1*IN
        NOTE_HEIGHT=1*IN

        doc=self.document.getroot() # self.document is the canvas seen in Inkscape
        width_orig =inkex.unittouu(doc.get('width'))
        height_orig =inkex.unittouu(doc.get('height'))
        doc_width=4*BORDER+4*SEAM_ALLOWANCE + bust_circumference/2.0
        doc_height=2*BORDER+3*SEAM_ALLOWANCE+(upper_front_height+side) # add 15% to pattern height
        doc.set('width',str(doc_width))
        doc.set('height',str(doc_height))

        # create a bottom layer for all patterns in this pattern set
        pattern=addLayer(doc,'pattern')

        # create a base layer group for both front & back bodice patterns
        bodice=addLayer(pattern,'bodice')

        # create a layer group for the front bodice pattern A
        bodice_front=addLayer(bodice,'bodice_front')
        A=bodice_front

        # create a layer group for the back bodice pattern B
        bodice_back=addLayer(bodice,'bodice_back')
        B=bodice_back

        #pattern notes
        notes=[]
        notes.append('Set Inkscape Preferences/Steps/Outset to 56.25px (5/8 inch seam allowance)')
        notes.append('Create the Seam Allowances: Select the pattern paths & press Ctrl-)')
        notes.append('Remove Points & Gridlines: Press Ctrl-F and type "reference" in the Attribute field, click Find button, press Delete key.')
        notes.append('Print: Save as a PDF file. Open PDF with a PDF document viewer (Adobe, Evince, Okular). Print with the Print Preview option.')

        #pattern points
        b1=patternPointXY(B,'b1',0,0) #B
        b2=patternPoint(B,'b2',downPoint(b1, front_waist_length)) #A
        b3=patternPoint(B,'b3',upPoint(b2, side)) #C
        a1=patternPoint(A,'a1',leftPoint(b3, bust_circumference/2.0)) #D
        b4=patternPoint(B,'b4',leftPoint(b3,across_back/2.0)) #E
        b5=patternPoint(B,'b5',upPoint(b4,armscye_circumference/3.0)) #F
        b6=patternPoint(B,'b6',upPoint(b1, 0.5*IN)) #G
        b7=patternPoint(B,'b7',leftPoint(b6,1.5*IN)) #H
        b8=patternPoint(B,'b8',intersectLineAtLength(b5,b7, -0.5*IN)) #I
        a2=patternPoint(A,'a2',leftPoint(b4, armscye_circumference/4.0)) #J
        a3=patternPoint(A,'a3',midPoint(a2,b4)) #K
        a4=patternPoint(A,'a4',upPoint(a2, 2.5*IN)) #L
        a5=patternPoint(A,'a5',upPoint(b5,1.5*IN)) #M
        a6=patternPoint(A,'a6',leftPoint(a5,2*IN)) #N
        a7=patternPoint(A,'a7',leftPoint(a6,distance(b7,b8))) #R
        a8=patternPointXY(A,'a8',a7.x, b3.y-(upper_front_height-distance(b1,b7))) #P
        a9=patternPoint(A,'a9',downPoint(a8, neck_circumference/4.0)) #Q
        a10=patternPoint(A,'a10',upPoint(a9, 0.5*IN)) #O
        a11=patternPoint(A,'a11',leftPoint(a10, (neck_circumference/6.0)+0.25*IN )) #S
        b9=patternPoint(B,'b9',midPoint(a3,b4)) #T on back bodice B
        a12=patternPoint(A,'a12',b9) #T on front bodice A
        b10=patternPoint(B,'b10',downPoint(b9,side)) #U
        b11=patternPoint(B ,'b11',rightPoint(b10,1*IN)) #V
        a13=patternPoint(A,'a13',leftPoint(b10,1*IN)) #W
        a14=patternPoint(A,'a14',intersectLineAtLength(a11, a1, front_waist_length)) #X
        a15=patternPoint(A,'a15',downPoint(a8,distance(a8,a14))) #Y - new point at front waist
        b12=patternPoint(B,'b12',upPoint(b4,distance(b5, b4)/3.0)) #Z - new point at back armscye
        #temporary armscye curve from a3 to b12 to find top point of side seam
        length=distance(a3,b12)/3.0
        temp_b12_c1=rightPoint(a3,length) #don't create an svg controlpoint circle for this point
        temp_b12_c2=downPoint(b12,length) #or for this point
        #find top point of side seam with intersection of side and armscye curve, save to two points a16 and b13
        curve1=pointList(a3,temp_b12_c1,temp_b12_c2,b12)
        intersections=intersectLineCurve(b10,b9,curve1) #this line is directional from b10 to b9
        b13=patternPoint(B,'b13',intersections[0]) # AA on bodice back B -use 1st intersection found, in this case there's only one intersection
        a16=patternPoint(A,'a16',b13) #AA on bodice back A

        #front control points - path runs counterclockwise from front neck center a11
        #front neck control points from a8 to a11
        length=distance(a8,a11)/3.0
        a11.c2=controlPoint(A,'a11.c2',rightPoint(a11,1.5*length))
        a11.c1=controlPoint(A,'a11.c1',polarPoint(a8,length,angleOfLine(a8,a11.c2)))
        #front waist control points from a14 to a15
        length=distance(a14,a15)/3.0
        a15.c1=controlPoint(A,'a15.c1',polarPoint(a14,length,angleOfLine(a14,a11)+ANGLE90)) #control handle line is perpendicular to line a14-a11
        a15.c2=controlPoint(A,'a15.c2',leftPoint(a15,length))
        #front waist control points from a15 to a13
        length=distance(a15,a13)/3.0
        a13.c1=controlPoint(A,'a13.c1',rightPoint(a15,1.5*length))
        a13.c2=controlPoint(A,'a13.c2',polarPoint(a13,length,angleOfLine(a13,a13.c1))) #second control aimed at first control point
        #front side control points from a13 to a12
        length=distance(a13,a12)/3.0
        a12.c1=controlPoint(A,'a12.c1',upPoint(a13,length))
        a12.c2=controlPoint(A,'a12.c2',downPoint(a12,length))
        #front armscye control points from a16 to a3 to a4 to 16
        length1=distance(a16,a3)/3.0
        length2=distance(a3,a4)/3.0
        length3=distance(a4,a6)/3.0
        angle1=angleOfLine(a16,a3)
        angle2=ANGLE180
        angle3=(angle1+angle2)/2.0
        a3.c1=controlPoint(A,'a3.c1',polarPoint(a16,length1,angle1))
        a3.c2=controlPoint(A,'a3.c2',polarPoint(a3,length1,angle3-ANGLE180))
        a4.c1=controlPoint(A,'a4.c1',polarPoint(a3,length2,angle3))
        angle4=angleOfLine(a3,a6)
        angle5=angleOfLine(a4,a6)
        angle6=(angle4+angle5)/2.0
        a4.c2=controlPoint(A,'a4.c2',polarPoint(a4,1.5*length2,angle6-ANGLE180))
        a6.c1=controlPoint(A,'a6.c1',polarPoint(a4,length3,angle6))
        a6.c2=controlPoint(A,'a6.c2',polarPoint(a6,length3/2.0,angleOfLine(a8,a6)+ANGLE90))

        #back control points - path runs clockwise from back nape b1
        #back neck control points from b7 to b1
        length=distance(b7,b1)/3.0
        b1.c1=controlPoint(B,'b1.c1',downPoint(b7,length/2.0)) #short control point handle
        b1.c2=controlPoint(B,'b1.c2',leftPoint(b1,length*2)) #long control point handle
        #back side control points from b11 to b9
        length=distance(b11,b9)/3.0
        b9.c1=controlPoint(B,'b9.c1',upPoint(b11,length))
        b9.c2=controlPoint(B,'b9.c2',downPoint(b9,length))
        #back armscye points from b13 to b12 to b8
        length1=distance(b13,b12)/3.0
        length2=distance(b12,b8)/3.0
        angle1=angleOfLine(b13,b8)
        b12.c1=controlPoint(B,'b12.c1',polarPoint(b13,length1,angleOfLine(a3.c1,a16)))
        b12.c2=controlPoint(B,'b12.c2',polarPoint(b12,length1,angle1-ANGLE180))
        b8.c1=controlPoint(B,'b8.c1',polarPoint(b12,length2,angle1))
        b8.c2=controlPoint(B,'b8.c2',polarPoint(b8,length2/2.0,angleOfLine(b7,b8)-ANGLE90))

        # all points are defined,now create paths with them...
        # pattern marks,labels,grainlines,seamlines,cuttinglines,darts,etc.

        #bodice front A
        #grainline points
        aG1=patternPoint(A,'aG1',downPoint(a11,front_waist_length/3.0))
        aG2=patternPoint(A,'aG2',downPoint(aG1,front_waist_length/2.0))
        path_str=formatPath('M',aG1,'L',aG2)
        A_grainline=addPath(A,'A_grainline',path_str,'grainline')
        # gridline
        # this grid is helpful to troubleshoot during design phase
        path_str=formatPath('M',a1,'L',a3,'M',a4,'L',a2,'M',a8,'L',a15,'M',a11,'L',a10,'M',a7,'L',a5)
        A_gridline=addPath(A,'A_gridline',path_str,'gridline')
        #seamline & cuttingline
        path_str=formatPath('M',a11,'L',a14,'C',a15.c1,a15.c2,a15,'C',a13.c1,a13.c2,a13,'C',a12.c1,a12.c2,a12)
        path_str=path_str+formatPath('L',a16,'C',a3.c1,a3.c2,a3,'C',a4.c1,a4.c2,a4,'C',a6.c1,a6.c2,a6,'L',a8,'C',a11.c1,a11.c2,a11)
        A_seamline=addPath(A,'A_seamline',path_str,'seamline')
        A_cuttingline=addPath(A,'A_cuttingline',path_str,'cuttingline')

        #bodice back B
        #grainline points
        bG1=patternPoint(B,'bG1',downPoint(b7,front_waist_length/3.0))
        bG2=patternPoint(B,'bG2',downPoint(bG1,front_waist_length/2.0))
        path_str=formatPath('M',bG1,'L',bG2)
        B_grainline=addPath(B,'B_grainline',path_str,'grainline')
        # gridline
        # this grid is helpful to troubleshoot during design phase
        path_str=formatPath('M',a5,'L',b4,'M',b3,'L',b9,'M',b9,'L',b10,'M',b7,'L',b6,'L',b1,'M',b11,'L',b10)
        B_gridline=addPath(B,'B_gridline',path_str,'gridline')
        #seamline & cuttingline
        path_str=formatPath('M',b1,'L',b2,'L',b11,'C',b9.c1,b9.c2,b9,'L',b13,'C',b12.c1,b12.c2,b12,'C',b8.c1,b8.c2,b8,'L',b7,'C',b1.c1,b1.c2,b1)
        B_seamline=addPath(B,'B_seamline',path_str,'seamline')
        B_cuttingline=addPath(B,'B_cuttingline',path_str,'cuttingline')

        #layout patterns on document
        #layout bodice front A
        adx=BORDER+SEAM_ALLOWANCE-a14.x # left value - a14 is the leftmost point on bodice front,
        ady=NOTE_HEIGHT+BORDER+SEAM_ALLOWANCE-a8.y # a8 is the topmost point on bodice front
        bodice_front.set('transform','translate('+str(adx)+' '+str(ady)+')')
        #layout bodice front B
        bdx=adx+a12.x+BORDER+2*SEAM_ALLOWANCE-b9.x # left value - b9 is the leftmost point on bodice back
        bdy=ady+a13.y-b11.y # move B down even with a13
        bodice_back.set('transform','translate('+str(bdx)+' '+str(bdy)+')')

        #resize document to fit pattern piece layout
        doc_width=abs(b1.x-a14.x)+4*SEAM_ALLOWANCE+3*BORDER
        doc.set('width',str(doc_width))

        #Place notes on document after pattern pieces are created so that notes are centered
        x=doc_width/2.0
        y=BORDER/2.0 #start notes half-way through border
        i=0
        for item in notes:
            addText(bodice,'note'+str(i),x,y,item,fontsize='28',textalign='center',textanchor='middle',reference='false')
            y=y+0.33*IN


effect=ShirtWaistAllington()
effect.affect()

