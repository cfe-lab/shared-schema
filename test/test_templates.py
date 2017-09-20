import unittest

from shared_schema import templates


class TestTemplates(unittest.TestCase):

    def test_no_template_clashes(self):
        try:
            orig_templates = templates.TEMPLATES
            templates.TEMPLATES = {}
            tpl = ""
            templates.register("a name that won't be used", tpl)
            with self.assertRaises(ValueError):
                templates.register("a name that won't be used", tpl)
        finally:
            templates.TEMPLATES = orig_templates

    def test_missing_template(self):
        with self.assertRaises(KeyError):
            templates.render("asdf", {})
