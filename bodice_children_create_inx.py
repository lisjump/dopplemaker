#!/usr/bin/python
from xmlparser import *
import string, re, sys

def sortkey(item):
   splitkeys =  re.findall('^(\d*)(\w*)', item)
   if splitkeys[0][0] == "":
     return sys.maxint, splitkeys[0][1]
   else:
     return int(splitkeys[0][0]), splitkeys[0][1] 

default_size = "8"

output = open('bodice_pivnick.inx', 'w+')

measurementsneededfile = open('bodice_pivnick_msmnts.txt', 'r')
measurementsneededraw = list(measurementsneededfile)
measurementsneeded = []
for measurement in measurementsneededraw:
  measurementsneeded.append(string.rstrip(str(measurement), '\n'))

measurementsraw = open('women_measurements.xml', 'r')
measurementsxml = xml2obj(measurementsraw)
measurementsraw.close()

try:
  measurementscustomraw = open('women_measurements_custom.xml', 'r')
  measurementscustomxml = xml2obj(measurementscustomraw)
  measurementscustomraw.close()
except (OSError, IOError):
  measurementscustomxml = measurementsxml


sizesavailable = []
categories = []
measurements  = {}

for measurement in measurementsxml.measurement:
  if measurement.name in measurementsneeded:
    name = str(measurement.name)
    measurements[name] = {}
    measurements[name]['category'] = str(measurement.category)
    measurements[name]['gui_text'] = str(measurement.gui_text)
    measurements[name]['description'] = str(measurement.description)
    measurements[name]['sizes'] = {}
    measurements[name]['sizesavailable'] = set()
    categories.append(measurements[name]['category'])
    for size in measurement.sizes.size:
      if size.value:
        sizesavailable.append(str(size.name))
        measurements[name]['sizesavailable'].add(str(size.name))
        measurements[name]['sizes'][str(size.name)] = str(size.value)

for measurement in measurementscustomxml.measurement:
  name = str(measurement.name)
  if name not in measurementsneeded: 
    continue
  if name not in measurements.keys():
    measurements[name] = {}
    measurements[name]['category'] = str(measurement.category)
    measurements[name]['gui_text'] = str(measurement.gui_text)
    measurements[name]['description'] = str(measurement.description)
    measurements[name]['sizes'] = {}
    measurements[name]['sizesavailable'] = set()
    categories.append(measurements[name]['category'])
  for size in measurement.sizes.size:
    if size.value:
	  sizesavailable.append(str(size.name))
	  measurements[name]['sizesavailable'].add(str(size.name))
	  measurements[name]['sizes'][str(size.name)] = str(size.value)

  

categories = set(categories)
sizesavailable = set(sizesavailable)

for name in measurements:
  sizesavailable &= measurements[name]['sizesavailable']

sizesavailable = list(sizesavailable)
sizesavailable.sort(key = sortkey)
  
  
inxstart = '''
<inkscape-extension>

  <_name>Bodice-Pivnick</_name>
  <id>sewingpatterns.bodice_pivnick.llueninghoener</id>

  <dependency type="executable" location="extensions">bodice_pivnick.py</dependency>
  <dependency type="executable" location="extensions">inkex.py</dependency>
  <dependency type="executable" location="extensions">sewing_patterns.py</dependency>
  <param name="extra" type="notebook">
    <page name="extra" _gui-text="Options">
      <param name="m_unit" type="optiongroup" _gui-text="Select measurement: ">
            <option value="Inches">Inches</option>
            <option value="Centimeters">Centimeters</option>
      </param>
      <param name="sleeves" type="optiongroup" _gui-text="Sleeves: ">
            <option value="yes">Yes</option>
            <option value="no">No</option>
      </param>
      <param name="size" type="optiongroup" _gui-text="Select Size: ">
            <option type="string" value="custom">Custom</option>
'''
output.write(inxstart)
for size in sizesavailable:
  output.write("            <option type=\"string\" value=\"" + size + "\">" + size + "</option>\n")
output.write("      </param>\n    </page>\n")

itemsperpage = 7

for category in categories:
  count = 0
  for name in measurements:
    if measurements[name]['category'] == category:
      if count == 0:
        output.write("    <page name=\"extra\" _gui-text=\"" + category + "\">\n")
      count = count + 1
      default_value = str(25.5)
      for sizename in measurements[name]['sizes']:
        if sizename == default_size:
          default_value = measurements[name]['sizes'][sizename]
          break
      if (count % itemsperpage == 0): 
        output.write("    </page>\n<page name=\"extra\" _gui-text=\"" + category + str(count/itemsperpage+1) + "\">\n")
      output.write("      <param name=\"" + name + "\" type=\"float\" precision=\"3\"  min=\"1.0\" max=\"1000.0\" ")
      output.write("gui-text=\"" + measurements[name]['gui_text'] + "\">" + default_value + "</param>\n")
      if measurement.description:
        output.write("      <param name=\"extra\" type=\"description\">" + measurements[name]['description'] + "</param>\n")
  if count > 0:
    output.write("    </page>\n")
    
inxend = '''
  </param>

  <effect>
    <object-type>all</object-type>
    <effects-menu>
       <submenu _name="Sewing Patterns"/>
    </effects-menu>
  </effect>

  <script>
    <command reldir="extensions" interpreter="python">bodice_pivnick.py</command>
  </script>

</inkscape-extension>
'''

output.write(inxend)

output.close()