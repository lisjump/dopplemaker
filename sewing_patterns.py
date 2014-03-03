#!/usr/bin/python
#
# sewing_patterns.py
# Inkscape extension-Effects-Sewing Patterns
# Originally written by Susan Spencer,Steve Conklin <www.taumeta.org>
# Updated and modified by Lisabeth Lueninghoener <lazydayartifacts.com> <lazydayartifacts.blogspot.com>
#
# This program is free software:you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation,either version 2 of the License,or
# (at your option) any later version. Attribution must be given in
# all derived works.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not,see<http://www.gnu.org/licenses/>

import sys, math, inkex, gettext
sys.path.append('/usr/share/inkscape/extensions')
from simplestyle import *
from math import *

def debug(errmsg):
    inkex.errormsg(gettext.gettext(errmsg))

#---Classes---
class Point():
    '''Python object class to create variables that represent a named Cartesian point.
    Accepts id, x, y. Returns object with .id,.x,.y attributes.
    Example: a5=Point('a5',10.0,15.32) returns variable a5 where a5.id='a5', a5.x=10.0, a5.y=15.32xt
    If called with no parameters the defaults are id='', x=0, y=0
    The python object's id attribute enables it to be represented on the canvas as an svg object with the same id.
    '''
    def __init__(self,id='',x=0.0,y=0.0): #if no parameters are passed in then the default values id='',x=0, y=0 are used
        self.id=id
        self.x=x
        self.y=y

