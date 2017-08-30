import argparse

import shared_schema
import shared_schema.csv as csv
import shared_schema.dot as dot
import shared_schema.data as data
import shared_schema.html as html
import shared_schema.tex as tex


FORMATS = {
    'csv': csv.make,
    'dot': dot.make,
    'html': html.make,
    'tex': tex.make,
}


parser = argparse.ArgumentParser(
    prog='python -m shared_schema',
    description='Print shared schema in various formats',
)
parser.add_argument(
    'format',
    choices=FORMATS.keys(),
    help='The format to export the schema in'
)


def main():
    args = parser.parse_args()
    maker = FORMATS[args.format]
    outp = maker(
        schema_data=data.schema_data,
        version=shared_schema.__version__,
    )
    print(outp)
