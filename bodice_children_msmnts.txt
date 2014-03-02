#!/usr/bin/python
from xmlparser import *

fo = open('measurementnames.txt', 'w+')

# measurementsraw = open('women_measurements.xml', 'r')
measurementsraw = open('children_measurements.xml', 'r')
measurements = xml2obj(measurementsraw)
measurementsraw.close()


for measurement in measurements.measurement:
  fo.write(measurement.name)
  fo.write("\n")
  
fo.close()