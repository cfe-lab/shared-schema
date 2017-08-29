import unittest

import shared_schema.data
from shared_schema.data import Entity

import test.example_data



class TestSchema(unittest.TestCase):

    def test_no_duplicate_keys(self):
        bad_data = [
            Entity.make("a", "", [], meta={'primary key': None}),
            Entity.make("a", "", [], meta={'primary key': None}),
        ]
        with self.assertRaises(AssertionError):
            schema_data = shared_schema.data.Schema(bad_data)

    def test_find_relations(self):
        sd = shared_schema.data.Schema(test.example_data.entities)
        rels = sd.relationships
        expected_rels = {("baz", "foo")}
        self.assertEqual(
            rels,
            expected_rels,
            "Relationships not as expected",
        )
