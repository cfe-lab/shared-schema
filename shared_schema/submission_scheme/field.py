"""This module defines the submission scheme's Fields

This includes functions for converting database schema field types to
simpler submission scheme field types, and listing the possible values
for enum fields. The field obejct has methods for printing its
converted type and possible values, and class methods for creating a
submission scheme field from a database schema field, possible
changing some of its properties in the process.
"""

from typing import List, Tuple

from shared_schema import datatypes, util


def _possible_values(schema_field_type: str) -> List[str]:
    """The possible values of a schema field's corresponding submission
    scheme field.
    """
    if not datatypes.classify(schema_field_type) is datatypes.Datatype.ENUM:
        return []
    else:
        return list(util.enum_members(schema_field_type))


def _get_scheme_field_type(schema_field_type: datatypes.Datatype) -> str:
    if not isinstance(schema_field_type, datatypes.Datatype):
        raise ValueError()
    scheme_types = {
        datatypes.Datatype.INTEGER: "number",
        datatypes.Datatype.FLOAT: "number",
        datatypes.Datatype.STRING: "text",
        datatypes.Datatype.DATE: "date",
        datatypes.Datatype.UUID: "text",
        datatypes.Datatype.BOOL: "bool",
        datatypes.Datatype.ENUM: "text",
        datatypes.Datatype.FOREIGN_KEY: "text",
    }
    return scheme_types.get(schema_field_type)


class Field(object):
    """A field in a submission scheme entity"""

    def __init__(
        self,
        name: str,
        schema_type: datatypes.Datatype,
        schema_path: Tuple[str, str] = None,
        descr: str = None,
        req: bool = False,
        possible_values: str = None,
    ) -> None:
        self.schema_type = schema_type
        self.name = name
        self.description = descr
        self._possible_values = possible_values
        self.required = req
        if schema_path is None:
            msg = "Missing schema_path for field '{}'"
            raise TypeError(msg.format(name))
        self.schema_path = schema_path

    def __str__(self):
        tmpl = "<Field {} ({})>"
        return tmpl.format(self.name, self.type)

    @property
    def type(self) -> datatypes.Datatype:
        return datatypes.classify(self.schema_type)

    @property
    def possible_values(self) -> str:
        if self._possible_values is None:
            vals = [
                "``{}``".format(v) for v in _possible_values(self.schema_type)
            ]
            return ", ".join(vals)
        else:
            return self._possible_values

    @staticmethod
    def from_schema_field(
        schema_field,
        req=False,
        new_descr=None,
        new_name=None,
        new_possible_values=None,
        schema_path=None,
    ):
        def or_default(item, default):
            if item is not None:
                return item
            else:
                return default

        return Field(
            or_default(new_name, schema_field.name),
            schema_path=schema_path,
            schema_type=schema_field.type,
            req=req,
            descr=or_default(new_descr, schema_field.description),
            possible_values=or_default(new_possible_values, None),
        )
