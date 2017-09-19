import unittest

from shared_schema.submission_schemes import field
from shared_schema.submission_schemes import multi_table
from shared_schema.submission_schemes import util


class TestMultiTableSubmissionScheme(unittest.TestCase):

    def test_construction_succeeded(self):
        'Test that the derivation from the database schema succeeded'
        for entity, fields in multi_table.scheme.items():
            for fld in fields:
                assert isinstance(fld, field.Field), \
                    "Field was constructed successfully"