class PatternPiece():
    def __init__(self, id, parent): 
      self.id = id
      self.layer = addLayer(parent, id)
      self.draft = addLayer(self.layer, 'draft')
      self.pts = {}        # 'id': pt 
      self.cpts = {}       # pt: {1:cpt, 2:cpt}
      self.seam = []       # an array of points
      self.darts = {}      # 'id': (leg1, leg2, top, center) all are points
      self.guides = {}     # 'id': (pt1, pt2) are all points
      self.grainline = []  # an array with two points
      self.layerVisible(True, False)
    
    # Points
    def pointXY(self, id, x, y):
      self.pts[id] = patternPointXY(self.draft, id, x, y)
      return self.pts[id]

    def point(self, id, pt):
      return self.pointXY(id, pt.x, pt.y)

    def cpointXY(self, parent, id, x, y):
      #control points go in clockwise order
      if parent not in self.cpts:
        self.cpts[parent] = {}
      self.cpts[parent][id] = controlPointXY(self.draft, parent.id + str(id), x, y)
      return self.cpts[parent][id]

    def cpoint(self, parent, id, pt):
      #control points go in clockwise order
      return self.cpointXY(parent, id, pt.x, pt.y)
      
    def deleteCpt(self, parent, id):
      self.cpts[parent].pop(id, None)
    
    # Check for inclusion
    def pointInPiece(self, point):
      if (point.id not in self.pts) or (point != self.pts[point.id]):
        return False
      else:
        return True
        
    def pointHasCpt(self, point, cptid):
      if (point in self.cpts) and (cptid in self.cpts[point]):
        return True
      else:
        return False
        
    # Declaring and Changing Pattern Objects
    def declareGrainline(self, pt1, pt2):
      self.grainline = [self.point('Grain1', pt1), self.point('Grain2', pt2)]
      
    def declareSeam(self, *pts):
      self.seam = [pt for pt in pts]
    
    def declareSeamFromIds(self, *ids):
      self.seam = [self.pts[id] for id in ids]
     
    def insertPointInSeam(self, pt, ptbefore, ptafter):
      if (ptbefore not in self.seam) or (ptafter not in self.seam):
        return
        
      if self.seam.index(ptbefore) == self.seam.index(ptafter) - 1:
        self.seam.insert(self.seam.index(ptafter), pt)
      elif self.seam.index(ptbefore) == self.seam.index(ptafter) + 1:
        self.seam.insert(self.seam.index(ptbefore), pt)
      elif (self.seam.index(ptbefore) == 0) and (self.seam.index(ptafter) == len(self.seam)-2):
        self.seam.insert(len(self.seam)-1, pt)
      elif (self.seam.index(ptbefore) == len(self.seam)-2) and (self.seam.index(ptafter) == 0):
        self.seam.insert(len(self.seam)-1, pt)
      else:
        return
      
      if pt not in self.pts:
        self.pts[pt.id] = pt
    
    def insertNewPointInSeam(self, id, pt, ptbefore, ptafter):
      self.point(id, pt)
      self.insertPointInSeam(pt, ptbefore, ptafter)
    
    def addDart(self, leg1, leg2, top, mid):
      id = leg1.id + top.id + leg2.id
      backwardsid = leg2.id + top.id + leg1.id
      if backwardsid in self.darts:
        id = backwardsid
      self.darts[id] = ([leg1, leg2, top, mid])
      return self.darts[id]
    
    def addGuide(self, pt1, pt2):
      id = pt1.id + pt2.id
      backwardsid = pt2.id + pt1.id
      if backwardsid in self.guides:
        id = backwardsid
      self.guides[id] = ([pt1, pt2])
      return self.guides[id]
    
    def smoothPoint(self, pt, percent1, percent2 = None):
    #picks control points for a point to smooth out the seam
    #percent1 is the decimal percentage from the point to the point prior on the seam
    #percent2 is the decimal percentage from the point to the point following on the seam
    
      if percent2 == None:
        percent2 = percent1
      
      if pt not in self.seam:
        return False
        
      index = self.seam.index(pt)
      if index == 0:
        pt1 = self.seam[len(self.seam)-2]
      else:
        pt1 = self.seam[index - 1]
      
      pt2 = self.seam[index + 1]
      
      pt3 = intersectLines(pt1, pt2, pt, leftPoint(pt, 2))
      
      changex = pt3.x - pt.x
      
      new1 = leftPoint(pt1, changex)
      new2 = leftPoint(pt2, changex)
      
      if highest([new1, new2, pt]) == pt:
        if  highest([new1, new2]) == new1:
          cp1 = intersectLineAtLength(pt, new2, -distance(pt, pt1)*percent1)
          cp2 = intersectLineAtLength(pt, new2, distance(pt, pt2)*percent2)
        else:
          cp1 = intersectLineAtLength(pt, new1, distance(pt, pt1)*percent1)
          cp2 = intersectLineAtLength(pt, new1, -distance(pt, pt2)*percent2)
      elif lowest([new1, new2, pt]) == pt:
        if  lowest([new1, new2]) == new1:
          cp1 = intersectLineAtLength(pt, new2, -distance(pt, pt1)*percent1)
          cp2 = intersectLineAtLength(pt, new2, distance(pt, pt2)*percent2)
        else:
          cp1 = intersectLineAtLength(pt, new1, distance(pt, pt1)*percent1)
          cp2 = intersectLineAtLength(pt, new1, -distance(pt, pt2)*percent2)
      else:
        cp1 = intersectLineAtLength(pt, new1, distance(pt, pt1)*percent1)
        cp2 = intersectLineAtLength(pt, new2, distance(pt, pt2)*percent2)
        
      self.cpoint(pt, 1, cp1)
      self.cpoint(pt, 2, cp2)
    
    # Drawing Pattern Objects
    def drawDart(self, dart):
      path_str=formatPath('M', dart[0], 'L', dart[2], 'L', dart[1])
      addPath(self.layer, self.id + 'dart', path_str, 'dartline')
      path_str=formatPath('M', dart[2], 'L', dart[3])
      addPath(self.layer, self.id + 'dartcenter', path_str, 'seamline')
      
    def drawGuide(self, guide):
      path_str=formatPath('M', guide[0], 'L', guide[1])
      addPath(self.layer, self.id + 'guide', path_str, 'dartline')
      
    def drawSeam(self):
      #accepts a list of points in clockwise order
      path_str = formatPath('M', self.seam[0])
      
      # Draw path and find control points
      for i in range(1, len(self.seam)):
        if self.pointHasCpt(self.seam[i-1], 2): 
          if self.pointHasCpt(self.seam[i], 1):
            path_str = path_str + formatPath('C', self.cpts[self.seam[i-1]][2], self.cpts[self.seam[i]][1], self.seam[i])
          else:
            path_str = path_str + formatPath('C', self.cpts[self.seam[i-1]][2], self.seam[i], self.seam[i])
        elif self.pointHasCpt(self.seam[i], 1):
          path_str = path_str + formatPath('C', self.seam[i-1], self.cpts[self.seam[i]][1], self.seam[i])
        else:
          path_str = path_str + formatPath('L', self.seam[i])
      
      addPath(self.layer, self.id + 'seam', path_str, 'seamline')
      
      # draw darts
      for dart in self.darts.keys():
        self.drawDart(self.darts[dart])
      
      # draw guides
      for guide in self.guides.keys():
        self.drawGuide(self.guides[guide])
      
      # draw grainline
      path_str = formatPath('M', self.grainline[0], 'L', self.grainline[1])
      addPath(self.layer, self.id + 'grainline', path_str, 'grainline')

    def drawPoints(self, pointArray = False):
      if not pointArray:
        pointArray = []
        for id in self.pts:
          pointArray.append(self.pts[id])
      
      for pt in pointArray:
        drawPoint(self.draft, pt.id, pt.x, pt.y)
          
    # Moving Pattern Piece 
    def move(self, changeX, changeY):
      for id in self.pts:
        updatePoint(self.pts[id], Point('', self.pts[id].x + changeX, self.pts[id].y + changeY))
      for parentid in self.cpts:
        for id in self.cpts[parentid]:
          updatePoint(self.cpts[parentid][id], Point('', self.cpts[parentid][id].x + changeX, self.cpts[parentid][id].y + changeY))
      
    def movePointToXY(self, point, x, y):
      self.move(x - point.x, y - point.y)

    def movePointToPoint(self, point, point2):
      self.move(point2.x - point.x, point2.y - point.y)

    def rotate(self, pivot, radians):
      ptset = set()
      for pt in self.pts:
        ptset.add(self.pts[pt])
      for pt in self.cpts:
        for cpt in self.cpts[pt]:
          ptset.add(self.cpts[pt][cpt])
      rotatePtArray(pivot, radians, ptset)
    
    def rotatePtToPt(self, pivot, point, point2):
      self.rotate(pivot, -angleOfVector(point, pivot, point2))

    # Manipulating Pattern Piece
    def moveDart(self, oldDartArray, newSize, newDartArray, pivot = None):
      # accepts dartArray [leg1, leg2, top, center]to be closed (using the 'id' in the array
      # the new size of the OLD dart, and newDartArray
      # the new dart legs and top can be existing or not, the center point must exist
      # pivot is a point defaulted to either 5/8 above the current dart top or, 
      # if newDart exists, the intersection of the two darts
      
      # Check to make sure the necessaries exist
      if (newDartArray[3] not in self.pts.keys()) or (self.pts[newDartArray[3]] not in self.seam):
        return
      oldid  = oldDartArray[0] + oldDartArray[2] + oldDartArray[1] 
      if oldid not in self.darts.keys():
        oldid  = oldDartArray[1] + oldDartArray[2] + oldDartArray[0] 
      if oldid not in self.darts.keys():
        return
      oldDart = self.darts[oldid]
      
      # Check to see if the new dart already exists.  If not, create it.
      newid  = newDartArray[0] + newDartArray[2] + newDartArray[1] 
      newidrev  = newDartArray[1] + newDartArray[2] + newDartArray[0] 
      if newid in self.darts.keys():
        newDart = self.darts[newid]
      elif newidrev in self.darts.keys():
        newDart = self.darts[newidrev]
      else:
        if newDartArray[0] not in self.pts.keys():
          self.pointXY(newDartArray[0], 0, 0)
        if newDartArray[1] not in self.pts.keys():
          self.pointXY(newDartArray[1], 0, 0)
        if newDartArray[2] not in self.pts.keys():
          self.pointXY(newDartArray[2], 0, 0)
        newDart = self.addDart(self.pts[newDartArray[0]], self.pts[newDartArray[1]], self.pts[newDartArray[2]], self.pts[newDartArray[3]])
        if (newDart[3] in self.cpts) and (1 in self.cpts[newDart[3]].keys()):
          self.cpoint(newDart[0], 1, self.cpts[newDart[3]][1])
          del self.cpts[newDart[3]][1]
        if (newDart[3] in self.cpts) and (2 in self.cpts[newDart[3]].keys()):
          self.cpoint(newDart[1], 2, self.cpts[newDart[3]][2])
          del self.cpts[newDart[3]][2]
        self.seam.insert(self.seam.index(newDart[3]), newDart[0])
        self.seam.insert(self.seam.index(newDart[3]) + 1, newDart[1])
      
      # Add c-pts and plit the seam into two halves on either side of the dart centers
      seamandcpts = []
      for i in range(1, len(self.seam)):
        if self.pointHasCpt(self.seam[i-1], 2): 
          seamandcpts.append(self.cpts[self.seam[i-1]][2])
        if self.pointHasCpt(self.seam[i], 1):
          seamandcpts.append(self.cpts[self.seam[i]][1]) 
        seamandcpts.append(self.seam[i])

      if seamandcpts[0] == seamandcpts[len(seamandcpts) -1]:
        seamandcpts.pop
        
      seamhalf1a = []
      seamhalf1b = []
      seamhalf2 = []
      half2 = False
      half1b = False
      for pt in seamandcpts:
        if pt in [oldDart[3], newDart[3]]:
          if not half2:
            seamhalf1a.append(pt)
            seamhalf2.append(pt)
            half2 = True
          elif not half1b:
            seamhalf2.append(pt)
            seamhalf1b.append(pt)
            half1b = True
        else:
          if half1b:
            seamhalf1b.append(pt)
          elif half2:
            seamhalf2.append(pt)
          else:
            seamhalf1a.append(pt)
        
      seamhalf1 = seamhalf1b + seamhalf1a
          
      # determine the half seam with the smaller angle and move it
      if (oldDart[0] in seamhalf1) and (pointInAngle(oldDart[0], oldDart[3], pivot, newDart[3])):
        movepoints = seamhalf1
      elif (oldDart[1] in seamhalf1) and (pointInAngle(oldDart[1], oldDart[3], pivot, newDart[3])):
        movepoints = seamhalf1
      else:
        movepoints = seamhalf2

      if movepoints[0] == oldDart[3]:
        moveDart(movepoints, pivot, oldDart, newSize, newDart)
      elif movepoints[0] == newDart[3]:
        movepoints.reverse()
        moveDart(movepoints, pivot, oldDart, newSize, newDart)
      
      self.drawPoints(movepoints)
      self.drawPoints(newDart)
    
    # Combining and switching pattern pieces
    def addPieces(self, *tuples):
      # adds all of the pts and cpts from one or more pattern pieces to the current piece
      # tuples are id, pattern piece pairs 
      # the id is attached to the front of the point ids, so that there are not duplicate point names
      
      pieces = {}
      for tuple in tuples:
        pieces[tuple[0]] = tuple[1]
        
      for id in pieces:
        for ptid in pieces[id].pts:
          self.point(id + ptid, pieces[id].pts[ptid])
          if pieces[id].pointHasCpt(pieces[id].pts[ptid], 1):
            self.cpoint(self.pts[id + ptid], 1, pieces[id].cpts[pieces[id].pts[ptid]][1])
          if pieces[id].pointHasCpt(pieces[id].pts[ptid], 2):
            self.cpoint(self.pts[id + ptid], 2, pieces[id].cpts[pieces[id].pts[ptid]][2])

    # Display
    def layerVisible(self, main = True, draft = False):
      layerVisible(self.layer, main)
      layerVisible(self.draft, draft)
    
    # Measurement
    def lengthOfCurve(self, ptArray):
      # accepts a clockwise array of points and 
      # returns the length of the curve they form with their control points
      length = 0
      for i in range(1, len(ptArray)):
        if self.pointHasCpt(ptArray[i-1], 2): 
          if self.pointHasCpt(ptArray[i], 1):
            length = length + lengthOfCurve(ptArray[i-1], self.cpts[ptArray[i-1]][2], self.cpts[ptArray[i]][1], ptArray[i])
          else:
            length = length + lengthOfCurve(ptArray[i-1], self.cpts[ptArray[i-1]][2], ptArray[i], ptArray[i])
        elif self.pointHasCpt(ptArray[i], 1):
          length = length + lengthOfCurve(ptArray[i-1], ptArray[i-1], self.cpts[ptArray[i]][1], ptArray[i])
        else:
          length = length + distance(ptArray[i-1], ptArray[i])
      return length

