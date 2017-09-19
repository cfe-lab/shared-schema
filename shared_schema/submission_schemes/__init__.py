'''Definition and export for data submission schemes.

Submission schemes are simplified subsets of the schema that collaborators can
use as a guide when submitting data. Schemes are defined as "views" onto the
schema so that names, types, and descriptions aren't duplicated.
'''

from . import exporter
from . import multi_table


SCHEMES = {
    'multi-table': multi_table.scheme,
}


def handler(args):
    scheme_name = args.scheme
    scheme = SCHEMES[scheme_name]
    path = args.dest
    exporter.export_scheme(scheme, path, skip_confirmation=args.y)
