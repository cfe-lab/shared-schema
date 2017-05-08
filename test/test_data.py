import unittest

import schema.data
from schema.data import entity

import test.example_data



class TestSchema(unittest.TestCase):

    def test_no_duplicate_keys(self):
        bad_data = [
            entity("a", "", []),
            entity("a", "", []),
        ]
        with self.assertRaises(AssertionError):
            schema_data = schema.data.Schema(bad_data)

    def test_find_relations(self):
        sd = schema.data.Schema(test.example_data.entities)
        rels = sd.relationships
        expected_rels = {("baz", "foo")}
        self.assertEqual(
            rels,
            expected_rels,
            "Relationships not as expected",
        )

    
        
        