#---Points---
def patternPointXY(parent,id,x,y):
    '''Accepts parent,id,x,y. Returns object of class Point. Calls addPoint() & addText() to create a pattern point on canvas.'''
    # create python variable
    pnt=Point(id,x,y)
    # create svg circle red 5px radius
    addCircle(parent,id,x,y,radius=5,fill='red',stroke='red',stroke_width='1',reference='true')
    #draw label 8px right and 8px above circle
    addText(parent,id+'_text',x+8,y-8,id,fontsize='30',textalign='left',textanchor='left',reference='true') #the id is used for two things here: the text object's id and the text object's content.
    return pnt # return python variable for use in remainder of pattern

def patternPoint(parent,id,pnt):
    """Wrapper for patternPointXY. Accepts a Point object instead of X & Y values."""
    return patternPointXY(parent,id,pnt.x,pnt.y)

def controlPointXY(parent,id,x,y):
    '''Accepts parent,id,x,y. Returns object of class Point. Calls addPoint() & addText() to create a pattern point with label on canvas.'''
    # create python variable
    pnt=Point(id,x,y)
    # create unfilled grey circle 5px radius
    addCircle(parent,id,x,y,radius=5,fill='none',stroke='gray',stroke_width='1',reference='true')
    #draw label 8px right and 8px above circle
    addText(parent,id+'_text',x+8,y-8,id,fontsize='30',textalign='left',textanchor='left',reference='true') #the id is used twice: the text object id and the text object content.
    return pnt # return python variable for use in remainder of pattern

