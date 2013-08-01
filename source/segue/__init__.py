# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import os
import imp
import uuid


def discover_processors(paths=None, options=None):
    '''Return processor plugins discovered on *paths*.
    
    If *paths* is None will try to use environment variable 
    :envvar:`SEGUE_PROCESSOR_PLUGIN_PATH`
    
    Each discovered plugin should have a register function that can be called
    to return a processor instance. The register function should accept
    arbitrary keyword arguments.
    
    *options* will be passed to the register functions as keyword arguments.
    
    '''
    processors = []
    
    if paths is None:
        plugin_path = os.environ.get('SEGUE_PROCESSOR_PLUGIN_PATH')
        if plugin_path:
            paths = plugin_path.split(os.pathsep)
        else:
            paths = []
    
    if options is None:
        options = {}
    
    for path in paths:
        for base, directories, filenames in os.walk(path):
            for filename in filenames:
                name, extension = os.path.splitext(filename)
                if extension != '.py':
                    continue
                
                module_path = os.path.join(base, filename)
                module_name = uuid.uuid4().hex
                
                module = imp.load_source(module_name, module_path)
                processor = module.register(**options)
    
    return processors

