# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from __future__ import absolute_import

import os
import errno
import tempfile
import operator
import json

import maya.utils
import pymel.core

from .base import Host

# Add in a mock executeInMainThreadWithResult function if not defined (as in the
# case when running Maya in batch mode).
try:
    _call = maya.utils.executeInMainThreadWithResult
except AttributeError:
    def _call(command, *args, **kw):
        '''Call *command* with *args* and *kw* and return result.'''
        return command(*args, **kw)


class MayaHost(Host):
    '''Represent Maya application.'''
    
    def get_selection(self):
        '''Return the current selection as a list of ids.'''
        selected = _call(pymel.core.ls, selection=True)
        
        items = []
        for entry in selected:
            items.append(_call(entry.fullPath))
        
        return items
    
    def get_frame_range(self):
        '''Return the current frame range as a tuple of (start, stop).'''
        return (
            _call(pymel.core.playbackOptions, query=True, minTime=True),
            _call(pymel.core.playbackOptions, query=True, maxTime=True)
        )
    
    def save(self, selection=None, source=None, target=None,
             start=None, stop=None, step=1):
        '''Export *selection* in *source* for frame range to *target*.
        
        *selection* should be a list of ids that can be used to select objects
        in the *source*. If None the result of :py:meth:`get_selection` will be
        used.
        
        *source* should be the full path to the scene file. If None, the
        current open scene will be used.
            
        *target* should be a folder in which to save the 'package'. If not
        specified a temporary folder location will be used.
        
        *start* and *stop* specify the frame range and *step* the time interval
        in frames at which to sample. If *start* and *stop* are not specified
        the range returned by :py:meth:`get_frame_range` will be used.
        
        Return the path to the exported folder of data.
        
        '''
        # Open source if provided.
        if source is not None:
            _call(pymel.core.openFile, source, force=True)
        
        # Ensure necessary plugins loaded
        if not _call(
            pymel.core.pluginInfo, 'objExport', query=True, loaded=True
        ):
            _call(pymel.core.loadPlugin, 'objExport')
        
        if not _call(
            pymel.core.pluginInfo, 'AbcExport', query=True, loaded=True
        ):
            _call(pymel.core.loadPlugin, 'AbcExport')
        
        # Check selection
        if selection is None:
            selection = self.get_selection()
            
        if not selection:
            raise ValueError('Cannot save empty selection.')
        
        # Set range
        if None in (start, stop):
            range = self.get_frame_range()
            
            if start is None:
                start = range[0]
            
            if stop is None:
                stop = range[1]
            
        # Ensure target folder exists
        if target is None:
            target = tempfile.mkdtemp('_segue')
        else:
            try:
                os.makedirs(target)
            except OSError as error:
                if error.errno != errno.EEXIST:
                    raise
        
        reference_path = os.path.join(target, 'reference.obj')
        cache_path = os.path.join(target, 'cache.abc')
        package_path = os.path.join(target, 'package.json')
        
        # Need to select nodes for export so maintain current selection if any.
        previous_selection = _call(pymel.core.ls, selection=True)
        
        try:
            _call(pymel.core.select, selection, replace=True)
    
            # Export obj for reference (to preserve groups)
            _call(pymel.core.exportSelected, 
                reference_path, type='OBJexport', force=True,
                preserveReferences=True,
                options='groups=1;ptgroups=1;materials=0;smoothing=0;normals=1'
            )
            
            # Export alembic cache
            _call(pymel.core.select, selection, hierarchy=True, replace=True)
            
            options = []
            for entry in selection:
                options.append('-root {0}'.format(entry))
            options.append('-frameRange {0} {1}'.format(start, stop))
            options.append('-step {0}'.format(step))
            options.append('-uvWrite')
            options.append('-stripNamespaces')
            options.append('-file {0}'.format(cache_path))
            
            _call(pymel.core.AbcExport, verbose=True, jobArg=' '.join(options))
            
            # Create package file
            package = {
                'reference': self._package_path(target, reference_path),
                'cache': self._package_path(target, cache_path)
            }
            with open(package_path, 'w') as file_:
                json.dump(package, file_)
            
        finally:
            # Revert to previous selection
            _call(pymel.core.select, clear=True)
            _call(pymel.core.select, previous_selection, replace=True)
        
        return target
    