def controlPoint(parent,id,pnt):
    """Wrapper for controlPointXY. Accepts a Point object instead of X & Y values."""
    return controlPointXY(parent,id,pnt.x,pnt.y)

def drawPoint(parent, id, x, y):
    # create svg circle red 5px radius
    addCircle(parent,id,x,y,radius=5,fill='red',stroke='red',stroke_width='1',reference='true')
    #draw label 8px right and 8px above circle
    addText(parent,id+'_text',x+8,y-8,id,fontsize='30',textalign='left',textanchor='left',reference='true') #the id is used for two things here: the text object's id and the text object's content.    
    
#---pattern manipulation---
def moveDart(path, pivot, old_dart, old_dart_new_size, new_dart):
        """
        accepts an array for points from center point of old dart up to and including new_dart_center 
        dart pivot, the four points of the old dart (leg1, leg2, top, middle)
        the new size for the old dart, and 
        the four points of the new dart (three new points must be created, but not placed)
        
        updates the path, updates darts, and updates dart centers
        """
        originaldartcenter = Point("", path[-1].x, path[-1].y)
        dart_center_outset = distance(midPoint(old_dart[0], old_dart[1]), old_dart[3])
        parity = 1
        # fix this based on which direction the dart closes in
        slashAngle = angleOfVector(old_dart[3], pivot, new_dart[3]) % (2*math.pi)
        if (slashAngle < 0) or (slashAngle > math.pi) : 
          parity = -1
        old_angle = angleOfVector(old_dart[0], pivot, old_dart[1])
        new_angle = math.acos((distance(old_dart[0], old_dart[1])**2 - old_dart_new_size**2)/(2*distance(pivot, old_dart[0])*distance(pivot, old_dart[1])) + math.cos(old_angle))
        rotatePtArray(pivot, parity*(old_angle-new_angle), path)
        updatePoint(old_dart[3], intersectLineAtLength(midPoint(old_dart[0], old_dart[1]), old_dart[2], -dart_center_outset))
        
        #fix this based on which pointed is included in the path
        if new_dart[0] in path:
          updatePoint(new_dart[1], originaldartcenter)
          updatePoint(new_dart[0], path[-1])
        else:
          updatePoint(new_dart[0], originaldartcenter)
          updatePoint(new_dart[1], path[-1])
        updatePoint(new_dart[2], intersectLineAtLength(pivot, midPoint(new_dart[0], new_dart[1]), distance(pivot, old_dart[2])))
        updatePoint(new_dart[3], intersectLineAtLength(midPoint(new_dart[0], new_dart[1]), new_dart[2], -dart_center_outset))
        return

def rotatePtArray(pivot, angle, path):
        """
        Accepts pivot point, angle of rotation, and the points to be rotated.
        Accepts positive(clockwise) & negative (counter clockwise) angles .
        """
        if (angle != 0.0):
            for pnt in path:
                length = distance(pivot, pnt)
                rotated_pnt = polarPoint(pivot, length, angleOfLine(pivot, pnt) + angle) # if angle > 0 spread clockwise. if angle < 0 spread counterclockwise
                updatePoint(pnt, rotated_pnt)
        return
        
def writeSomething(parent, text, x=0, y=0):
  addText(parent, 'note', x, y, str(text), fontsize='40', textalign='left', textanchor='left', reference='true')

#---tests for position---
def isRight(pnt1, pnt2):
    '''returns 1 if pnt2 is to the right of pnt1'''
    right=0
    if pnt2.x>pnt1.x:
        right=1
    return right

def isLeft(pnt1, pnt2):
    '''returns 1 if pnt2 is to the left of pnt1'''
    left=0
    if pnt2.x<pnt1.x:
        left=1
    return left

def isAbove(pnt1, pnt2):
    '''returns 1 if pnt2 is above pnt1'''
    up=0
    if pnt2.y<pnt1.y:
        up=1
    return up

def isBelow(pnt1, pnt2):
    '''returns 1 if pnt2 is below pnt1'''
    down=0
    if pnt2.y>pnt1.y:
        down=1
    return down

def lowest(pnts):
    """Accepts array pnts[]. Returns lowest point in array."""
    low = pnts[0]
    for item in pnts:
        if isBelow(low,item): #if item is below current low
            low = item
    return low

def highest(pnts):
    """Accepts array pnts[]. Returns highest point in array."""
    high = pnts[0]
    for item in pnts:
        if isAbove(high,item): #if item is above current high
            high = item
    return high

def leftmost(pnts):
    """Accepts array pnts[]. Returns leftmost point in array."""
    left = pnts[0]
    for item in pnts:
        if isLeft(left,item):
            left = item
    return left

def rightmost(pnts):
    """Accepts array pnts[]. Returns rightmost point in array."""
    right = pnts[0]
    for item in pnts:
        if isRight(right,item):
            right = item
    return right

def sameSideOfLine(p1, p2, l1, l2):
  #returns true if p1 and p2 are on the same side of line l1 l2
  v1 = (l2.x - l1.x)*(p1.y - l1.y) - (l2.y - l1.y)*(p1.x - l1.x)
  v2 = (l2.x - l1.x)*(p2.y - l1.y) - (l2.y - l1.y)*(p2.x - l1.x)
  
  if (v1 * v2 > 0):
    return True
  else:
    return False
    
def pointInAngle(pt, leg1, vertex, leg2):
  # returns true if the point is in the acute or obtuse angle (<180deg)
  mid = midPoint(leg1, leg2)
  if sameSideOfLine(pt, mid, leg1, vertex) and sameSideOfLine(pt, mid, leg2, vertex):
    return True
  else:
    return False

#---functions to calculate points. These functions do not create SVG objects---
def updatePoint(p1,p2):
    '''Accepts p1 and p2 of class Point. Updates p1 with x & y values from p2'''
    x,y=p2.x,p2.y
    p1.x,p1.y=x,y
    return

def rightPoint(p1,n):
    '''Accepts point p1 and float n. Returns p2 to the right of p1 at (p1.x+n, p1.y)'''
    id=""
    p2=Point(id,p1.x+n,p1.y)
    return p2

