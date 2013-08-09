# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from segue.backend.processor.foreground import ForegroundProcessor


def register(**kw):
    '''Register processor.'''
    return ForegroundProcessor('in_app', 'Here And Now', host=kw.get('host'))

