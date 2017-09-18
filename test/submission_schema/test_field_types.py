import unittest

from shared_schema import data
from shared_schema.submission_schemes import field_types


class FieldTypesTestCase(unittest.TestCase):

    def test_possible_values(self):
        self.assertEqual(
            [],
            field_types._possible_values('string'),
            'Atomic types have empty possible values',
        )
        self.assertEqual(
            [],
            field_types._possible_values('foreign key(Person)'),
            'Foreign keys have empty possible values',
        )
        self.assertEqual(
            ['a', 'b', 'c'],
            field_types._possible_values('enum(a, b, c)'),
        )

    def test_invalid_field_type(self):
        with self.assertRaises(ValueError):
            invalid_type = 'asdf'
            field_types._get_scheme_field_type(invalid_type)

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
            self.assertEqual(
                outp,
                field_types._get_scheme_field_type(inp)
            )

    def test_existing_field_types(self):
        # Check that we can get an expected answer for all fields in
        # the existing schema
        for entity in data.schema_data.raw_entities:
            for field in entity.fields:
                field_types._get_scheme_field_type(field.type)
                field_types._possible_values(field.type)
