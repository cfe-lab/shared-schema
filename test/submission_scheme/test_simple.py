import unittest

from shared_schema.data import schema_data
from shared_schema.submission_schemes import field
from shared_schema.submission_schemes import simple


class TestSimpleSubmissionScheme(unittest.TestCase):

    def test_construction_succeeded(self):
        'Test that the derivation from the database schema succeeded'
        for entity, fields in simple.scheme.items():
            for fld in fields:
                assert isinstance(fld, field.Field), \
                  "Field was constructed successfully"

    def test_single_field(self):
        # this is mostly here to ensure the validity of the next test
        self.assertEqual(
            1,
            len(simple.scheme.values()),
            "More than one table in simple scheme",
        )

    def test_unique_field_names(self):
        simple_fields = next(iter(simple.scheme.values()))
        names = [f.name for f in simple_fields]
        duplicate_names = set(nm for nm in names if names.count(nm) > 1)
        msg = ("Duplicate field name in simple submission scheme:\n"
               "Duplicate fields: {}")
        self.assertEqual(
            len(names),
            len(set(names)),
            msg.format(duplicate_names),
        )

    def test_applicable_schema_paths_are_valid(self):
        '''Verify that fields' schema paths point to fields in the schema'''
        for fld in simple.scheme['simple']:
            if fld.schema_path == 'not applicable':
                continue
            schema_data.find_field(*fld.schema_path)
