import sys

import schema.csv as csv
import schema.dot as dot
import schema.data as data
import schema.index as index


def generate():
    cmd = sys.argv[1]

    if cmd == "dot":
        out = dot.make(data.schema_data, "SHARED Schema")
        print(out)
        sys.exit(0)
    elif cmd == "index":
        out = index.make(data.schema_data)
        print(out)
        sys.exit(0)
    elif cmd == "csv":
        out = csv.make(data.schema_data)
        print(out)
        sys.exit(0)
    else:
        print("Unknown command '{}'".format(cmd))
        sys.exit(1)


if __name__ == "__main__":
    generate()
