# -*- coding: utf-8 -*-

import argparse

parser = argparse.ArgumentParser(description='Read and modify Gcode')

parser.add_argument('filename', action='store', help='Gcode-File to be altered')

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-l', '--layer',  action='store', type=int, metavar='layer', help='The layer at which to continue printing')
group.add_argument('-z', '--zheight', action='store', type=float, metavar='height', help='The height at which to continue printing')

args = parser.parse_args()

#todo:

#get post-header code point
startLayer0 = None

with open(args.filename) as f:
    lastpos = f.tell()
    for line in f:        
        if ';LAYER:0' in line:
            startLayer0 = lastpos            
        lastpos = f.tell()

if startLayer0:
    print startLayer0
    

#search for height if possible

#get layer number
#get height
#get extrusion of last layer
#get xy position of first point
#delete non-wanted code
#insert post-init move to height + safety
#insert extrusion set to last layers value
#save file
#return x,y of first point to calling program
