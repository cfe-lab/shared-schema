'''This module defines submission scheme's Fields

This includes functions for converting database schema field types to
simpler submission scheme field types, and listing the possible values
for enum fields. The field obejct has methods for printing its
converted type and possible values, and class methods for creating a
submission scheme field from a database schema field, possible
changing some of its properties in the process.
'''

from typing import List

from shared_schema import util


def _possible_values(schema_field_type: str) -> List[str]:
    """The possible values of a schema field's corresponding submission
    scheme field.
    """
    if not schema_field_type.strip().startswith('enum'):
        return []
    else:
        return list(util.enum_members(schema_field_type))


def _get_scheme_field_type(schema_field_type: str) -> str:
    sft = schema_field_type.strip()
    if sft == 'date':
        return 'date'
    elif sft == 'bool':
        return 'bool'
    elif sft in ['integer', 'float']:
        return 'number'
    elif sft in ['string', 'uuid']:
        return 'text'
    elif sft.startswith('enum'):
        return 'text'
    elif sft.startswith('foreign key'):
        return 'text'
    else:
        msg_tmpl = 'Unknown schema field type: {}'
        raise ValueError(msg_tmpl.format(sft))


class Field(object):
    '''A field in a submission scheme entity'''

    def __init__(self, name: str, schema_type: str=None, descr: str=None,
                 req: bool=False, possible_values: str=None) -> None:
        self._schema_field_type = schema_type
        self.name = name
        self.description = descr
        self._possible_values = possible_values
        self.required = req

    @property
    def type(self) -> str:
        return _get_scheme_field_type(self._schema_field_type)

    @property
    def possible_values(self) -> str:
        if self._possible_values is None:
            vals = ["``{}``".format(v) for v in
                    _possible_values(self._schema_field_type)]
            return ', '.join(vals)
        else:
            return self._possible_values

    @staticmethod
    def from_schema_field(schema_field, req=False, new_descr=None,
                          new_name=None, new_possible_values=None):

        def or_default(item, default):
            if item is not None:
                return item
            else:
                return default

        return Field(
            or_default(new_name, schema_field.name),
            schema_field.type,
            req=req,
            descr=or_default(new_descr, schema_field.description),
            possible_values=or_default(new_possible_values, None),
        )
