'''This module lists standard treatments and their contents

There's a grammar for the way treatment regimens are defined, a list of
compounds that may be included in treatment regimens, and a list of standard
treatment regimens based on drug labels from the US FDA.
'''

import csv
import sys

from . import standard


def format_row(row):
    'Capitalize keys so we can display them'
    return {k.capitalize(): v for k, v in row.items()}


def _print_table(keys, rows):
    display_keys = [k.capitalize() for k in keys]
    writer = csv.DictWriter(
        sys.stdout,
        display_keys,
    )
    for row in rows:
        writer.writerow(format_row(row))


TABLES = {
    'regimens': (standard._regimen_keys, standard.regimens),
    'compounds': (standard._compound_keys, standard.compounds),
}


def handler(args):
    '''Print the desired information to standard output'''
    table = args.table
    keys, rows = TABLES[table]
    _print_table(keys, rows)
