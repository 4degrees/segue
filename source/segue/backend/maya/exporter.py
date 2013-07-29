# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import os
import errno
import tempfile
import operator
import json

import pymel.core


class MayaExporter(object):
    '''Export geometry from Maya.'''
    
    def __init__(self):
        '''Initialise exporter'''
        super(MayaExporter, self).__init__()
        
        # Ensure necessary plugins loaded
        if not pymel.core.pluginInfo('objExport', query=True, loaded=True):
            pymel.core.loadPlugin('objExport')
        
        if not pymel.core.pluginInfo('AbcExport', query=True, loaded=True):
            pymel.core.loadPlugin('AbcExport')
    
    def export(self, nodes, path=None, start=None, end=None, step=1):
        '''Export *nodes* for *start* - *end* frame range to *path*.
        
        *nodes* must be a list of dictionaries in the form 
        {'label':label, 'object':object} where object is the PyMel object for
        selection.
            
        *path* should be a folder in which to save the 'asset'. If not
        specified a temporary folder location will be used.
        
        *step* should specify the time interval in frames at which to sample.
        
        Return the path to the exported folder of data.
        
        '''
        if path is None:
            path = tempfile.mkdtemp('_segue')
        else:
            try:
                os.makedirs(path)
            except OSError as error:
                if error.errno != errno.EEXIST:
                    raise
        
        reference_path = os.path.join(path, 'reference.obj')
        cache_path = os.path.join(path, 'cache.abc')
        package_path = os.path.join(path, 'package.json')
        
        # Need to select nodes for export so maintain current selection if any.
        previous_selection = pymel.core.ls(selection=True)
        selection = map(operator.itemgetter('object'), nodes)
        
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
                options.append('-root {0}'.format(entry.name()))
            options.append('-frameRange {0} {1}'.format(start, end))
            options.append('-step {0}'.format(step))
            options.append('-uvWrite')
            options.append('-stripNamespaces')
            options.append('-file {0}'.format(cache_path))
            
            pymel.core.AbcExport(verbose=True, jobArg=' '.join(options))
            
            # Create package file
            package = {
                'reference': self._package_path(path, reference_path),
                'cache': self._package_path(path, cache_path)
            }
            with open(package_path, 'w') as file_:
                json.dump(package, file_)
            
        finally:
            # Revert to previous selection
            pymel.core.select(clear=True)
            pymel.core.select(previous_selection, replace=True)
        
        return path
    
    def _package_path(self, root, path):
        '''Return fragment of *path* with *root* stripped.
        
        Also, convert to generic Linux-esque format.
        
        '''
        if not root.endswith(os.sep):
            root += os.sep
        
        return path[len(root):].replace(os.sep, '/')

