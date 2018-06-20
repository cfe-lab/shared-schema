import argparse

import shared_schema.exporter
import shared_schema.regimens as regimens
import shared_schema.submission_scheme as submission_scheme

DESC = '''Describe the SHARED project's database schema and related
information in various formats.'''

parser = argparse.ArgumentParser(
    prog='python -m shared_schema',
    description=DESC,
)
parser.set_defaults(handler=lambda _: parser.print_help())

subparsers = parser.add_subparsers(title='commands')

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

submission_scheme_exporter = subparsers.add_parser(
    name='sub-scm',
    help='Export submission scheme data',
)
submission_scheme_exporter.add_argument(
    'dest',
    help='The path to save scheme description files at',
)
submission_scheme_exporter.add_argument(
    '-y',
    action='store_true',
    help='Skip confirmation prompt',
)
submission_scheme_exporter.set_defaults(handler=submission_scheme.handler)

regimens_exporter = subparsers.add_parser(
    name='regimens',
    help='Export treatment regimens',
)
regimens_exporter.add_argument(
    'table',
    choices=regimens.TABLES.keys(),
    help="The regimen data table to export",
)
regimens_exporter.set_defaults(handler=regimens.handler)

# TODO(nknight): add a `version` command (using argparse's version action)

if __name__ == "__main__":
    args = parser.parse_args()
    args.handler(args)
