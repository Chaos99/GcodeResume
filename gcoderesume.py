# -*- coding: utf-8 -*-

import argparse
import tempfile
from sys import exit
from os import remove
from shutil import copy

parser = argparse.ArgumentParser(description='Read and modify Gcode')

parser.add_argument('filename', action='store', help='Gcode-File to be altered')

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-l', '--layer',  action='store', type=int, default=None, metavar='layer', help='The layer at which to continue printing')
group.add_argument('-z', '--zheight', action='store', type=float, default=None, metavar='height', help='The height at which to continue printing')

parser.add_argument('-e', '--epsilon', action='store', type=float, default=0.05, metavar='epsilon', help='When to still print the layer even if the height is missed by that much')

args = parser.parse_args()


class rewindable_iterator(object):
    not_started = object()

    def __init__(self, iterator):
        self._iter = iter(iterator)
        self._is_first = True
        self._is_last = False
        self._last = self.not_started
        self._current = self.not_started
        self._next = self.not_started

    def __iter__(self):
        return self

    def next(self):
        #call next() two times on first run
        if self._is_first:
            self._current = self._iter.next()
            try:
                #will fail on one-element lists
                self._next = self._iter.next()
            except StopIteration:
                self._is_last = True
                self._next = self.not_started
            #continue normally from here
            self._is_first = False
        
        #seems like raising thos is normal at the end
        elif self._is_last:
            raise StopIteration
        
        #normal case, rotate through
        else:
            self._last = self._current
            self._current = self._next            
            try:
                self._next = self._iter.next()
            except StopIteration:
                self._is_last = True
                self._next = self.not_started
                
        return self._current

    def last(self):
        if self._is_first:
            raise RuntimeError("Tried to get line before the first.")
        else:
            return self._last
        
    def ahead(self):
        if self._is_last:
            raise RuntimeError("Tried to get next line after last.")
        else:
            return self._next
            
    def tell(self):
        return self._iter.tell()
        
    def seek(self, num):
        return self._iter.seek(num)

extrude = None
layer = None
height = 0.0
xCoord = None
yCoord = None
stop = False

#create temp file to copy content line by line
w = tempfile.NamedTemporaryFile(mode='w+t', delete=False)
temp_name = w.name

#open original for reading
with open(args.filename, mode='rt') as f:  
    #re-instantiate as iterator with look-back and look-ahead
    fplus = rewindable_iterator(f)
    for line in fplus:    
#get post-header code point
        if ';LAYER:0' in line:
            #stop copying line to new file 
            stop = True
            
        if stop and ';LAYER:' in line:              
            # get current layer number
            layer = int(line.split(':')[1].strip())            
#search for height
            nextLine = fplus.ahead()
            if ('G1' in nextLine or 'G0'in nextLine) and 'Z' in nextLine:
                command = nextLine.split(' ')
                for part in command:
                    if 'Z' in part:
                        #get the next height value
                        height=float(part[1:])
#get extrusion of last layer
            lastLine = fplus.last()  
            
            if ('G1' in lastLine or 'G0'in lastLine) and 'E' in lastLine:
                command = lastLine.split(' ')
                for part in command:
                    if 'E' in part:
                        #get the last extrusion value
                        extrude=float(part[1:])
#get xy position of first new point                        
                    if 'X' in part:
                        xCoord = float(part[1:])
                    if 'Y' in part:
                        yCoord = float(part[1:])
            
#search for layer or height 
        #if given height is reached or only slightly missed or if layer is reached
        if stop and \
           ((args.zheight and \
             ( args.zheight <= height or \
              abs(args.zheight - height ) <= args.epsilon\
             )\
            ) or \
            ( args.layer and args.layer == layer) \
           ) :
        
            #insert extrusion set to last layers value
            if extrude:
                resetExtrusionCommand = "G92 E{0:.5f}\n".format(extrude)
                w.write(resetExtrusionCommand)
            else:
                raise RuntimeWarning("No Extrusion value found.")
            #insert post-init move to height + safety
            gotoHeightCommand = "G0 X0 Y0 Z{0:.2f}\n".format(height+10)
            w.write(gotoHeightCommand)                
            #gotoStartCommand = "G0 X{0:.2f} Y{0:.2f} Z{0:.2f}".format(xCoord, yCoord, height+1)
            #continue copying lines to new file
            stop = False

    #copy each line to temp file
        if not stop:
            w.write(line)

if not layer: #LAYER:0 was not found 
    w.close()
    remove(temp_name)
    exit("Nothing removed from file. Invalid content or parameters.")  
      
#save file
# close temp file, copy over original, destroy temp    
w.close()
copy(temp_name, args.filename)
remove(temp_name)

#return x,y of first point to calling program
#print xCoord, yCoord