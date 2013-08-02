# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import subprocess
import pickle
import base64
import copy_reg
import types

try:
    from shlex import quote
except ImportError:
    from pipes import quote

from .base import Processor

# Support for instancemethod pickling
def _pickle_method(method):
    '''Pickle a method.'''
    method_name = method.im_func.__name__
    obj = method.im_self
    cls = method.im_class
    
    if method_name.startswith('__') and not method_name.endswith('__'):
        # Handle mangled names
        cls_name = cls.__name__.lstrip('_')
        method_name = '_{0}{1}'.format(cls_name, method_name)
    
    return _unpickle_method, (method_name, obj, cls)


def _unpickle_method(method_name, obj, cls):
    '''Unpickle a method.'''
    if obj and method_name in obj.__dict__:
        # Handle classmethod
        cls, obj = obj, None
    
    for cls in cls.__mro__:
        try:
            method = cls.__dict__[method_name]
        except KeyError:
            pass
        else:
            break
    
    return method.__get__(obj, cls)


# Register instancemethod support
copy_reg.pickle(types.MethodType, _pickle_method, _unpickle_method)


class BackgroundProcessor(Processor):
    '''Local background processor.'''
    
    def process(self, command, args=None, kw=None):
        '''Process *command* with *args* and *kw*.'''
        if args is None:
            args = ()
        
        if kw is None:
            kw = {}
        
        serialised = base64.b64encode(
            pickle.dumps(
                {'command': command, 'args': args, 'kw': kw},
                pickle.HIGHEST_PROTOCOL
            )
        )
        
        python_statement = (
            'import pickle;'
            'import base64;'
            'data = base64.b64decode(\'{0}\');'
            'data = pickle.loads(data);'
            'data[\'command\'](*data[\'args\'], **data[\'kw\'])'
        ).format(serialised.replace("'", r"\'"))

        command = ' '.join(['python', '-c', '"{0}"'.format(python_statement)])
        print command
        print ''
        process = subprocess.Popen(command)
        return 'Background process started: {0}'.format(process.pid)

