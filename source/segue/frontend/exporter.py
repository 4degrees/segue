# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import traceback

from PySide import QtGui

from .selector import SelectorWidget
from .options import OptionsWidget
from .worker import Worker
from ..backend.processor.foreground import ForegroundProcessor


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
        
        self.progress_bar = QtGui.QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.layout().addWidget(self.progress_bar)
        self.progress_bar.hide()
        
    def post_build(self):
        '''Perform post-build operations.'''
        self.setWindowTitle('Segue Exporter')
        
        self.selector_widget.added.connect(self.validate)
        self.selector_widget.removed.connect(self.validate)
        self.options_widget.processor_widget.currentIndexChanged.connect(
            self.validate
        )
        self.options_widget.target_widget.textChanged.connect(self.validate)
        
        self.export_button.clicked.connect(self.export)
        
        self.validate()
        
    def validate(self, *args, **kw):
        '''Validate options and update UI state.'''
        self.export_button.setEnabled(False)
        
        if not self.selector_widget.items():
            return
        
        processor = self.options_widget.processor_widget.itemData(
            self.options_widget.processor_widget.currentIndex()
        )
        if processor is None:
            return
        
        target = self.options_widget.target_widget.text()
        if not target:
            return
        
        self.export_button.setEnabled(True)
    
    def export(self):
        '''Perform export according to set options.'''
        processor = self.options_widget.processor_widget.itemData(
            self.options_widget.processor_widget.currentIndex()
        )
        
        self.export_button.hide()
        self.progress_bar.setRange(0, 0) # Indeterminate
        self.progress_bar.show()
        
        options = {
            'source': None,
            'selection': self.selector_widget.items(),
            'target': self.options_widget.target_widget.text(),
            'start': self.options_widget.start_frame_widget.value(),
            'stop': self.options_widget.stop_frame_widget.value(),
            'step': self.options_widget.step_frame_widget.value()
        }
        
        # TODO: Can this be decoupled?
        if not isinstance(processor, ForegroundProcessor):
            temporary_file = self.host.save()
            options['source'] = temporary_file
        
        command = [self.host.save_package, None, options]
        
        try:
            worker = Worker(processor.process, command)
            worker.start()
          
            while worker.isRunning():
                app = QtGui.QApplication.instance()
                app.processEvents()
      
            if worker.error:
                raise worker.error[1], None, worker.error[2]
             
        except Exception as error:
            traceback.print_exc()
            QtGui.QMessageBox.critical(
                self,
                'Process failed',
                'Could not export selection!'
                '\n{0}'.format(error)
            )
        
        else:
            QtGui.QMessageBox.information(
                self,
                'Process completed',
                'Selection exported successfully!'
                '\n{0}'.format(worker.result or '') 
            )
        finally:
            self.progress_bar.setMaximum(1)
            self.progress_bar.reset()
            self.progress_bar.hide()
            self.export_button.show()

