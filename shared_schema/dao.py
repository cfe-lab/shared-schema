'''Concrete database connection functions and data-access-objects

'''
import uuid

import sqlalchemy as sa
import sqlalchemy.types as sa_types

from . import data
from . import datatypes
from . import tables
from . import util
from . import regimens


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
        datatypes.Datatype.FLOAT: sa.Float(asdecimal=True),
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


def is_pk(field: tables.Field, entity: tables.Entity):
    is_sole_pk = field.name == entity.meta["primary key"]
    is_compound_pk = field.name in entity.meta["primary key"]
    return is_sole_pk or is_compound_pk


def as_column(field: tables.Field, entity: tables.Entity, schema_data):
    col_type = column_type(field.type, schema_data)
    name = field.name
    mark_pk = is_pk(field, entity)
    nullable = field.nullable
    return sa.Column(name, col_type, primary_key=mark_pk, nullable=nullable)


def as_table(entity: tables.Entity, meta, schema_data):
    columns = [as_column(f, entity, schema_data) for f in entity.fields]
    return sa.Table(
        entity.name,
        meta,
        *columns,
    )


class DAO(object):
    '''A Data Access Object (DAO) that conforms to the SHARED Schema.

    The tables (as defined by a shared_schema.tables.Schema instance)
    are available in a dictionary that lives in an attribute called
    "tables". They're also available directly as attributes on the DOA
    (in lowercase, e.g. "dao.regimen" or "dao.behaviordata").
    '''

    def __init__(self, db_url, engine_args=None, schema_data=None):
        '''Connects to the database and creates as SqlAlchemy engine.

        Arguments:
        - db_url        the connection string of the database to use
        - schema_data   an instance of shared_schema.tables.Schema
        - engine_args   a map of keyword args for sqlalchemy.create_engine

        Use the database URL "sqlite:///:memory:" for an ephemeral
        testing database.

        If isn't provided, "shared_schema.data.schema_data" is used by
        default.
        '''
        self._db_url = db_url
        self._meta = sa.MetaData()
        self.tables = {}
        if schema_data is None:
            schema_data = data.schema_data
        for entity in schema_data.entities.values():
            tbl = as_table(entity, self._meta, schema_data)
            self.tables[entity.name] = tbl
            setattr(self, entity.name.lower(), tbl)
        if engine_args is None:
            engine_args = {}
        self.engine = sa.create_engine(db_url, **engine_args)
        # Enable foreign key checking (disabled by default in SQLite)"
        if "sqlite" in self._db_url.lower():
            with self.engine.connect() as conn:
                conn.execute("PRAGMA foreign_keys = on")

    def init_db(self):
        self._meta.create_all(self.engine)

    def load_standard_regimens(self):
        '''Populate the Regimen and RegimenDrugInclusion tables with the
        regimens from shared_schema.regimens.standard
        '''
        for regname, regspec in regimens.standard.regimens.items():
            with self.engine.begin():
                reg_id = uuid.uuid4()
                self.insert(
                    "regimen",
                    {
                        "id": reg_id,
                        "name": regname,
                    },
                )
                regdata = regimens.cannonical.from_string(regspec)
                inclusions = regimens.cannonical.drug_inclusions(regdata)
                inclusion_data = [{
                    "regimen_id": reg_id,
                    "medication_id": incl.medication_id,
                    "dose": incl.dose,
                    "frequency": incl.frequency,
                    "duration": incl.duration,
                } for incl in inclusions]
                self.insert("regimendruginclusion", inclusion_data)

    def execute(self, expr, *rest):
        conn = self.engine.connect()
        return conn.execute(expr, *rest)

    def insert(self, tablename, item):
        table = getattr(self, tablename)
        if table is None:
            raise ValueError("No such table: {}".format(tablename))
        ins = table.insert()
        with self.engine.begin() as conn:
            conn.execute(ins, item)

    def get_regimen(self, reg_id):
        reg_qry = self.regimen.select(self.regimen.c.id == reg_id)
        result = self.execute(reg_qry).fetchone()
        return result
