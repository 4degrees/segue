# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import sys

from PySide import QtGui

from segue.frontend.exporter import ExporterWidget


class Host(object):
    '''Mock host implementation.'''
    
    def get_selection(self):
        '''Return current selection.'''
        return ['|group1|objectA', '|group2|objectB', '|objectC',
                '|group3|group4|objectD']


if __name__ == '__main__':
    '''Interactively test the exporter.'''
    app = QtGui.QApplication(sys.argv)

    host = Host()
    widget = ExporterWidget(host=host)
    widget.show()
    
    raise SystemExit(app.exec_())

