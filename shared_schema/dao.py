'''Concrete database connection functions and data-access-objects

'''
import uuid

import sqlalchemy as sa
import sqlalchemy.types as sa_types

from . import data
from . import datatypes
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
    dt = datatypes.classify(field_type)
    # NOTE(nknight): We're ignoring the 'length' parameter to the
    # string field becuase sqlite and postgres don't require it
    simple_types = {
        datatypes.Datatype.INTEGER: sa.Integer,
        datatypes.Datatype.FLOAT: sa.Float,
        datatypes.Datatype.STRING: sa.String(),
        datatypes.Datatype.DATE: sa.Date,
        datatypes.Datatype.UUID: UUID,
        datatypes.Datatype.BOOL: sa.Boolean,
    }
    if dt in simple_types:
        return simple_types.get(dt)
    if dt is datatypes.Datatype.FOREIGN_KEY:
        target_entity = util.foreign_key_target(field_type)
        target_entity_pk = schema_data.primary_key_of(target_entity)
        fk_target = "{}.{}".format(target_entity, target_entity_pk)
        return sa.ForeignKey(fk_target)
    if dt is datatypes.Datatype.ENUM:
        members = list(util.enum_members(field_type))
        if not members:
            msg = "Invalid enum type: {}"
            raise ValueError(msg.format(field_type))
        return sa.Enum(*members)
    msg = "Can't get column type for '{}'"
    raise ValueError(msg.format(field_type))


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

    def __init__(self, db_url, schema_data=None, echo=False):
        self._meta = sa.MetaData()
        self.tables = {}
        if schema_data is None:
            schema_data = data.schema_data
        for entity in schema_data.entities.values():
            tbl = as_table(entity, self._meta, schema_data)
            self.tables[entity.name] = tbl
            setattr(self, entity.name.lower(), tbl)
        self.engine = sa.create_engine(db_url, echo=echo)

    def init_db(self):
        self._meta.create_all(self.engine)

    def execute(self, expr, *rest):
        conn = self.engine.connect()
        return conn.execute(expr, *rest)

    def get_regimen(self, reg_id):
        reg_qry = self.regimen.select(self.regimen.c.id == reg_id)
        result = self.execute(reg_qry).fetchone()
        return result
