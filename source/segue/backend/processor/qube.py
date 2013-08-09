# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import pickle
import base64
try:
    from shlex import quote
except ImportError:
    from pipes import quote

from .base import Processor
from .. import pickle_support


class QubeProcessor(Processor):
    '''Foreground processor.'''
    
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

        command = []
        if self.host is None:
            command.extend('python')
        else:
            command.extend(self.host.get_python_prefix())
        
        command.extend(['-c', python_statement])

        job = self._create_job(command)
        job_id = self._submit_job(job)
        
        return 'Submitted Qube job: {0}'.format(job_id)
    
    def _create_job(self, command):
        '''Create and return the Qube job for the *command*.'''
        return {
            'prototype': 'cmdline',
            'name': 'segue',
            'cpus': 1,
            'package': {
                'cmdline': ' '.join(command)
            }
        }
    
    def _submit_job(self, job):
        '''Submit the *job* to Qube.
        
        Return the job id.
        
        '''
        # Import here so that subclasses can avoid qb import if desired.
        import qb
        
        return qb.submit(job)

