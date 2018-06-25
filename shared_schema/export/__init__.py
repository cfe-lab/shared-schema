'''An interface for expirting the schema in different formats

Each module that knows how to export the schema (e.g. to
ReSTructuredText, LaTeX, HTML, etc.) defines a function to do produce
the output. This module lists the available functions and handles
passing in the schema and doing any IO.
'''
import shared_schema
from shared_schema import data

from . import csv, dot, rst

FORMATS = {'csv': csv.make, 'dot': dot.make, 'rst': rst.make}


def handler(args):
    maker = FORMATS[args.format]
    outp = maker(
        schema_data=data.schema_data,
        version=shared_schema.__version__,
    )
    print(outp)
