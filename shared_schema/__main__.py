import argparse

import shared_schema.exporter


DESC = '''Describe the SHARED project's database schema and related
information in various formats.'''


parser = argparse.ArgumentParser(
    prog='python -m shared_schema',
    description=DESC,
)
parser.set_defaults(handler=lambda _: parser.print_help())


subparsers = parser.add_subparsers(title='commands', )


exporter = subparsers.add_parser(
    name='export',
    help='Print the schema in various formats',
)
exporter.add_argument(
    'format',
    choices=shared_schema.exporter.FORMATS.keys(),
    help='The format to print the schema in',
)
exporter.set_defaults(handler=shared_schema.exporter.handler)


if __name__ == "__main__":
    args = parser.parse_args()
    args.handler(args)
