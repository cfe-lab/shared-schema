"""Common utility functions"""

import re


def foreign_key_target(field_type):
    """What entity does a foreign key target?"""
    matches = re.findall(r"foreign key\s*\((.+)\)", field_type)
    return matches[0]


def enum_members(field_type):
    "The members of an ENUM type field (from the field's type)"
    matches = re.findall(r"enum\s*\((.+)\)", field_type)
    return (member.strip().lower() for member in matches[0].split(","))
