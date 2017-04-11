import sys

import schema.dot as dot
import schema.data as data


def generate():
    cmd = sys.argv[1]

    if cmd == "dot":
        out = dot.make(data.schema_data, "SHARED Schema")
        print(out)
        sys.exit(0)
    else:
        print("Unknown command '{}'".format(cmd))
        sys.exit(1)


if __name__ == "__main__":
    generate()
