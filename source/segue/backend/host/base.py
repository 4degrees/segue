# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import os


class Host(object):
    '''Represent a host application.'''
    
    def __init__(self, name=None):
        '''Initialise host with a *name*.'''
        super(Host, self).__init__()
        self.name = name
        if self.name is None:
            self.name = self.__class__.__name__.lower()
    
    def get_python_prefix(self):
        '''Return Python executable prefix as a list.'''
        return ['python']
    
    def get_selection(self):
        '''Return the current selection as a list of ids.'''
        raise NotImplementedError()
    
    def get_frame_range(self):
        '''Return the current frame range as a tuple of (start, stop).'''
        raise NotImplementedError()

    def get_current_frame(self):
        '''Return the current frame.'''
        raise NotImplementedError()
    
    def save(self, target=None):
        '''Save current scene to *target*.
        
        If *target* is not specified will use a temporary file.
        
        Return the saved file path.
        
        '''
        raise NotImplementedError()
    
    def save_package(self, selection=None, source=None, target=None,
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
        raise NotImplementedError()
    
    def load_package(self, package, target=None):
        '''Load *package* onto *target*.
        
        If *target* not specified create an appropriate parent node.

        Return target node.

        '''
        raise NotImplementedError()
    
    def _package_path(self, root, path):
        '''Return fragment of *path* with *root* stripped.
        
        Also, convert to generic Linux-esque format.
        
        '''
        if not root.endswith(os.sep):
            root += os.sep
        
        return path[len(root):].replace(os.sep, '/')

