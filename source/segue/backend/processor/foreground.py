# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from .base import Processor


class ForegroundProcessor(Processor):
    '''Foreground processor.'''
    
    def process(self, command, args=None, kw=None):
        '''Process *command* with *args* and *kw*.'''
        if args is None:
            args = ()
        
        if kw is None:
            kw = {}
        
        command(*args, **kw)

