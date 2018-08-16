"""This module defines the datatypes in the SHARED schema.
"""

import enum

# NOTE(nknight): MyPy doesn't support keyword args for namedtuples. See mypy
# issue 4184: https://github.com/python/mypy/issues/4184

Datatype = enum.Enum(  # type: ignore
    "Datatype",
    [
        "INTEGER",
        "FLOAT",
        "STRING",
        "DATE",
        "UUID",
        "BOOL",
        "ENUM",
        "FOREIGN_KEY",
    ],
    module=__name__,
)

TYPE_MAP = {dt.name.lower(): dt for dt in Datatype}


def classify(src):
    if type(src) is not str:
        msg = "Expecting a string, but got '{}' instead"
        raise ValueError(msg.format(src))
    normed_src = src.lower().strip()
    if normed_src in TYPE_MAP:
        # covers everything except ENUM and FOREIGN_KEY
        return TYPE_MAP.get(normed_src)
    if normed_src.startswith("enum"):
        return Datatype.ENUM
    if normed_src.startswith("foreign key"):
        return Datatype.FOREIGN_KEY
    else:
        msg = "Can't parse a datatype from '{}'"
        raise ValueError(msg.format(src))
