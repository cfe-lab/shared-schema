import unittest

from shared_schema import dot
from shared_schema import data

from test.example_data import entities


class TestElementRenderers(unittest.TestCase):

    def test_entity_node(self):
        foo_ent = entities[0]
        expected = ('foo [href="/#foo", tooltip="A foo", '
                    'target="_parent", style="filled", '
                    'fillcolor="transparent"];')
        calcd = dot.node(foo_ent)
        self.assertEqual(
            calcd,
            expected,
            "Unexpected entity node output",
        )

    def test_link_edge(self):
        relation = ("Foo", "BaR")
        expected = "Foo -> BaR;"
        calcd = dot.edge(relation)
        self.assertEqual(
            calcd,
            expected,
            "Unexpected edge output",
        )

    def test_make_smoketest(self):
        dot.make(data.Schema(entities))
