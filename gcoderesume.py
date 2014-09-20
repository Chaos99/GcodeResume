# -*- coding: utf-8 -*-

import argparse

parser = argparse.ArgumentParser(description='Read and modify Gcode')

parser.add_argument('filename', action='store', help='Gcode-File to be altered')

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-l', '--layer',  action='store', type=int, default=None, metavar='layer', help='The layer at which to continue printing')
group.add_argument('-z', '--zheight', action='store', type=float, default=None, metavar='height', help='The height at which to continue printing')

parser.add_argument('-e', '--epsilon', action='store', type=float, default=0.1, metavar='epsilon', help='When to still print the layer even if the height is missed by that much')

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
#todo:

startLayer0 = None
cutPosition = None
repeat = False
extrude = None
layer = None
height = None
xCoord = None
yCoord = None

with open(args.filename, mode='r+t') as f:  
    #re-instantiate as iterator with look-back and look-ahead
    fplus = rewindable_iterator(f)
    for line in fplus:   
        endOfLastLine = fplus.tell()
#get post-header code point
        if ';LAYER:0' in line:
            #get position to cut later on
            startLayer0 = endOfLastLine 
        if ';LAYER:' in line:              
            # get current layer number
            layer = int(line.split(':')[1].strip())
            cutPosition = endOfLastLine
            
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
            
        endOfLastLine = fplus.tell()

#search for layer or height
        #if given height is reached or only slightly missed or if layer is reached
        if (args.zheight and \
           ( args.zheight >= height or (args.zheight - height )<= args.epsilon)) or \
           ( args.layer and args.layer == layer):
            break

#insert extrusion set to last layers value
resetExtrusionCommand = "G92 E{0:.5f}".format(extrude)

#insert post-init move to height + safety
gotoHeightCommand = "G0 X0 Y0 Z{0:.2f}".format(height+10)

gotoStartCommand = "G1 X{0:.2f} Y{0:.2f} Z{0:.2f}".format(xCoord, yCoord, height+1)


print resetExtrusionCommand
print gotoHeightCommand

if startLayer0:
    print startLayer0
if cutPosition:
    print cutPosition
if extrude:
    print xCoord 
    print yCoord
    print extrude
if height:
    print height
    


#delete non-wanted code
#save file
#return x,y of first point to calling program
