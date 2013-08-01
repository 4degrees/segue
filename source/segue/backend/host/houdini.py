# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import os
try:
    import json
except ImportError:
    import simplejson as json

import hou

from .base import Host


class HoudiniHost(Host):
    '''Represent Houdini application.'''
    
    def load(self, package, target=None):
        '''Load *package* onto *target*.
        
        If *target* not specified create an appropriate parent node.
        
        '''
        if target is None:
            target = hou.node('/obj').createNode('uk.ltd.4degrees::segue')
            target.parm('package').set(str(package))
        
        # Clear children
        for child in target.children():
            child.destroy()
        
        # Load package file
        package_path = target.evalParm('package')
        if not os.path.isfile(package_path):
            return
        
        with open(package_path, 'r') as package_file:
            package = json.load(package_file)
        
        cache_relative_path = package.get('cache')
        if not cache_relative_path:
            raise ValueError('No cache specified in package.')
        
        reference_relative_path = package.get('reference')
        if not reference_relative_path:
            raise ValueError('No reference specified in package.')
        
        package_root_path = os.path.abspath(os.path.dirname(package_path))
        cache_path = os.path.join(package_root_path, cache_relative_path)
        reference_path = os.path.join(package_root_path,
                                      reference_relative_path)
        
        # TODO: Check for 'houdini' attribute which will be bgeo. If found, use
        # that instead.
        
        # Create Alembic archive
        alembic_node = target.createNode('alembicarchive', 'cache')
        alembic_node.parm('fileName').set(str(cache_path))
        alembic_node.parm('loadmode').set('houdini')
        alembic_node.parm('buildHierarchy').pressButton()
        
        # Merge Alembic geometry in order to map onto reference object.
        geometry_nodes = []
        for child in alembic_node.allSubChildren():
            if child.type().name() == 'geo':
                geometry_nodes.append(child)
        
        geometry_node = target.createNode('geo', 'output')
        merge_node = geometry_node.createNode('object_merge', 'cache')
        merge_node.parm('xformtype').set(1) # Into This Object
        merge_node.parm('numobj').set(len(geometry_nodes))
        
        for index, entry in enumerate(geometry_nodes):
            parameter_name = 'objpath{0}'.format(index + 1)
            merge_node.parm(parameter_name).set(entry.path())
        
        # Read in reference object
        reference_node = geometry_node.node('file1')
        reference_node.setName('reference')
        reference_node.parm('file').set(str(reference_path))
        
        # Map Alembic animation onto reference geometry
        point_node = reference_node.createOutputNode('point', 'map_points')
        point_node.setInput(1, merge_node)
        
        # Point positions
        point_node.parm('tx').setExpression('$TX2')
        point_node.parm('ty').setExpression('$TY2')
        point_node.parm('tz').setExpression('$TZ2')
        
        # Point normals
        point_node.parm('donml').set(1)
        point_node.parm('nx').setExpression('$NX2')
        point_node.parm('ny').setExpression('$NY2')
        point_node.parm('nz').setExpression('$NZ2')
        
        # Vertex normals
        vertex_node = point_node.createOutputNode('vertex',
                                                  'map_vertex_normals')
        vertex_node.setInput(1, merge_node)
        
        vertex_node.parm('donormal').set(1)
        vertex_node.parm('normalx').setExpression('$NX2')
        vertex_node.parm('normaly').setExpression('$NY2')
        vertex_node.parm('normalz').setExpression('$NZ2')
        
        # Fix normals
        facet_node = vertex_node.createOutputNode('facet', 'fix_normals')
        facet_node.parm('prenml').set(1)
        
        # Group
        group_node = facet_node.createOutputNode('group', 'output')
        
        alembic_node.setDisplayFlag(0)    
        group_node.setDisplayFlag(1)
        
        # Layout
        geometry_node.layoutChildren()
        target.layoutChildren()

