import unittest

from shared_schema.data import schema_data
from shared_schema.submission_schemes import field
from shared_schema.submission_schemes import multi_table


class TestMultiTableSubmissionScheme(unittest.TestCase):

    def test_construction_succeeded(self):
        'Test that the derivation from the database schema succeeded'
        for entity, fields in multi_table.scheme.items():
            for fld in fields:
                assert isinstance(fld, field.Field), \
                    "Field was constructed successfully"

    def test_field_names_are_unique(self):
        for entity, fields in multi_table.scheme.items():
            fnames = [f.name for f in fields]
            msg = ("Non-unique field names in multi-table submission scheme:\n"
                   "Entity: {}  Duplicate fields: {}")
            duplicate_fields = set(name for name in fnames
                                   if fnames.count(name) > 1)
            self.assertEqual(
                len(fnames),
                len(set(fnames)),
                msg.format(entity, duplicate_fields)
            )

    def test_applicable_schema_paths_are_valid(self):
        '''Verify that fields' schema paths point to fields in the schema'''
        for tbl in multi_table.scheme.values():
            for fld in tbl:
                if fld.schema_path == 'not applicable':
                    continue
                schema_data.find_field(*fld.schema_path)
