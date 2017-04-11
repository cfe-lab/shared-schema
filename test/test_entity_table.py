import unittest

from schema.data import entity, field
import schema.entity
from test.example_data import *

class TestEntityTable(unittest.TestCase):

    def test_render_row_smoketest(self):
        test_field = field("id", "uid", "An Id")
        schema.entity.field_row(test_field)

    def test_fields_table_smoketest(self):
        fields = [
            field("id", "uuid", "the id"),
            field("name", "string", "the name"),
            field("date", "date", "the date"),
        ]
        schema.entity.fields_table(fields)
        
    def test_entity_entry_smoketest(self):
        for e in entities:
            schema.entity.entry(e)
