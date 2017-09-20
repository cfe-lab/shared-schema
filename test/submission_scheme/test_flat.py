import unittest

from shared_schema.submission_schemes import field
from shared_schema.submission_schemes import flat


class TestFlatSubmissionScheme(unittest.TestCase):

    def test_construction_succeeded(self):
        'Test that the derivation from the database schema succeeded'
        for entity, fields in flat.scheme.items():
            for fld in fields:
                assert isinstance(fld, field.Field), \
                  "Field was constructed successfully"

    def test_single_field(self):
        # this is mostly here to ensure the validity of the next test
        self.assertEqual(
            1,
            len(flat.scheme.values()),
            "More than one table in flat scheme",
        )

    def test_unique_field_names(self):
        flat_fields = next(iter(flat.scheme.values()))
        names = [f.name for f in flat_fields]
        duplicate_names = set(nm for nm in names if names.count(nm) > 1)
        msg = ("Duplicate field name in flat submission scheme:\n"
               "Duplicate fields: {}")
        self.assertEqual(
            len(names),
            len(set(names)),
            msg.format(duplicate_names),
        )
