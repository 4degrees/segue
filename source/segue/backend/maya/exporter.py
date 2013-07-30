# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import os
import errno
import tempfile
import operator
import json

import pymel.core


def export(nodes, source=None, target=None, start=None, end=None, step=1):
    '''Export *nodes* in *source* for *start* - *end* frame range to *target*.
    
    If *source* is None, the current open scene will be used.
    
    *nodes* must be a list of entries understood by Maya for selection of
    objects (e.g. node path).
        
    *target* should be a folder in which to save the 'asset'. If not
    specified a temporary folder location will be used.
    
    *step* should specify the time interval in frames at which to sample.
    
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
        pymel.core.select(nodes, replace=True)

        # Export obj for reference (to preserve groups)
        pymel.core.exportSelected(
            reference_path, type='OBJexport', force=True,
            preserveReferences=True,
            options='groups=1;ptgroups=1;materials=0;smoothing=0;normals=1'
        )
        
        # Export alembic cache
        pymel.core.select(nodes, hierarchy=True, replace=True)
        
        options = []
        for entry in nodes:
            options.append('-root {0}'.format(entry))
        options.append('-frameRange {0} {1}'.format(start, end))
        options.append('-step {0}'.format(step))
        options.append('-uvWrite')
        options.append('-stripNamespaces')
        options.append('-file {0}'.format(cache_path))
        
        pymel.core.AbcExport(verbose=True, jobArg=' '.join(options))
        
        # Create package file
        package = {
            'reference': _package_path(target, reference_path),
            'cache': _package_path(target, cache_path)
        }
        with open(package_path, 'w') as file_:
            json.dump(package, file_)
        
    finally:
        # Revert to previous selection
        pymel.core.select(clear=True)
        pymel.core.select(previous_selection, replace=True)
    
    return target


def _package_path(root, path):
    '''Return fragment of *path* with *root* stripped.
    
    Also, convert to generic Linux-esque format.
    
    '''
    if not root.endswith(os.sep):
        root += os.sep
    
    return path[len(root):].replace(os.sep, '/')

