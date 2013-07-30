# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.


from PySide import QtGui

from .selector import SelectorWidget


class ExporterWidget(QtGui.QWidget):
    '''Manage exporting.'''
    
    def __init__(self, host, parent=None):
        '''Initialise with *host* application and *parent*.'''
        super(ExporterWidget, self).__init__(parent=parent)
        self.host = host
        self.build()
        self.post_build()
        
    def build(self):
        '''Build and layout the interface.'''
        self.setLayout(QtGui.QVBoxLayout())
        
        self.selector_widget = SelectorWidget(host=self.host)
        self.layout().addWidget(self.selector_widget)
        
        self.options_widget = QtGui.QWidget()
        self.layout().addWidget(self.options_widget)
        
        self.export_button = QtGui.QPushButton('Export')
        self.layout().addWidget(self.export_button)
        
    def post_build(self):
        '''Perform post-build operations.'''
        self.setWindowTitle('Segue Exporter')
        