def leftPoint(p1,n):
    '''Accepts point p1 and float n. Returns p2 to the left of p1 at (p1.x-n, p1.y)'''
    id=""
    p2=Point(id,p1.x-n,p1.y)
    return p2

def upPoint(p1,n):
    '''Accepts point p1 and float n. Returns p2 above p1 at (p1.x, p1.y-n)'''
    id=""
    p2=Point(id,p1.x,p1.y-n)
    return p2

def downPoint(p1,n):
    '''Accepts point p1 and float n. Returns p2 below p1 at (p1.x, p1.y+n)'''
    id=""
    p2=Point(id,p1.x,p1.y+n)
    return p2

def symmetricPoint(p1,p2,type='vertical'):
    """
    Accepts p1 and p2 of class Point, and optional type is either 'vertical' or 'horizontal with default 'vertical'.
    Returns p3 of class Point as "mirror image" of p1 relative to p2
    If type=='vertical': pnt is on opposite side of vertical line x=p2.x from p1
    If type=='horizontal': pnt is on opposite side of horizontal line y=p2.y from p1
    """
    p3=Point()
    dx=p2.x-p1.x
    dy=p2.y-p1.y
    if (type=='vertical'):
        p3.x=p2.x+dx
        p3.y=p1.y
    elif (type=='horizontal'):
        p3.x=p1.x
        p3.y=p2.y+dy
    return p3

def polarPoint(p1,length,angle):
    '''
    Adapted from http://www.teacherschoice.com.au/maths_library/coordinates/polar_-_rectangular_conversion.htm
    Accepts p1 as type Point,length as float,angle as float. angle is in radians
    Returns p2 as type Point, calculated at length and angle from p1,
    Angles start at position 3:00 and move clockwise due to y increasing downwards on Cairo Canvas
    '''
    id=''
    r=length
    x=p1.x+(r*math.cos(angle))
    y=p1.y+(r*math.sin(angle))
    p2=Point(id,x,y)
    return p2

def midPoint(p1,p2,n=0.5):
    '''Accepts points p1 & p2, and n where 0<n<1. Returns point p3 as midpoint b/w p1 & p2'''
    p3=Point('',(p1.x+p2.x)*n,(p1.y+p2.y)*n)
    return p3

#---measurements
def distance(p1,p2):
    '''Accepts two points p1 & p2. Returns the distance between p1 & p2.'''
    return ( ((p2.x-p1.x)**2)+((p2.y-p1.y)**2) )**0.5

def lengthOfCurve(P0,C1,C2,P1,t=10):
  length = 0
  ptArray = interpolateCurve(P0,C1,C2,P1,t)
  
  for i in range(1, len(ptArray)):
    length = length + distance(ptArray[i-1], ptArray[i])

  return length

def angleOfLine(p1,p2):
    """ Accepts points p1 & p2. Returns the angle of the vector between them. Uses atan2."""
    return math.atan2(p2.y-p1.y,p2.x-p1.x)

def angleOfVector(p1,v,p2):
    '''Accepts three points o1, v, and p2. Returns radians of the angle formed between the three points.'''
    return angleOfLine(v,p1)-angleOfLine(v,p2)

def slopeOfLine(p1,p2):
    """ Accepts two point objects and returns the slope """
    if ((p2.x-p1.x) <> 0):
        m=(p2.y-p1.y)/(p2.x-p1.x)
    else:
        #TODO: better error handling here
        debug('Vertical Line in slopeOfLine')
        m=None
    return m

#---intersections
def intersectLineAtLength(p1,p2,length,rotation=0):
    """
    Accepts p1 and p2 of class Point, distance, and an optional rotation angle
    Returns p3 of class Point on the line at length measured from p1 towards p2
    If length is negative, will return p3 at length measured from p1 in opposite direction from p2
    The point is optionally rotated about the first point by the rotation angle in degrees
    """
    lineangle=angleOfLine(p1,p2)
    angle=lineangle+(rotation*(math.pi/180))
    x=(length*math.cos(angle))+p1.x
    y=(length*math.sin(angle))+p1.y
    p3=Point("",x,y)
    return p3

def intersectLines(p1,p2,p3,p4):
    """
    Find intersection between two lines. Accepts p1,p2,p3,p4 as class Point. Returns p5 as class Point
    Intersection does not have to be within the supplied line segments
    """
    x,y=0.0,0.0
    if (p1.x==p2.x): #if 1st line vertical,use slope of 2nd line
        x=p1.x
        m2=slopeOfLine(p3,p4)
        b2=p3.y-m2*p3.x
        y=m2*x+b2
    elif (p3.x==p4.x): #if 2nd line vertical, use slope of 1st line
        x=p3.x
        m1=slopeOfLine(p1,p2)
        b1=p1.y-m1*p1.x
        y=m1*x+b1
    else: #otherwise use ratio of difference between points
        m1=(p2.y-p1.y)/(p2.x-p1.x)
        m2=(p4.y-p3.y)/(p4.x-p3.x)
        b1=p1.y-m1*p1.x
        b2=p3.y-m2*p3.x
        #if (abs(b1-b2)<0.01) and (m1==m2):
            #x=p1.x
        #else:
            #x=(b2-b1)/(m1-m2)
        if (m1==m2):
            #TODO: better error handling here
            debug('***** Parallel lines in intersectLines *****')
        else:
            x=(b2-b1)/(m1-m2)
            y=(m1*x)+b1 # arbitrary choice,could have used m2 & b2
    p5=Point("",x,y)
    return p5

def intersectCircles(C1,r1,C2,r2):
    """
    Accepts C1,r1,C2,r2 where C1 & C2 are center points of each circle, and r1 & r2 are the radius of each circle.
    Returns an array of points of intersection.
    """
    x0,y0=C1.x,C1.y
    x1,y1=C2.x,C2.y
    d=distance(C1,C2) # distance b/w circle centers
    dx,dy=(x1-x0),(y1-y0) # negate y b/c canvas increases top to bottom
    pnts=[]
    if (d==0):
        #intersections=0
        #TODO: better error handling here
        debug('center of both circles are the same in intersectCircles()')
