# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import os
import errno
import tempfile
import operator
import json

import pymel.core

from .base import Host


class MayaHost(Host):
    '''Represent Maya application.'''
    
    def get_selection(self):
        '''Return the current selection as a list of ids.'''
        selected = pymel.core.ls(selection=True)
        
        items = []
        for entry in selected:
            items.append(entry.fullPath())
        
        return items
    
    def get_frame_range(self):
        '''Return the current frame range as a tuple of (start, stop).'''
        return (
            pymel.core.playbackOptions(query=True, minTime=True),
            pymel.core.playbackOptions(query=True, maxTime=True)
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
            pymel.core.openFile(source, force=True)
        
        # Ensure necessary plugins loaded
        if not pymel.core.pluginInfo('objExport', query=True, loaded=True):
            pymel.core.loadPlugin('objExport')
        
        if not pymel.core.pluginInfo('AbcExport', query=True, loaded=True):
            pymel.core.loadPlugin('AbcExport')
        
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
        previous_selection = pymel.core.ls(selection=True)
        
        try:
            pymel.core.select(selection, replace=True)
    
            # Export obj for reference (to preserve groups)
            pymel.core.exportSelected(
                reference_path, type='OBJexport', force=True,
                preserveReferences=True,
                options='groups=1;ptgroups=1;materials=0;smoothing=0;normals=1'
            )
            
            # Export alembic cache
            pymel.core.select(selection, hierarchy=True, replace=True)
            
            options = []
            for entry in selection:
                options.append('-root {0}'.format(entry))
            options.append('-frameRange {0} {1}'.format(start, stop))
            options.append('-step {0}'.format(step))
            options.append('-uvWrite')
            options.append('-stripNamespaces')
            options.append('-file {0}'.format(cache_path))
            
            pymel.core.AbcExport(verbose=True, jobArg=' '.join(options))
            
            # Create package file
            package = {
                'reference': self._package_path(target, reference_path),
                'cache': self._package_path(target, cache_path)
            }
            with open(package_path, 'w') as file_:
                json.dump(package, file_)
            
        finally:
            # Revert to previous selection
            pymel.core.select(clear=True)
            pymel.core.select(previous_selection, replace=True)
        
        return target
    