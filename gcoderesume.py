# -*- coding: utf-8 -*-
"""
@author: Chaos

Copyright 2014 by Chaos99

GcodeResume is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

GcodeResume is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with GcodeResume.  If not, see <http://www.gnu.org/licenses/>.
"""


import argparse
import tempfile
from sys import exit
from os import remove
from shutil import copy
from helpers import windowIterator
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.WARN)
if not log.handlers:
    log.addHandler(logging.StreamHandler())

parser = argparse.ArgumentParser(description='Read and modify Gcode')

parser.add_argument('filename', action='store',
                    help='Gcode-File to be altered')

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-l', '--layer',  action='store', type=int,
                   default=None, metavar='layer',
                   help='The layer at which to continue printing')
group.add_argument('-z', '--zheight', action='store', type=float,
                   default=None, metavar='height',
                   help='The height at which to continue printing')

parser.add_argument('-e', '--epsilon', action='store', type=float,
                    default=0.05, metavar='epsilon',
                    help="When to still print the layer even if the height is "
                         "missed by that much")

args = parser.parse_args()


def getCoords(fileIterator, searchRadius):
    '''search for z coordinate in G0/G1 command in next lines'''
    xCoord = None
    yCoord = None
    zCoord = None
    for line in xrange(searchRadius):
        nextLine = fileIterator.ahead(line)
        if ('G1' in nextLine or 'G0'in nextLine) and 'Z' in nextLine:
            command = nextLine.split(' ')
            for part in command:
                if 'X' in part:
                    xCoord = float(part[1:])
                if 'Y' in part:
                    yCoord = float(part[1:])
                if 'Z' in part:
                    zCoord = float(part[1:])
            if xCoord and yCoord and zCoord:
                log.debug("Found x=%f, y=%f, z=%f", xCoord, yCoord, zCoord)
                return xCoord, yCoord, zCoord
    # this is only reached if no complete coordinate set is found
    raise RuntimeError("No next G1/G0 command with x/y/z coords "
                       "found in next {} lines".format(searchRadius))


def getExtrusion(fileIterator, searchRadius):
    '''search for extrusion parameter in G0/G1 command in last lines'''
    for line in xrange(searchRadius):
        lastLine = fileIterator.last(line)
        if ('G1' in lastLine or 'G0'in lastLine) and 'E' in lastLine:
            command = lastLine.split(' ')
            for part in command:
                if 'E' in part:
                    #get the last extrusion value
                    extrude = float(part[1:])
                    return extrude  # leave if found
    raise RuntimeError("No previous G1/G0 command with extrusion value "
                       "found in last {} lines".format(searchRadius))


extrude = None
layer = None
height = 0.0
xCoord = None
yCoord = None
stop = False
history = 5


#create temp file to copy content line by line
w = tempfile.NamedTemporaryFile(mode='w+t', delete=False)
temp_name = w.name


#open original for reading
with open(args.filename, mode='rt') as f:
    #re-instantiate as iterator with look-back and look-ahead
    fplus = windowIterator(f, history)
    for line in fplus:
#get post-header code point
        if ';LAYER:0' in line:
            #stop copying line to new file
            stop = True

        if stop and ';LAYER:' in line:
            # get current layer number
            layer = int(line.split(':')[1].strip())
            log.debug("Layer: %d", layer)
#search for height
#get xy position of first new point
            xCoord, yCoord, height = getCoords(fplus, history)

#search for layer or height
        #if given height is reached or only slightly missed or
        #if layer is reached
        if (stop and
            ((args.zheight and
             (args.zheight <= height or
              abs(args.zheight - height) <= args.epsilon)) or
             (args.layer and args.layer == layer))):
            if args.layer:
                log.debug("\nFound layer %d at:\n%s",
                          args.layer, fplus.debug())
            elif args.zheight:
                log.debug("\nFound height %f at:\n%s",
                          args.zheight, fplus.debug())

            #get extrusion of last layer
            extrude = getExtrusion(fplus, history)
            #insert extrusion set to last layers value
            if extrude:
                resetExtrusionCommand = "G92 E{0:.5f}\n".format(extrude)
                log.debug("Reset extrusion: " + resetExtrusionCommand)
                w.write(resetExtrusionCommand)
            else:
                raise RuntimeWarning("No Extrusion value found.")
            #insert post-init move to height + safety
            gotoHeightCommand = "G0 X0 Y0 Z{0:.2f}\n".format(height+10)
            log.debug("Go to Height: " + gotoHeightCommand)
            w.write(gotoHeightCommand)
            gotoStartCommand = "G0 X{0:.2f} Y{0:.2f} Z{0:.2f}".format(xCoord,
                                                                      yCoord,
                                                                      height+1)
            log.debug("Go to Start: " + gotoStartCommand)
            #continue copying lines to new file
            stop = False

    #copy each line to temp file
        if not stop:
            w.write(line)

if not layer:  # LAYER:0 was not found
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