#         debug('C1 = (' + str(C1.x) + ', ' +  str(C1.y) '), radius1 = ' + str(r1))
#         debug('C2 = (' + C2.x + ', ' +  C2.y '), radius2 = ' + r2)
        return
    elif (d<abs(r1-r2)):
        #intersections=0
        #TODO: better error handling here
        debug('one circle is within the other in intersectCircles()')
#         debug('d = ' + d)
#         debug('r1 - r2 = ' + str(r1-r2))
#         debug('d< abs(r1 - r2) ?', (d<abs(r1-r2)))
#         debug('C1 =', C1.x, C1.y, 'radius1 =', r1)
#         debug('C2 =', C2.x, C2.y, 'radius1 =',r2)
        return
    elif (d>(r1+r2)):
        #intersections=0
        #TODO: better error handling here
        debug('circles do not intersect in intersectCircles()')
#         debug('d =', d)
#         debug('r1 + r2 =',(r1+r2))
#         debug('d > abs(r1 + r2) ?', (d>abs(r1+r2)))
#         debug('C1 =', C1.x, C1.y, 'radius1 =', r1)
#         debug('C2 =', C2.x, C2.y, 'radius1 =',r2)
        # TODO:possible kluge -check if this is acceptable using a small margin of error between r1 & r2 (0.5*CM)?:
        #r2=d-r1
        return
    else:
        #intersections=2 or intersections=1
        a=((r1*r1)-(r2*r2)+(d*d))/(2.0*d)
        x2=x0+(dx*a/d)
        y2=y0+(dy*a/d)
        h=math.sqrt((r1*r1)-(a*a))
        rx=-dy*(h/d)
        ry=dx*(h/d)
        X1=x2+rx
        Y1=y2+ry
        X2=x2-rx
        Y2=y2-ry
        pnts.append(Point("",X1,Y1))
        pnts.append(Point("",X2,Y2))
        return pnts

def intersectCircleAtX(C,r,x):
    """
    Finds points on circle where p.x=x
    Accepts C as center point of the circle, r as radius point, and float x.
    Returns an array of points of intersection
    """
    id=''
    pnts=[]
    if abs(x-C.x)>r:
        #TODO: better error handling here
        debug('x is outside radius of circle in intersections.intersectCircleAtX()')
        return
    else:
        translated_x=x-C.x # center of translated circle is (0,0) as translated_x is the difference b/w C.x & x
        translated_y1=abs(math.sqrt(r**2-translated_x**2))
        translated_y2=-(translated_y1)
        y1=translated_y1+C.y # translate back to C.y
        y2=translated_y2+C.y # translate back to C.y
        pnts.append(Point(id,x,y1))
        pnts.append(Point(id,x,y2))
        return pnts

def intersectCircleAtY(C,r,y):
    """
    Finds points one or two points on circle where P.y=y
    Accepts C of class Point or Point as circle center, r of type float as radius, and y of type float)
    Returns an array P containg intersections of class Point
    Based on paulbourke.net/geometry/sphereline/sphere_line_intersection.py,written in Python 3.2 by Campbell Barton
    """
    pnts=[]
    if abs(y-C.y)>r:
        #TODO: better error handling here
        debug('y is outside radius in intersectCircleAtY() -- no intersection')
        return
    else:
        translated_y=y-C.y
        translated_x1=abs(math.sqrt(r**2-translated_y**2))
        translated_x2=-translated_x1
        x1=translated_x1+C.x
        x2=translated_x2+C.x
        pnts.append(Point('',x1,y))
        pnts.append(Point('',x2,y))
        return pnts

def intersectLineCircle_old(C,r,P1,P2):
    """
    Finds intersection of a line segment and a circle.
    Accepts circle center point object C,radius r,and two line point objects P1 & P2
    Returns an object P with number of intersection points,and up to two coordinate pairs as P.intersections,P.p1,P.p2
    Based on paulbourke.net/geometry/sphereline/sphere_line_intersection.py,written in Python 3.2 by Campbell Barton
    """
    p1,p2=Point(),Point()
    pnts=[]
    intersections=0

    if P1.x==P2.x: #vertical line
        if abs(P1.x-C.x)>r:
            #TODO: better error handling here
            debug('Circle does not intersect vertical line P1:',P1.name,P1.x,P1.y,', P2:',P2.name,P2.x,P2.y,', Circle:',C.name,C.x,C.y,', radius',r)
            return None
        else:
            p1.x=P1.x
            p2.x=P1.x
            p1.y=C.y+sqrt((r**2)-((P1.x-C.x)**2))
            p2.y=C.y-sqrt(r**2-(P1.x-C.x)**2)
            pnts.append(p1)
            pnts.append(p2)
    elif P1.y==P2.y: #horizontal line
        if abs(P1.y-C.y)>r:
            #TODO: better error handling here
            debug('Circle does not intersect horizontal line P1:',P1.name,P1.x,P1.y,', P2:',P2.name,P2.x,P2.y,',Circle:',C.name,C.x,C.y,', radius',r)
            return None
        else:
            p1.y=P1.y
            p2.y=P1.y
            p1.x=C.x+sqrt(r**2-(P1.y-C.y)**2)
            p2.x=C.x-sqrt(r**2-(P1.y-C.y)**2)
            pnts.append(p1)
            pnts.append(p2)
    else:
        a=(P2.x-P1.x)**2+(P2.y-P1.y)**2
        b=(2.0*((P2.x-P1.x)*(P1.x-C.x))+2.0*((P2.y-P1.y)*(P1.y-C.y)))  #correction - wim vanroose 02/16/2013
        c=((C.x)**2+(C.y)**2+(P1.x)**2+(P1.y)**2-(2.0*(C.x*P1.x+C.y*P1.y ))-(r)**2) #correction - wim vanroose 02/16/2013
        i=b**2-4.0*a*c
        if i<0.0:
            #TODO: better error handling here
            debug('Circle does not intersect b/w line P1:',P1.name,P1.x,P1.y,'P2:',P2.name,P2.x,P2.y,'Circle:',C.name,C.x,C.y,'radius',r)
            return None
        elif i==0.0:
            # one intersection
            intersections=1
            mu=-b/(2.0*a)
            p1.x=P1.x+mu*(P2.x-P1.x),
            p1.y=P1.y+mu*(P2.y-P1.y)
            pnts.append(p1)
        elif i>0.0:
            # two intersections
            mu1=(-b+math.sqrt(i))/(2.0*a)
            p1.x=P1.x+mu1*(P2.x-P1.x)
            p1.y=P1.y+mu1*(P2.y-P1.y)
            mu2=(-b-math.sqrt(i))/(2.0*a)
            p2.x=P1.x+mu2*(P2.x-P1.x)
            p2.y=P1.y+mu2*(P2.y-P1.y)
            pnts.append(p1)
            pnts.append(p2)
    return pnts

