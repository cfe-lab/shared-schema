'''This module lists standard treatments and their contents

There's a grammar for the way treatment regimens are defined, a list of
compounds that may be included in treatment regimens, and a list of standard
treatment regimens based on drug labels from the US FDA.
'''

import csv
import sys

from . import grammar  # noqa
from . import standard  # noqa
from . import cannonical  # noqa


def _print_table(keys, rows):
    display_keys = [k.capitalize() for k in keys]
    writer = csv.DictWriter(
        sys.stdout,
        display_keys,
    )
    writer.writeheader()
    for row in rows:
        rowdict = dict(zip(display_keys, row))
        writer.writerow(rowdict)


TABLES = {
    'regimens': (standard.regimen_keys, standard.regimens),
    'compounds': (standard.compound_keys, standard.compounds),
    'frequencies': (standard.freq_keys, standard.freqs),
}


def handler(args):
    '''Print the desired information to standard output'''
    table = args.table
    keys, rows = TABLES[table]
    _print_table(keys, rows.items())
