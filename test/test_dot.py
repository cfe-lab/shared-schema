import unittest

from schema import dot
from schema import data

from test.example_data import *

class TestElementRenderers(unittest.TestCase):

    def test_entity_node(self):
        foo_ent = entities[0]
        expected = '''Foo [href="#foo", tooltip="A foo"];'''
        calcd = dot.node(foo_ent)
        self.assertEqual(
            calcd,
            expected,
            "Unexpected entity node output",
        )

    def test_link_edge(self):
        relation = ("foo", "bar")
        expected = "Foo -> Bar;"
        calcd = dot.edge(relation)
        self.assertEqual(
            calcd,
            expected,
            "Unexpected edge output",
        )

    def test_make_smoketest(self):
        dot.make(data.SchemaData(entities))
