# -*- coding: utf-8 -*-

import argparse

parser = argparse.ArgumentParser(description='Read and modify Gcode')

parser.add_argument('filename', action='store', help='Gcode-File to be altered')

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-l', '--layer',  action='store', type=int, default=None, metavar='layer', help='The layer at which to continue printing')
group.add_argument('-z', '--zheight', action='store', type=float, default=None, metavar='height', help='The height at which to continue printing')

args = parser.parse_args()

#todo:

#get post-header code point
startLayer0 = None
endOfLastLine = None
endOfSecondToLastLine = None
repeat = False
extrude = None
layer = None

with open(args.filename) as f:   
    for line in f:   
        #remember positions of last 3 lines
        endOfThirdToLastLine = endOfSecondToLastLine
        endOfSecondToLastLine = endOfLastLine
        endOfLastLine = f.tell()
        if ';LAYER:0' in line:
            #get position to cut later on
            startLayer0 = endOfLastLine 
        if ';LAYER:' in line:   
            #security block, because we will come back to this after the backtracking
            if repeat: 
                repeat = False
                continue
            # get current layer number
            layer = int(line.split(':')[1].strip())
            
            # if layer number given as parameter, search for it
            if args.layer and layer == args.layer:
                repeat = True
                #jump back to last line
                f.seek(endOfSecondToLastLine)
                lastLine = f.readline() #reads just the newline char
                lastLine = f.readline()
                if ('G1' in lastLine or 'G0'in lastLine) and 'E' in lastLine:
                    command = lastLine.split(' ')
                    for part in command:
                        if 'E' in part:
                            #get the last extrusion value
                            extrude=float(part[1:])
                
        endOfLastLine = f.tell()

if startLayer0:
    print startLayer0
if extrude:
    print extrude
    

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
