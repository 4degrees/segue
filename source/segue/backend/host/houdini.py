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
    
    def get_python_prefix(self):
        '''Return Python executable prefix as a list.'''
        return ['hython']
    
    def load_package(self, package, target=None):
        '''Load *package* onto *target*.
        
        If *target* not specified create an appropriate parent node.

        Return target node.

        '''
        if target is None:
            target = hou.node('/obj').createNode('Segue')
            target.parm('package').set(str(package))
        
        # Clear children
        for child in target.children():
            child.destroy()
        
        # Load package file
        package_path = target.evalParm('package')
        if not os.path.isfile(package_path):
            raise ValueError('Not a valid package: {0}'.format(package_path))

        with open(package_path, 'r') as package_file:
            package = json.load(package_file)

        package_root_path = os.path.abspath(os.path.dirname(package_path))

        # Create final output geometry node.
        output_geometry_node = target.createNode('geo', 'output')
        output_geometry_node.node('file1').destroy()
        switch_node = output_geometry_node.createNode(
            'switch', 'implementation'
        )

        # Construct default obj + abc implementation.
        cache_relative_path = package.get('cache')
        if not cache_relative_path:
            raise ValueError('No cache specified in package.')
        
        reference_relative_path = package.get('reference')
        if not reference_relative_path:
            raise ValueError('No reference specified in package.')
        
        cache_path = os.path.join(package_root_path, cache_relative_path)
        reference_path = os.path.join(package_root_path,
                                      reference_relative_path)

        # Create obj + abc output container
        obj_abc_geometry_node = target.createNode('geo', 'obj-abc')

        # Read in reference object
        reference_node = obj_abc_geometry_node.node('file1')
        reference_node.setName('reference')
        reference_node.parm('file').set(str(reference_path))

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
        
        merge_node = obj_abc_geometry_node.createNode(
            'object_merge', 'cache'
        )
        merge_node.parm('xformtype').set(1) # Into This Object

        # Merge must happen in same order as reference object setup.
        # TODO: Is there a better way rather than relying on brittle naming?
        # First identify all geo in cache by container name to match against
        # primitive group in reference object.
        geometry_node_containers = {}
        for geometry_node in geometry_nodes:
            path = geometry_node.path()
            container = path.split('/')[-2]
            existing = geometry_node_containers.get(container)
            if existing is not None:
                raise ValueError(
                    'Unsupported duplicate container name in hierarchy '
                    'detected: {0} (from "{1}" and "{2}")'
                    .format(container, path, existing.path())
                )

            geometry_node_containers[container] = geometry_node

        # Filter primitive groups to only include those that match geometry
        # whilst maintaining ordering.
        primitive_group_names = []
        for primitive_group in reference_node.geometry().primGroups():
            name = primitive_group.name()
            if name in geometry_node_containers:
                primitive_group_names.append(name)

        # Now apply merge maintaining correct ordering.
        merge_node.parm('numobj').set(len(primitive_group_names))
        for index, name in enumerate(primitive_group_names):
            parameter_name = 'objpath{0}'.format(index + 1)
            geometry_node = geometry_node_containers[name]
            merge_node.parm(parameter_name).set(geometry_node.path())

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

        # Flags
        reference_node.setRenderFlag(0)
        alembic_node.setDisplayFlag(0)
        group_node.setDisplayFlag(1)
        obj_abc_geometry_node.setDisplayFlag(0)

        # Layout
        obj_abc_geometry_node.layoutChildren()

        # Connect to switch.
        obj_abc_merge_node = output_geometry_node.createNode(
            'object_merge', 'obj-abc'
        )
        obj_abc_merge_node.parm('xformtype').set(1)  # Into This Object
        obj_abc_merge_node.parm('numobj').set(1)
        obj_abc_merge_node.parm('objpath1').set(
            obj_abc_geometry_node.path()
        )

        switch_node.setNextInput(obj_abc_merge_node)

        # Load and switch to bgeo version if available.
        bgeo_relative_path = package.get('bgeo')

        if bgeo_relative_path is None:
            # Backwards compatibility.
            bgeo_relative_path = package.get('houdini')

        if bgeo_relative_path is not None:
            bgeo_path = os.path.join(package_root_path, bgeo_relative_path)

            bgeo_geometry_node = target.createNode('geo', 'bgeo')
            file_node = bgeo_geometry_node.node('file1')
            file_node.setName('output')
            file_node.parm('file').set(str(bgeo_path))

            # Flags
            bgeo_geometry_node.setDisplayFlag(0)

            # Layout
            bgeo_geometry_node.layoutChildren()

            # Connect to switch.
            bgeo_merge_node = output_geometry_node.createNode(
                'object_merge', 'bgeo'
            )
            bgeo_merge_node.parm('xformtype').set(1)  # Into This Object
            bgeo_merge_node.parm('numobj').set(1)
            bgeo_merge_node.parm('objpath1').set(
                bgeo_geometry_node.path()
            )

            switch_node.setNextInput(bgeo_merge_node)
            switch_node.parm('input').set(1)

        # Layout
        output_geometry_node.layoutChildren()
        target.layoutChildren()
        return target
