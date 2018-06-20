import unittest

from shared_schema import data, datatypes
from shared_schema.submission_scheme import field


class TestSubmissionSchemeField(unittest.TestCase):
    def test_possible_values(self):
        self.assertEqual(
            [],
            field._possible_values('string'),
            'Atomic types have empty possible values',
        )
        self.assertEqual(
            [],
            field._possible_values('foreign key(Person)'),
            'Foreign keys have empty possible values',
        )
        self.assertEqual(
            ['a', 'b', 'c'],
            field._possible_values('enum(a, b, c)'),
        )

    def test_invalid_field_type(self):
        with self.assertRaises(ValueError):
            invalid_type = 'asdf'
            field._get_scheme_field_type(invalid_type)

    def test_valid_field_type(self):
        cases = [
            ('date', 'date'),
            ('bool', 'bool'),
            ('integer', 'number'),
            ('float', 'number'),
            ('string', 'text'),
            ('uuid', 'text'),
            ('enum(1,2,3)', 'text'),
            ('foreign key (Person)', 'text'),
        ]
        for inp, outp in cases:
            dt = datatypes.classify(inp)
            self.assertEqual(outp, field._get_scheme_field_type(dt))

    def test_existing_field(self):
        # Check that we can get an expected answer for all fields in
        # the existing schema
        for entity in data.schema_data.raw_entities:
            for fld in entity.fields:
                dt = datatypes.classify(fld.type)
                field._get_scheme_field_type(dt)
                field._possible_values(fld.type)
