import unittest

import shared_schema.tables as tables
import test.example_data


class TestSchema(unittest.TestCase):

    def test_no_duplicate_keys(self):
        bad_data = [
            tables.Entity.make("a", "", [], meta={'primary key': None}),
            tables.Entity.make("a", "", [], meta={'primary key': None}),
        ]
        with self.assertRaises(AssertionError):
            schema_data = tables.Schema(bad_data)

    def test_find_relations(self):
        sd = tables.Schema(test.example_data.entities)
        rels = sd.relationships
        expected_rels = {("baz", "foo")}
        self.assertEqual(
            rels,
            expected_rels,
            "Relationships not as expected",
        )
