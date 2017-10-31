import unittest

import shared_schema.datatypes as datatypes


Datatype = datatypes.Datatype


class TestClassify(unittest.TestCase):

    def test_atomic_types(self):
        simple_cases = [
            ('integer', Datatype.INTEGER),
            ('float', Datatype.FLOAT),
            ('string', Datatype.STRING),
            ('date', Datatype.DATE),
            ('uuid', Datatype.UUID),
            ('bool', Datatype.BOOL),
        ]
        for src, expected in simple_cases:
            self.assertEqual(datatypes.classify(src), expected)

    def test_enum(self):
        cases = [
            'enum(1,2,3)',
            'enum(a,b,c)',
            'enum(asdf, jkl, semicolon)',
            'enum(enum, bool, int)',
        ]
        for src in cases:
            self.assertEqual(datatypes.classify(src), Datatype.ENUM)

    def test_foreign_key(self):
        cases = [
            'foreign key(Enum)',
            'foreign key(Asdf Jkl)',
        ]
        for src in cases:
            self.assertEqual(datatypes.classify(src), Datatype.FOREIGN_KEY)

    def test_failure_cases(self):
        error_cases = [
            object(),
            None,
            'non-existant type',
        ]
        for src in error_cases:
            with self.assertRaises(ValueError):
                datatypes.classify(src)
