# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import subprocess
import pickle
import base64

try:
    from shlex import quote
except ImportError:
    from pipes import quote

from .base import Processor
from .. import pickle_support


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

