'''This module contains functions for converting database schema field
types to simpler submission scheme field types, and lists the possible
values for enum fields.
'''

from typing import List


from shared_schema import tables
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


class SubmissionSchemeFieldType(object):

    def __init__(self, schema_field_type: str) -> None:
        self._schema_field_type = schema_field_type

    @property
    def type(self) -> str:
        return _get_scheme_field_type(self._schema_field_type)

    @property
    def possible_values(self) -> List[str]:
        return _possible_values(self._schema_field_type)
        
