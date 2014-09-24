## README
Python script that changes a GCODE file produced with CuraEngine
to only print from a certain layer or certain height.

Beware: The file is changes in-place. No Backup done!

Usage: ```python gcoderesume.py filname [-l <layer> | -z <height>] [-e <error margin>]```

The error margin specifies, how much the layer height can be smaller than the given height to
still begin printing with that layer. Default is 0.05.


## License
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
