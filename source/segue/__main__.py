# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import sys


def main(arguments=None):
    '''Segue command line interface.'''


if __name__ == '__main__':
    '''Execute command line interface.'''
    if '__main__.py' in sys.argv[0]:
        sys.argv[0] = 'segue'

    raise SystemExit(int(main() is False))

