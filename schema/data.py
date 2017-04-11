import collections
import re

# Data Parsing

entity = collections.namedtuple("entity", ["name", "description", "fields"])
field = collections.namedtuple("field", ["name", "type", "description"])


def foreign_key_target(field_type):
    '''What entity does a foreign key target?'''
    matches = re.findall("\((.+)\)", field_type)
    return matches[0]


class SchemaData(object):

    def __init__(self, raw_entities):
        self.raw_entities = raw_entities
        self.entities = {e.name: e for e in raw_entities}
        err_msg = "Duplicate entities?"
        assert len(self.entities) == len(self.raw_entities), err_msg

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
