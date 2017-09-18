'''Objects for describing and checking tables an their fields.

A Field maps to an individual database column.

An Entity contains many fields, and represents a database table.

A Schema contains many entities, and can check things like foreign keys.'''

import collections

import shared_schema.util as util


_entity = collections.namedtuple(
    "entity",
    ["name", "description", "fields", "meta"],
)


class Entity(_entity):
    @classmethod
    def make(cls, name, description, fields, meta=None):
        if meta is None:
            raise UserWarning("Metadata is required (for primary key)")
        if 'primary key' not in meta:
            raise UserWarning("Primary key is required in meta")
        return cls(name, description, fields, meta)

    @property
    def tags(self):
        return self.meta.get('tags', {})


_field = collections.namedtuple(
    "field",
    ["name", "type", "description", "meta"],
)


class Field(_field):
    @classmethod
    def make(cls, name, type, description, meta=None):
        if meta is None:
            meta = dict()
        return cls(name, type, description, meta)

    @property
    def tags(self):
        return self.meta.get('tags', {})

field = Field.make


class Schema(object):

    types = {"integer", "float", "string", "foreign key", "date",
             "uuid", "enum", "bool"}

    def __init__(self, raw_entities):
        self.raw_entities = raw_entities
        self.entities = {e.name: e for e in raw_entities}
        err_msg = "Duplicate entities?"
        assert len(self.entities) == len(self.raw_entities), err_msg
        types = (f.type for e in self.entities.values() for f in e.fields)
        for t in types:
            err_msg = "invalid type: {}".format(t)
            assert self.type_is_valid(t, self.entities), err_msg

    @property
    def relationships(self):
        rels = set()
        for ename, entity in self.entities.items():
            types = (f.type for f in entity.fields)
            foreign_keys = [t for t in types if "foreign key" in t]
            targets = [util.foreign_key_target(f) for f in foreign_keys]
            for target in targets:
                rel = (entity.name, target)
                rels.add(rel)
        return rels

    @classmethod
    def type_is_valid(cls, t, entities):
        known_type = t in cls.types
        fk = t.lstrip().startswith("foreign key")
        enum = t.lstrip().startswith("enum")
        if not (known_type or fk or enum):
            return False
        elif fk:
            fk_target = util.foreign_key_target(t)
            err_msg = "invalid foreign key target: {}".format(fk_target)
            assert fk_target in entities, err_msg
            return True
        else:
            return True

    def find_field(self, entity_name, field_name):
        entity = self.entities.get(entity_name)
        if entity is None:
            msg = "No entity called '{}' in schema"
            raise KeyError(msg.format(entity_name))
        field = next((f for f in entity.fields if f.name == field_name),
                     None)
        if field is None:
            msg = "No field called '{}' on entity {}"
            raise KeyError(msg.format(field_name, entity_name))
        return field
