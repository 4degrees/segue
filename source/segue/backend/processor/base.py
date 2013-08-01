# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.


class Processor(object):
    '''Processor.'''
    
    def __init__(self, name, display_name):
        '''Initialise with *name* and *display_name*.'''
        super(Processor, self).__init__()
        self.name = name
        self.display_name = display_name
    
    def process(self, command, args, kw):
        '''Process *command* with *args* and *kw*.'''
        raise NotImplementedError()

