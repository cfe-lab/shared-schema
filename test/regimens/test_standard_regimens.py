import unittest

from shared_schema.regimens import standard
from shared_schema.regimens import grammar as rg


class TestStandardRegimens(unittest.TestCase):

    def test_parsing(self):
        "Check that the regimens in the standard regimens can be parsed"
        for nm, reg in standard.regimens.items():
            msg = "Error parsing regimenn for {}"
            try:
                rg.parse(reg)
            except SyntaxError:
                self.assertTrue(False, msg.format(nm))


class TestExpandStandard(unittest.TestCase):

    def test_valid_source_passes_through(self):
        cases = standard.regimens.values()
        for case in cases:
            self.assertEqual(
                case,
                standard.expand(case),
                "Expected raw source to not be changed by standard",
            )

    def test_names_expand_as_expected(self):
        for name, value in standard.regimens.items():
            self.assertEqual(
                standard.expand(name),
                value,
            )

    def test_names_and_source_can_coexist(self):
        cases = [
            "60mg DCV QD 12 weeks, PEGASYS",
            "VOSEVI, 600mg RBV BID 48 weeks",
            "VICTRELIS, VIEKIRA PAK, 400mg SOF QD 12 weeks",
            "400mg SOF + 100mg VEL QD 12 weeks, PEGASYS, 60mg DCV QD 12 weeks",
        ]
        for src in cases:
            expanded_src = standard.expand(src)
            rg.parse(expanded_src)
