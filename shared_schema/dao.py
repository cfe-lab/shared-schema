'''Concrete database connection functions and data-access-objects

'''
import uuid

import sqlalchemy as sa
import sqlalchemy.types as sa_types

from . import tables
from . import util


class UUID(sa_types.TypeDecorator):
    impl = sa_types.CHAR

    @staticmethod
    def as_str(u):
        return "{:032x}".format(u.int)

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            msg = "Tried to make a UUID column with a non-uuid value: {}"
            raise ValueError(msg.format(value))
        else:
            return self.as_str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)


def column_type(field_type, schema_data):
    simple_types = {
        'bool': sa.Boolean,
        'date': sa.Date,
        'float': sa.Float,
        'integer': sa.Integer,
        'string': sa.String(),  # ignore length; SQLite doesn't require it
        'uuid': UUID,
    }
    if field_type in simple_types:
        return simple_types.get(field_type)

    if field_type.strip().startswith('foreign key'):
        target_entity = util.foreign_key_target(field_type)
        target_entity_pk = schema_data.primary_key_of(target_entity)
        fk_target = "{}.{}".format(target_entity, target_entity_pk)
        return sa.ForeignKey(fk_target)

    if field_type.strip().startswith('enum'):
        members = list(util.enum_members(field_type))
        if not members:
            msg = "Invalid enum type: {}"
            raise ValueError(msg.format(field_type))
        return sa.Enum(*members)


def as_column(field: tables.Field, entity: tables.Entity, schema_data):
    col_type = column_type(field.type, schema_data)
    name = field.name
    is_pk = name == entity.meta['primary key']
    nullable = field.nullable
    return sa.Column(name, col_type, primary_key=is_pk, nullable=nullable)


def as_table(entity: tables.Entity, meta, schema_data):
    columns = [as_column(f, entity, schema_data) for f in entity.fields]
    return sa.Table(
        entity.name,
        meta,
        *columns,
    )


class DAO(object):
    '''A data access object that conforms to the SHARED Schema'''

    def __init__(self, schema_data):
        self._meta = sa.MetaData()
        self.tables = {}
        for entity in schema_data.entities.values():
            tbl = as_table(entity, self._meta, schema_data)
            self.tables[entity.name] = tbl
            setattr(self, entity.name.lower(), tbl)
