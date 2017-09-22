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
            tables.Schema(bad_data)

    def test_find_relations(self):
        sd = tables.Schema(test.example_data.entities)
        rels = sd.relationships
        expected_rels = {("baz", "foo")}
        self.assertEqual(
            rels,
            expected_rels,
            "Relationships not as expected",
        )

    def test_find_field(self):
        sd = tables.Schema(test.example_data.entities)

        self.assertEqual(
            sd.find_field('foo', 'foo1'),
            tables.field('foo1', 'integer', 'The first field of foo'),
        )
        self.assertEqual(
            sd.find_field('bar', 'bar2'),
            tables.field('bar2', 'date', 'The second field of a bar'),
        )
        with self.assertRaises(KeyError):
            sd.find_field('not a real entity', 'whatever')
        with self.assertRaises(KeyError):
            sd.find_field('foo', 'not a real field')
