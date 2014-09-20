Python script that changes a GCODE file produced with CuraEngine
to only print from a certain layer or certain height.

Beware: The file is changes in-place. No Backup done!

Usage: ```python gcoderesume.py filname [-l <layer> | -z <height>] [-e <error margin>]```

The error margin specifies, how much the layer height can be smaller than the given height to
still begin printing with that layer. Default is 0.05.
