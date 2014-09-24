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

from collections import deque


class windowIterator(object):
    """ An iterator wrapper with look-ahead/-behind """
    not_started = object()

    def __init__(self, iterator, num):
        """ Create wrapper around original iterator with
        configurable history/look-ahead buffer
        """
        self._size = num
        self._timeline = deque(maxlen=2*num+1)
        self._iter = iter(iterator)
        self._is_first = True
        self._current = self.not_started

    def __iter__(self):
        return self

    def next(self):
        """Get next element"""
        #call next() several times on first run
        if self._is_first:
            for _ in xrange(self._size + 1):
                try:
                    self._timeline.append(self._iter.next())
                except StopIteration:
                    self._timeline.append(None)
            self._current = self._timeline[self._size]
            #continue normally from here
            self._is_first = False

        #normal case, rotate through
        else:
            try:
                self._timeline.append(self._iter.next())
            except StopIteration:
                self._timeline.append(None)
            self._current = self._timeline[self._size]

        if not self._current:
            raise StopIteration

        return self._current

    def last(self, index=1):
        """Get element from history.

        (does not alter the current position)
        """
        if index > self._size:
            raise RuntimeError("Exceeded buffer size, out of bounds.")

        if self._timeline[self._size - index]:
            return self._timeline[self._size - index]
        else:
            raise RuntimeWarning("History not yet old enough.")
            return self._timeline[self._size - index]

    def ahead(self, index=1):
        """Get future element from look-ahead buffer.

        (does not alter the current position)
        """
        if index > self._size:
            raise RuntimeError("Exceeded buffer size, out of bounds.")

        if self._timeline[self._size + index]:
            return self._timeline[self._size + index]
        else:
            raise RuntimeWarning("Not enough elements left.")
            return self._timeline[self._size + index]

    def debug(self):
        msg = "read buffer (size: {}) content:\n".format(self._size)
        msg += "past\n"
        for (index, element) in zip(xrange((2 * self._size) + 1),
                                    self._timeline):
            if index == self._size:
                msg += "present >> {}\n".format(element[:-1])
            else:
                msg += element
        msg += "future\n"
        return msg
