import sys

import shared_schema
import shared_schema.csv as csv
import shared_schema.dot as dot
import shared_schema.data as data
import shared_schema.html as html
import shared_schema.tex as tex


def do_make(maker, *args):
    out = maker(*args)
    print(out)
    sys.exit()

def generate():
    cmd = sys.argv[1]

    if cmd == 'dot':
        do_make(dot.make, data.schema_data, "SHARED Schema")
    elif cmd == 'html':
        do_make(html.make, data.schema_data, schema.__version__)
    elif cmd == 'csv':
        do_make(csv.make, data.schema_data)
    elif cmd == 'tex':
        do_make(tex.make, data.schema_data, schema.__version__)
    else:
        print("Unknown command '{}'".format(cmd))
        print()
        print("Usage: python -m shared_schema <command>")
        print("Commands:")
        for cmd in ["csv", "dot", "html", "tex"]:
            print(" - {}".format(cmd))
        print()
        sys.exit(1)


if __name__ == "__main__":
    generate()
