# -*- coding: utf-8 -*-

import argparse

parser = argparse.ArgumentParser(description='Read and modify Gcode')

parser.add_argument('filename', action='store', help='Gcode-File to be altered')

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-l', '--layer',  action='store', type=int, default=None, metavar='layer', help='The layer at which to continue printing')
group.add_argument('-z', '--zheight', action='store', type=float, default=None, metavar='height', help='The height at which to continue printing')

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
repeat = False
extrude = None
layer = None
height = None

with open(args.filename) as f:  
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
            
#search for height
            nextLine = fplus.ahead()
            if ('G1' in nextLine or 'G0'in nextLine) and 'Z' in nextLine:
                command = nextLine.split(' ')
                for part in command:
                    if 'Z' in part:
                        #get the next height value
                        height=float(part[1:])
#get layer number
            lastLine = fplus.last()                
            if ('G1' in lastLine or 'G0'in lastLine) and 'E' in lastLine:
                command = lastLine.split(' ')
                for part in command:
                    if 'E' in part:
                        #get the last extrusion value
                        extrude=float(part[1:])
            
        endOfLastLine = fplus.tell()

if startLayer0:
    print startLayer0
if extrude:
    print extrude
if height:
    print height
    


#get height
#get extrusion of last layer
#get xy position of first point
#delete non-wanted code
#insert post-init move to height + safety
#insert extrusion set to last layers value
#save file
#return x,y of first point to calling program
