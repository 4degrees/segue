# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import os
import sys
import argparse
import subprocess
import errno

try:
    import json
except ImportError:
    import simplejson as json


def main(arguments=None):
    '''Segue command line interface.'''
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    optimise_parser = subparsers.add_parser(
        'optimise-for', help='Optimise package.'
    )
    optimise_parser.add_argument('application', choices=['houdini'],
                                 help='Application to optimise package for.')
    optimise_parser.add_argument('package', type=_valid_package,
                                 help='Path to package file to optimise.')
    optimise_parser.set_defaults(func=optimise_for)

    namespace = parser.parse_args(arguments)
    namespace.func(namespace)


def optimise_for(namespace):
    '''Handle subcommand.'''
    if namespace.application == 'houdini':
        optimise_for_houdini(namespace.package)
        return

    raise ValueError(
        'Cannot optimise for unsupported package: {0}'
        .format(namespace.application)
    )


def optimise_for_houdini(package_path):
    '''Optimise *package* for use in Houdini by adding bgeo format.'''
    with open(package_path, 'r') as package_file:
        package = json.load(package_file)

    if 'houdini' in package:
        print 'Package already optimised for Houdini.'
        return

    start = package['start']
    stop = package['stop']

    root_path = os.path.dirname(package_path)
    bgeo_path = os.path.join(root_path, 'bgeo', '$FF.bgeo')

    try:
        os.makedirs(os.path.dirname(bgeo_path))
    except OSError as error:
        if error.errno != errno.EEXIST:
            raise

    if not root_path.endswith(os.sep):
        root_path += os.sep

    bgeo_relative_path = bgeo_path[len(root_path):].replace(os.sep, '/')

    command = [
        'hython', '-c',
        (
        'import os;'
        'import segue.backend.host.houdini;'
        'import segue;'
        'host = segue.backend.host.houdini.HoudiniHost();'
        'node = host.load_package("{0}");'
        'implementation_node = node.node("output/implementation");'
        'rop_node = implementation_node.createOutputNode("rop_geometry");'
        'rop_node.parm("sopoutput").set("{1}");'
        'rop_node.parm("trange").set(1);'
        'rop_node.parm("f1").set({2});'
        'rop_node.parm("f2").set({3});'
        'rop_node.render();'
        .format(
            package_path.replace('\\', '/'),
            bgeo_path.replace('\\', '/'),
            start, stop)
        )
    ]
    subprocess.check_call(command)

    package['houdini'] = bgeo_relative_path
    with open(package_path, 'w') as package_file:
        json.dump(package, package_file)

    print 'Optimisation succeeded.'


def _valid_package(value):
    '''Check *value* refers to a valid package.'''
    if value.endswith('package.json') and os.path.isfile(value):
        return value

    raise argparse.ArgumentTypeError(
        '{0!r} is not a valid path to a package'.format(value)
    )


# Execute command line interface.
if __name__ == '__main__':
    if '__main__.py' in sys.argv[0]:
        sys.argv[0] = 'segue'

    main(sys.argv[1:])
    raise SystemExit(0)

