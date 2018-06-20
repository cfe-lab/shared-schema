'''This module is for exporting the submission scheme'''

import csv
import pathlib
import sys

COLUMNS = 'name', 'type', 'required', 'description', 'possible values'


def format_field(field):
    return {
        'name': field.name,
        'type': field.type,
        'required': 'yes' if field.required else 'no',
        'description': field.description,
        'possible values': field.possible_values,
    }


def get_confirmation(resolved_path, files):
    hdr_msg = "The following files will be written to '{}':"
    print(hdr_msg.format(resolved_path))
    for filename in files:
        print(" {}".format(filename))
    while True:
        try:
            response = input('Proceed? (y/n): ').lower()
            if response == 'y':
                return
            elif response == 'n':
                sys.exit('Aborting')
            else:
                print("Please enter 'y' or 'n'")
        except Exception:
            print()
            sys.exit('Aborting')


def save_entity(path, ename, efields):
    filename = "{}.csv".format(ename)
    pathname = path / filename
    with pathname.open('w') as outfile:
        writer = csv.DictWriter(outfile, COLUMNS)
        for field in efields:
            writer.writerow(format_field(field))


def export_scheme(scheme, path, skip_confirmation=False):
    'Given a Dict[entity_name, List[field]], export the scheme to CSV files'

    resolved_path = pathlib.Path(path)
    if not resolved_path.exists():
        msg = "{} doesn't exist"
        sys.exit(msg.format(resolved_path))
    if not resolved_path.is_dir():
        msg = "{} isn't a directory"
        sys.exit(msg.format(resolved_path))
    if not skip_confirmation:
        get_confirmation(
            resolved_path,
            ["{}.csv".format(fname) for fname in scheme.keys()],
        )
    for ename, efields in scheme.items():
        print("Writing {}.csv".format(ename))
        save_entity(resolved_path, ename, efields)
    print("Done.")
