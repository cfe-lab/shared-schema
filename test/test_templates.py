import unittest

from schema import templates


class TestTemplates(unittest.TestCase):

    def test_no_template_clashes(self):
        tpl = ""

        templates.register("a", tpl)
        with self.assertRaises(ValueError, msg="Undetected key clash"):
            templates.register("a", tpl)

    def test_missing_template(self):
        with self.assertRaises(KeyError, msg="Undetected missing template"):
            templates.render("asdf", {})
        
    
        
