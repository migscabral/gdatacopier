#!/usr/bin/env python
'''Exceptions raised by GDataCopier.
'''

__all__ = [
    'GDataCopierError',
    'GDataCopierConfigurationError',
    'GDataCopierOperationError',
    'GDataCopierFolderNotExists',
    'GDataCopierDuplicateDocumentNameFound',
]

# Base class for all gdatacopier exceptions
class GDataCopierError(StandardError):
    '''Base class for all gdatacopier exceptions.'''
    pass

# Specific exception classes
class GDataCopierConfigurationError(GDataCopierError):
    '''Exception raised when a user configuration error is detected.'''
    pass

class GDataCopierOperationError(GDataCopierError):
    '''Exception raised when a runtime error is detected.'''
    pass

class GDataCopierFolderNotExists(GDataCopierError):
    '''Exception raised when the folder inserted not exists.'''
    pass

class GDataCopierDuplicateDocumentNameFound(Exception):
    '''Exception raised when more than one match of the document name is found.'''
    pass