def intersectChordCircle(C,r,P,chord_length):
    ''' Accepts center of circle,radius of circle,a point on the circle,and chord length.
    Returns an array of two points on the circle at chord_length distance away from original point'''
    d=chord_length
    # point on circle given chordlength & starting point=2*asin(d/2r)
    d_div_2r=d/(2.0*r)
    angle=2*asin(d_div_2r)
    pnts=[]
    pnts.append(polarPoint(C,r,angle))
    pnts.append(polarPoint(C,r,- angle))
    return pnts

def intersectLineCurve(P1,P2,curve,n=100):
    '''
    Accepts two points of a line P1 & P2,and an array of connected bezier curves [P11,C11,C12,P12,C21,C22,P22,C31,C32,P32,...]
    Returns an array points_found[] of point objects where line intersected with the curve,and tangents_found[] of tangent angle at that point
    '''
    # get polar equation for line for P1-P2
    # point furthest away from 1st point in curve[] is the fixed point & sets the direction of the angle towards the curve
    #if distance(P1,curve[0]) >=distance(P2,curve[0] ):
    #   fixed_pnt=P1
    #   angle=angleOfLine(P1,P2)
    #else:
    #   fixed_pnt=P2
    #  angle=angleOfLine(P2,P1)
    #debug('intersectLineCurve...')
    #debug('....P1 ='+P1.id+' '+str(P1.x)+','+str(P1.y))
    #debug('....P2 ='+P2.id+' '+str(P2.x)+','+str(P2.y))
    #for pnt in curve:
        #debug( '....curve ='+pnt.id+' '+str(pnt.x)+','+str(pnt.y))
    fixed_pnt=P1
    angle=angleOfLine(P1,P2)
    intersections=0
    points_found=[]
    tangents_found=[]
    pnt=Point()
    j=0
    while j<=len(curve) -4: # for each bezier curve in curveArray
        intersection_estimate=intersectLines(P1,P2,curve[j],curve[j+3]) # is there an intersection?
        if intersection_estimate !=None or intersection_estimate !='':
            interpolatedPoints=interpolateCurve(curve[j],curve[j+1],curve[j+2],curve[j+3],n)  #interpolate this bezier curve,n=100
            k=0
            while k<len(interpolatedPoints)-1:
                length=distance(fixed_pnt,interpolatedPoints[k])
                pnt_on_line=polarPoint(fixed_pnt,length,angle)
                range=distance(interpolatedPoints[k],interpolatedPoints[k+1]) # TODO:improve margin of error
                length=distance(pnt_on_line,interpolatedPoints[k])
                #debug(str(k)+'pntOnCurve='+\
                #       str(interpolatedPoints[k].x)+','+ str(interpolatedPoints[k].y)+\
                #       'intersectLineAtLength='+ str(pnt_on_line.x) +','+ str( pnt_on_line.y)\
                 #      + 'length='+str(length)+'range='+str(range))
                if ( length<=range):
                    #debug('its close enough!')
                    if k>1:
                        if (interpolatedPoints[k-1] not in points_found) and (interpolatedPoints[k-2] not in points_found):
                            points_found.append(interpolatedPoints[k])
                            tangents_found.append(angleOfLine(interpolatedPoints[k-1],interpolatedPoints[k+1]))
                            intersections+=1
                    elif k==1:
                        if (curve[0] not in intersections):
                            points_found.append(interpolatedPoints[1])
                            tangents_found.append(angleOfLine(curve[0],interpolatedPoints[2]))
                            intersections += 1
                    else:
                        intersections.append(curve[0])
                        tangents_found.append(angleOfLine(curve[0],curve[1]))
                k+=1
        j+=3 # skip j up to P3 of the current curve to be used as P0 start of next curve
        if intersections==0:
            #TODO: better error handling here
            debug('no intersections found in intersectLineCurve('+P1.id+','+P2.id+' and curve')
    #return points_found,tangents_found
    return points_found

def interpolateCurve(P0,C1,C2,P1,t=100):
    '''
    Accepts curve points P0,C1,C2,P1 & number of interpolations t
    Returns array of interpolated points of class Point
    '''
    interpolatedPoints=[P0]
    for i in range(0, t):
            j=float(i)/t # j can't be an integer,i/t is an integer..always 0.
            x = ((1-j)**3)*P0.x + 3*((1-j)**2)*j*C1.x + 3*(1-j)*(j**2)*C2.x + (j**3)*P1.x
            y = ((1-j)**3)*P0.y + 3*((1-j)**2)*j*C1.y + 3*(1-j)*(j**2)*C2.y + (j**3)*P1.y
            interpolatedPoints.append(Point('',x,y))
    interpolatedPoints.append(P1)
    return interpolatedPoints

#---svg

def addCircle(parent,id,x,y,radius=5,fill='red',stroke='red',stroke_width='1',reference='false'):
    '''create & write a circle to canvas & set it's attributes'''
    circ=inkex.etree.SubElement(parent,inkex.addNS('circle','svg'))
    circ.set('id',id)
    circ.set('cx',str(x))
    circ.set('cy',str(y))
    circ.set('r',str(radius))
    circ.set('fill',fill)
    circ.set('stroke',stroke)
    circ.set('stroke-width',stroke_width)
    if reference=='true':
        circ.attrib['reference']='true'
    return

