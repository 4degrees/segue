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
        'optimise-for',
        help='Optimise package. (Deprecated: Use add-format instead)'
    )
    optimise_parser.add_argument('application', choices=['houdini'],
                                 help='Application to optimise package for.')
    optimise_parser.add_argument('package', type=_valid_package,
                                 help='Path to package file to optimise.')
    optimise_parser.set_defaults(func=optimise_for)

    add_format_parser = subparsers.add_parser(
        'add-format', help='Add additional format to package.'
    )
    add_format_parser.add_argument('format', choices=['bgeo'],
                                 help='Format to add to package.')
    add_format_parser.add_argument('package', type=_valid_package,
                                 help='Path to package file to optimise.')
    add_format_parser.set_defaults(func=add_format)

    namespace = parser.parse_args(arguments)
    namespace.func(namespace)


def add_format(namespace):
    '''Handle subcommand.'''
    if namespace.format == 'bgeo':
        add_bgeo_format(namespace.package)
        return

    raise ValueError(
        'Cannot add unsupported format "{0}" to package.'
        .format(namespace.format)
    )


def add_bgeo_format(package_path):
    '''Add bgeo format to *package*.'''
    with open(package_path, 'r') as package_file:
        package = json.load(package_file)

    # Upgrade old package.
    if 'houdini' in package:
        package['bgeo'] = package['houdini']
        del package['houdini']

        with open(package_path, 'w') as package_file:
            json.dump(package, package_file)

        print 'Package already contains bgeo format.'
        return

    if 'bgeo' in package:
        print 'Package already contains bgeo format.'
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

    package['bgeo'] = bgeo_relative_path
    with open(package_path, 'w') as package_file:
        json.dump(package, package_file)

    print 'Addition of bgeo format succeeded.'


def optimise_for(namespace):
    '''Handle subcommand.'''
    if namespace.application == 'houdini':
        add_bgeo_format(namespace.package)
        return

    raise ValueError(
        'Cannot optimise for unsupported package: {0}'
        .format(namespace.application)
    )


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

