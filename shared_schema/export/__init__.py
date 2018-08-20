"""An interface for exporting the schema in different formats

This module contains several submodules that know how to export the schema in
different formats (e.g. as CSV). They each define a function that accespts the
schema and returns the output as a printable. This module contains a directory
of available formats (in FORMAT) and takes care of selecting the appropriate
function, calling it, and printing the result.
"""

import shared_schema
from shared_schema import data

from . import csv, dot, erd, rst

FORMATS = {"csv": csv.make, "dot": dot.make, "rst": rst.make, "erd": erd.make}


def handler(args):
    maker = FORMATS[args.format]
    outp = maker(
        schema_data=data.schema_data, version=shared_schema.__version__
    )
    print(outp)
