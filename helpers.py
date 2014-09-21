# -*- coding: utf-8 -*-
"""
Created on Mon Sep 22 00:16:32 2014

@author: Chaos
"""


class windowIterator(object):
    """ An iterator wrapper with look-ahead/-behind """
    not_started = object()

    def __init__(self, iterator, num):
        """ Create wrapper around original iterator with
        configurable history/look-ahead buffer
        """
        self._iter = iter(iterator)
        self._is_first = True
        self._is_last = False
        self._last = self.not_started
        self._current = self.not_started
        self._next = self.not_started

    def __iter__(self):
        return self

    def next(self):
        """Get next element"""
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
        """Get last element from history.

        (does not alter the current position)
        """
        if self._is_first:
            raise RuntimeError("Tried to get line before the first.")
        else:
            return self._last

    def ahead(self):
        """Get next element from look-ahead buffer.

        (does not alter the current position)
        """
        if self._is_last:
            raise RuntimeError("Tried to get next line after last.")
        else:
            return self._next
