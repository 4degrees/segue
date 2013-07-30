# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import sys

from PySide import QtGui

from segue.frontend.exporter import ExporterWidget


if __name__ == '__main__':
    '''Interactively test the exporter.'''
    app = QtGui.QApplication(sys.argv)

    widget = ExporterWidget()
    widget.show()
    
    raise SystemExit(app.exec_())

