__author__ = 'Carlos Montes'

''' Utility functions, context managers and decorators related to Maya functionality. '''

import pymel.core as pmc


# Context manager that opens an undo chunk when entered, and closes it on exit
class undo_chunk(object):
    def __enter__(self):
        pmc.undoInfo(openChunk=True)
        
    def __exit__(self, *_):
        pmc.undoInfo(closeChunk=True)


# Create and close an undo chunk, and undo  in case of an error
class undo_on_error(object):
    def __enter__(self):
        pmc.undoInfo(openChunk=True)
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        pmc.undoInfo(closeChunk=True)
        if exc_val is not None:
            pmc.undo()