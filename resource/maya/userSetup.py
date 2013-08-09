# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import maya.utils as utils
import pymel.core


def setup():
    '''Configure Segue and add to a default menu.'''
    pymel.core.menu(
        label='Segue',
        tearOff=True,
        parent='MayaWindow'
    )
    
    pymel.core.menuItem(
        label='Geometry Exporter',
        command='''
            import segue.frontend.exporter
            import segue.backend.host.maya
            import segue
            
            processors = segue.discover_processors()
            host = segue.backend.host.maya.MayaHost()
            exporter = segue.frontend.exporter.ExporterWidget(
                host=host, processors=processors
            )
            
            exporter.show()
        '''.replace('            ', '')
    )

# Run setup
utils.executeDeferred(setup)

