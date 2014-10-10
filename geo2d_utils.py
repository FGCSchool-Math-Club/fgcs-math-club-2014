#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
This module is used by the :mod:`geometry` module. It introduces some
helper functions that I felt would best go in another module altogether.
"""

import math
from functools import wraps

# convenience notation
inf = float('inf')

def find_first_missing(seq):
    """
    Given an ascending sequence `seq`, the first missing number is returned
    if any, else None.

    Parameters
    ----------
    seq : list of ints
        A sequence of numbers in ascending order in which to search for the
        first missing element (ie. the sequence is not contiguous and the
        first gap is found).

    Returns
    -------
    out : int
        If a first missing number is found then it is returned, else `None` is
        returned.
    """

    mid = int(len(seq)/2)
    first_half = seq[:mid]
    last_half = seq[mid:]
    if seq[mid] - seq[mid-1] > 1:
        return seq[mid-1] + 1
    if first_half[-1] - first_half[0] != len(first_half) - 1:
        return find_first_missing(first_half)
    if last_half[-1] - last_half[0] != len(last_half) - 1:
        return find_first_missing(last_half)
    return None

def float_to_2pi(angle):
    """
    Convert any floating point number to the inverval [0, 2pi).

    Parameters
    ----------
    angle : float
        The floating point number to be remapped to [0, 2pi).

    Returns
    -------
    out : float
        A number in the interval [0, 2pi), corresponding to the floating point
        number `angle`.
    """

    return angle % (2*math.pi)

def rotated(list_, by):
    """
    Rotates an iterable (but only if it supports negative indexing) by the
    given amount.

    Parameters
    ----------
    list_ : list-like with negative indexing
        The `list` to be rotated.
    by : int
        The amount, ie. the number of places to rotate in the right direction
        the list by, 0 returns an identical `list`. This can also be negative
        and if so, then it will rotate the `list` to the left by the amount
        given.
    """

    if by == 0:
        return list_
    if by == -len(list_):
        # since giving by as -len(list_) is essentially the same as giving
        # by == 0, we make it raise an IndexError to be consistent with the
        # positive counterpart
        by -= 1
    # here we first determine if the number of places is in the right interval
    list_[by]
    if by < 0:
        by += len(list_)
    return list_[-by:] + list_[:-by]

def cached_property(func):
    """
    Simple decorator for caching class properties.

    Parameters
    ----------
    func : class method
        The class method to perform caching on. It has to be part of a
        class otherwise this won't make sense.

    Returns
    -------
    out : function
        The function decorated with property decorator (only for getting, not
        setting).
    """

    @wraps(func)
    def fget(self):
        if not hasattr(self, '_cached'):
            self._cached = {}
        return self._cached.setdefault(cached_name, func(self))

    cached_name = func.__name__
    return property(fget=fget)
