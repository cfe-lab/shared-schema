import re


def foreign_key_target(field_type):
    '''What entity does a foreign key target?'''
    matches = re.findall("\((.+)\)", field_type)
    return matches[0]
