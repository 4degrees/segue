# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.


from PySide import QtGui, QtCore


class OptionsWidget(QtGui.QFrame):
    '''Manage export options.'''
    
    def __init__(self, host, parent=None):
        '''Initialise with *host* application and *parent*.'''
        super(OptionsWidget, self).__init__(parent=parent)
        self.host = host
        self.build()
        self.post_build()
        
    def build(self):
        '''Build and layout the interface.'''
        self.setLayout(QtGui.QGridLayout())
        
        self.frame_range_label = QtGui.QLabel('Range')
        self.layout().addWidget(self.frame_range_label, 0, 0)
        
        self.frame_range_combobox = QtGui.QComboBox()
        self.layout().addWidget(self.frame_range_combobox, 0, 1)
        
        self.frame_range_group = QtGui.QFrame()
        self.frame_range_group.setLayout(QtGui.QHBoxLayout())
        self.frame_range_group.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.frame_range_group, 1, 1)
        
        self.start_frame_widget = QtGui.QLineEdit()
        self.start_frame_label = QtGui.QLabel('Start')
        self.start_frame_label.setBuddy(self.start_frame_widget)
        self.frame_range_group.layout().addWidget(self.start_frame_label)
        self.frame_range_group.layout().addWidget(self.start_frame_widget)
        
        self.stop_frame_widget = QtGui.QLineEdit()
        self.end_frame_label = QtGui.QLabel('End')
        self.end_frame_label.setBuddy(self.stop_frame_widget)
        self.frame_range_group.layout().addWidget(self.end_frame_label)
        self.frame_range_group.layout().addWidget(self.stop_frame_widget)

        self.step_frame_widget = QtGui.QLineEdit()
        self.step_frame_label = QtGui.QLabel('Step')
        self.step_frame_label.setBuddy(self.step_frame_widget)
        self.frame_range_group.layout().addWidget(self.step_frame_label)
        self.frame_range_group.layout().addWidget(self.step_frame_widget)

        self.dispatcher_widget = QtGui.QComboBox()
        self.dispatcher_label = QtGui.QLabel('Process')
        self.dispatcher_label.setBuddy(self.dispatcher_widget)
        self.layout().addWidget(self.dispatcher_label, 2, 0)
        self.layout().addWidget(self.dispatcher_widget, 2, 1)
                
    def post_build(self):
        '''Perform post-build operations.'''
        self.step_frame_widget.setText('1.0')
        self.start_frame_widget.setText('1.0')
        self.stop_frame_widget.setText('24.0')
        
        self.frame_range_combobox.currentIndexChanged.connect(
            self.on_select_range
        )
        
        self.frame_range_combobox.addItem('Set Manually', 'manual')
        try:
            self.host.get_frame_range()
        except NotImplementedError:
            pass
        else:
            self.frame_range_combobox.addItem('Set From Time Slider', 'auto')
            self.frame_range_combobox.setCurrentIndex(
                self.frame_range_combobox.count() - 1
            )
        
    def on_select_range(self, index):
        '''Handle choice of range options.'''
        option = self.frame_range_combobox.itemData(index)
        if option == 'auto':
            for control in (self.start_frame_widget, self.stop_frame_widget):
                control.setEnabled(False)
                
            start, stop = self.host.get_frame_range()
            self.start_frame_widget.setText(str(start))
            self.stop_frame_widget.setText(str(stop))
            
        else:
            for control in (self.start_frame_widget, self.stop_frame_widget):
                control.setEnabled(True)
            
        