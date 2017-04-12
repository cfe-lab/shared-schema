#encoding: utf8
import collections
import re

# Data Parsing

entity = collections.namedtuple("entity", ["name", "description", "fields"])
field = collections.namedtuple("field", ["name", "type", "description"])


def foreign_key_target(field_type):
    '''What entity does a foreign key target?'''
    matches = re.findall("\((.+)\)", field_type)
    return matches[0]


class Schema(object):

    types = {"integer", "float", "string", "foreign key", "date",
             "year", "uuid", "enum", "bool"}

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
            targets = [foreign_key_target(f) for f in foreign_keys]
            for target in targets:
                rel = (entity.name, target)
                rels.add(rel)
        return rels

    @classmethod
    def type_is_valid(cls, t, entities):
        known_type = t in cls.types
        fk = "foreign key" in t
        enum = "enum" in t
        if not (known_type or fk or enum):
            return False
        elif fk:
            fk_target = foreign_key_target(t)
            err_msg = "invalid foreign key target: {}".format(fk_target)
            assert  fk_target in entities, err_msg
            return True
        else:
            return True


# Parse Data

entities = [
    entity(
        "person",
        "A study participant",
        [field("id", "uuid", "Unique identifier"),
        ]),
    entity("isolate",
           "A clinical isolate from a patient",
           [field("id", "uuid", "Unique identifier"),
            field("person_id", "foreign key (person)",
                  "The person from whom the isolate was obtained"),
           ]),
]

schema_data = SchemaData(entities)
