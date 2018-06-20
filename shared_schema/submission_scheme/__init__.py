'''Definition and export for the data submission scheme.

The submission scheme is a simplified version of the schema that collaborators
can use as a guide when submitting data, and SHARED can use as a target while
normalising contributed data. Many fields in the submission scheme are derived
directly from the schema, so that names, types, and descriptions aren't
duplicated.
'''

from . import exporter, simple


def handler(args):
    path = args.dest
    exporter.export_scheme(simple.scheme, path, skip_confirmation=args.y)
