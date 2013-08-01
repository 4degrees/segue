# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from segue.backend.processor.background import BackgroundProcessor


def register(**kw):
    '''Register processor.'''
    return BackgroundProcessor('local', 'In The Background On This Machine')

