# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import multiprocessing

from .base import Processor


class BackgroundProcessor(Processor):
    '''Local background processor.'''
    
    def process(self, command, args=None, kw=None):
        '''Process *command* with *args* and *kw*.'''
        if args is None:
            args = ()
        
        if kw is None:
            kw = {}
        
        process = multiprocessing.Process(target=command, args=args, kwargs=kw)
        process.start()
        process.join()

