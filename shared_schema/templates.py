"""Template rendering

Register Mustache templates and populate them with data.
"""

import os.path

import pystache

TEMPLATES = {}

TEMPLATE_ROOT = os.path.join(os.path.dirname(__file__), "templates")


def load_file(fname):
    fpath = os.path.join(TEMPLATE_ROOT, fname)
    with open(fpath, "r") as infile:
        return infile.read()


def register(key, text):
    if key in TEMPLATES:
        raise ValueError("'{}' already has a template'".format(key))
    tpl = pystache.parse(text)
    TEMPLATES[key] = tpl


def render(key, tpl_data):
    try:
        tpl = TEMPLATES[key]
    except KeyError as k:
        tpl_lines = ("  - {}".format(k) for k in TEMPLATES.keys())
        tpl_block = "\n".join(tpl_lines)
        print("-" * 80)
        print("  '{}' isn't a registered template.".format(k))
        print("  Registered templates are:")
        print(tpl_block)
        print("-" * 80)
        raise
    return pystache.render(tpl, tpl_data)
