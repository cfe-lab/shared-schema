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

    def __init__(self, name: str, schema_type: str=None,
                 descr: str=None, req: bool=False) -> None:
        self._schema_field_type = schema_type
        self.name = name
        self.description = descr

    @property
    def type(self) -> str:
        return _get_scheme_field_type(self._schema_field_type)

    @property
    def possible_values(self) -> List[str]:
        return _possible_values(self._schema_field_type)

    @staticmethod
    def from_schema_field(cls, schema_field, req=False, new_descr=None,
                          new_name=None):
        return Field(
            (new_name if new_name is not None else schema_field.name),
            schema_field.type,
            req=req,
            descr=(new_descr if new_descr is not None else schema_field.descr),
        )
