# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.


from PySide import QtGui, QtCore

from . import icon


class SelectorWidget(QtGui.QFrame):
    '''Manage selection of nodes.'''
    
    added = QtCore.Signal(list)
    removed = QtCore.Signal(list)

    def __init__(self, host, parent=None):
        '''Initialise with *host* application and *parent*.
        
        *host* should provide a get_selection() method that returns the current
        selection as a list of strings.
        
        '''
        super(SelectorWidget, self).__init__(parent=parent)
        self.host = host
        self.build()
        self.post_build()
        
    def build(self):
        '''Build and layout the interface.'''
        self.setLayout(QtGui.QGridLayout())
        
        self.list_widget = QtGui.QListWidget()
        self.list_widget.setSelectionMode(
            QtGui.QAbstractItemView.ExtendedSelection
        )
        self.layout().addWidget(self.list_widget, 0, 0, 3, 1)
        
        self.add_button = QtGui.QPushButton()
        self.add_button.setToolTip('Select items in application and click to '
                                   'add them to the list.')
        self.add_button.setIcon(QtGui.QPixmap(':icon_plus'))

        self.layout().addWidget(self.add_button, 0, 1)
        
        self.remove_button = QtGui.QPushButton()
        self.remove_button.setToolTip('Select items in the list and click to '
                                      'remove them.')
        self.remove_button.setIcon(QtGui.QPixmap(':icon_minus'))
        self.layout().addWidget(self.remove_button, 1, 1)
        
        self.layout().setRowStretch(2, 1)
        self.layout().setColumnStretch(0, 1)
        
    def post_build(self):
        '''Perform post-build operations.'''
        self.add_button.clicked.connect(self._on_add)
        self.remove_button.clicked.connect(self._on_remove)
    
    def items(self):
        '''Return current items.'''
        items = []
        for index in range(self.list_widget.count()):
            items.append(self.list_widget.item(index).text())
        
        return items
    
    def _on_add(self):
        '''Handle selection addition.'''
        items = self.host.get_selection()
        self.add(items)
        
    def _on_remove(self):
        '''Handle selection removal.'''
        selected = self.list_widget.selectedItems()
        items = []
        for entry in selected:
            items.append(entry.text())
        self.remove(items)
    
    def _find(self, item):
        '''Find *item* and return corresponding row.
        
        If not matched return None.
        
        '''
        matches = self.list_widget.findItems(
            item,
            QtCore.Qt.MatchFixedString & QtCore.Qt.CaseSensitive
        )
        
        if matches:
            return self.list_widget.row(matches[0])
        
        else:
            return None
    
    def add(self, items):
        '''Add *items* to selection.'''
        added = []
        for item in items:
            row = self._find(item)
            if row is None:
                self.list_widget.addItem(item)
                added.append(item)
        
        self.added.emit(added)
        return added
    
    def remove(self, items):
        '''Remove *items* from selection.'''
        removed = []
        for item in items:
            row = self._find(item)
            if row is not None:
                list_item = self.list_widget.takeItem(row)
                del list_item
                removed.append(item)
        
        self.removed.emit(removed)
        return removed

