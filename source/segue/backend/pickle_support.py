# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

'''Pickle support for instancemethod's'''

import copy_reg
import types


def pickle_method(method):
    '''Pickle a method.'''
    method_name = method.im_func.__name__
    obj = method.im_self
    cls = method.im_class
    
    if method_name.startswith('__') and not method_name.endswith('__'):
        # Handle mangled names
        cls_name = cls.__name__.lstrip('_')
        method_name = '_{0}{1}'.format(cls_name, method_name)
    
    return unpickle_method, (method_name, obj, cls)


def unpickle_method(method_name, obj, cls):
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
copy_reg.pickle(types.MethodType, pickle_method, unpickle_method)

