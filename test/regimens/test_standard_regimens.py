import unittest

from shared_schema.regimens import standard
from shared_schema.regimens import grammar as rg


class TestStandardRegimens(unittest.TestCase):

    def test_parsing(self):
        "Check that the regimens in the standard regimens can be parsed"
        for nm, reg in ((r['name'], r['regimen']) for r in standard.regimens):
            msg = "Error parsing regimenn for {}"
            try:
                rg.parse(reg)
            except SyntaxError:
                self.assertTrue(False, msg.format(nm))
