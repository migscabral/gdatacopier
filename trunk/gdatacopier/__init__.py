#!/usr/bin/env python

import sys
if sys.hexversion < 0x2050000:
    raise ImportError('GDataCopier requires Python version 2.5. or later')

__all__ = [
    'exceptions',
    'helpers',
]