def addSquare(parent,id,(w,h),(x,y),reference='false'):
    # create & write a square element,set its attributes
    square=inkex.etree.SubElement(parent,inkex.addNS('rect','svg'))
    square.set('id',id)
    square.set('width',str(w))
    square.set('height',str(h))
    square.set('x',str(x))
    square.set('y',str(y))
    square.set('stroke','none')
    square.set('fill','#000000')
    square.set('stroke-width','1')
    if reference=='true':
        square.attrib['reference']='true'

def addText(parent,id,x,y,text,fontsize='12',textalign='left',textanchor='left',reference='false'):
    '''Create a text element, set its attributes, then write to canvas.
    The text element is different than other elements --> Set attributes first then write to canvas using append method.
    There is no inkex.etree.SubElement() method for creating a text element & placing it into the document in one step.
    Use inkex's etree.Element() method to create an unattached text svg object,
    then use a document object's append() method to place it on the document canvas'''
    #create a text element with inkex's Element()
    txt=inkex.etree.Element(inkex.addNS('text','svg'))
    #set attributes of the text element
    txt.set('id',id)
    txt.set('x',str(x))
    txt.set('y',str(y))
    txt.text=text
    style={'text-align':textalign,'text-anchor':textanchor,'font-size':fontsize}
    txt.set('style',formatStyle(style))
    if reference=='true':
        txt.attrib['reference']='true'
        #txt.setAttribute('reference','true') #alternative syntax
    #add to canvas in the parent group
    parent.append(txt)
    return

def addLayer(parent,id):
    '''Create & write an inkscape group-layer to canvas'''
    new_layer=inkex.etree.SubElement(parent,'g')
    new_layer.set('id',id)
    new_layer.set(inkex.addNS('groupmode','inkscape'),'layer')
    new_layer.set(inkex.addNS('label','inkscape'),'%s layer' % (id))
    return new_layer

def layerVisible(layer, visible=True):
    if visible:
      layer.set("style", formatStyle({"display":"inherit"}))
    else:
      layer.set("style", formatStyle({"display":"none"}))
    
def addGroup(parent,id):
    '''Create & write an svg group to canvas'''
    new_layer=inkex.etree.SubElement(parent,'g')
    new_layer.set('id',id)
    return new_layer

def addPath(parent,id,path_str,path_type):
    '''Accepts parent,id,path string,path type. Creates attribute dictionary. Creates & writes path.'''
    reference='false'
    if path_type=='seamline':
        path_style={'stroke':'green','stroke-width':'4','fill':'none','opacity':'1','stroke-dasharray':'15,5','stroke-dashoffset':'0'}
    elif path_type=='cuttingline':
        path_style={'stroke':'green','stroke-width':'4','fill':'none','opacity':'1'}
    elif path_type=='gridline':
        path_style={'stroke':'gray','stroke-width':'4','fill':'none','opacity':'1','stroke-dasharray':'6,6','stroke-dashoffset':'0'}
        reference='true'
    elif path_type=='dartline':
        path_style={'stroke':'gray','stroke-width':'4','fill':'none','opacity':'1'}
    elif path_type=='grainline':
        path_style={'stroke':'DimGray','stroke-width':'3','fill':'none','opacity':'1',\
                    'marker-start':'url(#ArrowStart)','marker-end':'url(#ArrowEnd)'}
    elif path_type=='slashline':
        path_style={'stroke':'green','stroke-width':'4','fill':'none','opacity':'1'}
    svg_path=inkex.etree.SubElement(parent,inkex.addNS('path','svg'))
    svg_path.set('id',id)
    svg_path.set('d',path_str)
    svg_path.set('style',formatStyle(path_style))
    if reference=='true':
        svg_path.attrib['reference']='true'
    return svg_path

def formatPath(*args):
    """
    Accepts a series of pseudo svg path arguments  'M','L','C' ,and point objects.
    Returns path_string which is a string formatted for use as the 'd' path attribute in an svg object.
    """
    tokens=[] # initialize an empty array
    # put all the parameters in *args into the array
    for arg in args:
        tokens.append(arg)
    com=','
    path_string=''
    i=0
    while (i < len(tokens)):
        cmd=tokens[i]
        if (cmd=='M') or (cmd=='L'):
            path_string += " %s %g %g" % (cmd, tokens[i+1].x, tokens[i+1].y)
            i=i+2
        elif (cmd=='C'):
            path_string += " %s %g %g %g %g %g %g" % (cmd, tokens[i+1].x,\
                            tokens[i+1].y, tokens[i+2].x, tokens[i+2].y, tokens[i+3].x, tokens[i+3].y)
            i=i+4
    return path_string

def resizeDoc(doc, border, *pieces):
  right = Point('right', 0, 0)
  bottom = Point('bottom', 0, 0)
  for piece in pieces:
    rightpoint = rightmost(piece.seam)
    right = rightmost([right, rightpoint])
    bottompoint = lowest(piece.seam)
    bottom = lowest([bottom, bottompoint])
    
  doc_width = right.x + border
  doc_height = bottom.y + border
  doc.set('width',str(doc_width))
  doc.set('height',str(doc_height))

def addDefs(doc):
    '''Add defs group with markers to the document'''
    defs=inkex.etree.SubElement(doc,inkex.addNS('defs','svg'))
    #add start arrow
    marker=inkex.etree.SubElement(defs,'marker',{'id':'ArrowStart','orient':'auto','refX':'0.0','refY':'0.0','style':'overflow:visible'})
    inkex.etree.SubElement(marker,'path',{'d':'M 0,0 L 0,5 L -20,0 L 0,-5 z', 'style':'fill:DimGray; stroke:DimGray; stroke-width:0.5'})
    #add end arrow
    marker=inkex.etree.SubElement(defs,'marker',{'id':'ArrowEnd','orient':'auto','refX':'0.0','refY':'0.0','style':'overflow:visible'})
    inkex.etree.SubElement(marker,'path', {'d':'M 0,0 L 0,5 L 20,0 L 0,-5 z', 'style':'fill:DimGray; stroke:DimGray; stroke-width:0.5'})

