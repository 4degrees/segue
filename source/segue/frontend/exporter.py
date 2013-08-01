# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.


from PySide import QtGui

from .selector import SelectorWidget
from .options import OptionsWidget


class ExporterWidget(QtGui.QWidget):
    '''Manage exporting.'''
    
    def __init__(self, host, processors, parent=None):
        '''Initialise with *host* application and *parent*.
        
        *processors* should be a list of
        :py:class:`~segue.backend.processor.base.Processor` instances to make
        available as processor options.
        
        '''
        super(ExporterWidget, self).__init__(parent=parent)
        self._host = None
        self._processors = None
        self.build()
        self.post_build()
        
        self.host = host
        self.set_processors(processors)
    
    @property
    def host(self):
        '''Return current host application.'''
        return self._host
    
    @host.setter
    def host(self, host):
        '''Set host application to *host*.'''
        self._host = host
        self.options_widget.host = host
        self.selector_widget.host = host
    
    def get_processors(self):
        '''Return current processors.'''
        return self.options_widget.get_processors()
    
    def set_processors(self, processors):
        '''Set processors clearing any existing ones.'''
        self.options_widget.set_processors(processors)
    
    def build(self):
        '''Build and layout the interface.'''
        self.setLayout(QtGui.QVBoxLayout())

        self.selector_widget = SelectorWidget(host=self.host)
        self.selector_widget.setFrameStyle(
            QtGui.QFrame.StyledPanel
        )
        self.layout().addWidget(self.selector_widget)
        
        self.options_widget = OptionsWidget(host=self.host)
        self.options_widget.setFrameStyle(
            QtGui.QFrame.StyledPanel
        )
        self.layout().addWidget(self.options_widget)
        
        self.export_button = QtGui.QPushButton('Export')
        self.layout().addWidget(self.export_button)
        
    def post_build(self):
        '''Perform post-build operations.'''
        self.setWindowTitle('Segue Exporter')
        
        self.selector_widget.added.connect(self.on_selection_changed)
        self.selector_widget.removed.connect(self.on_selection_changed)
        
        self.validate()
        
    def on_selection_changed(self, items):
        '''Handle selection change.'''
        self.validate()
        
    def validate(self):
        '''Validate options and update UI state.'''
        self.export_button.setEnabled(False)
        
        if not self.selector_widget.items():
            return
        
        self.export_button.setEnabled(True)

