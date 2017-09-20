import unittest

from shared_schema import util


class TestFunctions(unittest.TestCase):

    def test_foreign_key_target(self):
        cases = [
            ('foreign key(a)', 'a'),
            ('foreign key (b)', 'b'),
        ]
        for (input, expected) in cases:
            self.assertEqual(expected, util.foreign_key_target(input))

    def test_enum_members(self):
        cases = [
            ('enum(1, 2, 3)', ['1', '2', '3']),
            ('enum(a, b, c)', ['a', 'b', 'c']),
            ('enum (once,there,was,a,way)',
             ['once', 'there', 'was', 'a', 'way']),
        ]
        for (input, expected) in cases:
            self.assertEqual(
                expected,
                list(util.enum_members(input)),
            )
