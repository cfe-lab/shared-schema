"""Export the database schema in a format suitable for `erviz` to compile

Information about `erviz` can be found at:

    http://slopjong.de/2011/02/26/whats-erviz/
"""

import io
import typing as ty

import shared_schema.tables as tables


def field_def(fld: tables.Field) -> str:
    "Construct the field definition for a single entity field."
    meta = fld.meta
    reqd = "*" if "required" in meta.get("tags", set()) else " "
    fk = "*" if "foreign key" in fld.type else ""
    return " {reqd}{name}{fk}".format(reqd=reqd, name=fld.name, fk=fk)


def table_def(tbl: tables.Entity) -> ty.List[str]:
    "Construct the header and field definitions for an entity."
    lines = []
    lines.append("[{name}]".format(name=tbl.name))
    lines.extend(map(field_def, tbl.fields))
    return lines


def relation_def(schema_data: tables.Schema) -> ty.List[str]:
    "Construct the relationship definitions."
    rels = schema_data.relationships
    tmpl = "[{frm}] ---- [{to}]"
    return [tmpl.format(frm=frm, to=to) for frm, to in rels]


def make(schema_data=None, version=None):
    buffer = io.StringIO()

    for ent in schema_data.raw_entities:
        buffer.write("\n".join(table_def(ent)))
        buffer.write("\n")

    buffer.write("\n".join(relation_def(schema_data)))

    return buffer.getvalue()
