'''An interface for expirting the schema in different formats

Each module that knows how to export the schema (e.g. to
ReSTructuredText, LaTeX, HTML, etc.) defines a function to do produce
the output. This module lists the available functions and handles
passing in the schema and doing any IO.
'''

import shared_schema
import shared_schema.csv as csv
import shared_schema.data as data
import shared_schema.dot as dot
import shared_schema.html as html
import shared_schema.rst as rst
import shared_schema.tex as tex


FORMATS = {
    'csv': csv.make,
    'dot': dot.make,
    'html': html.make,
    'tex': tex.make,
    'rst': rst.make
}


def handler(args):
    maker = FORMATS[args.format]
    outp = maker(
        schema_data=data.schema_data,
        version=shared_schema.__version__,
    )
    print(outp)
