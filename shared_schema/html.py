'''Create an HTML representation of the Schema
'''

import datetime
import re
import string

import shared_schema.data as data
import shared_schema.templates as templates
import shared_schema.util as util


def classes(tags):
    possible_tags = ['managed', 'required']
    return ' '.join(filter(lambda t: t in tags, possible_tags))


def fmt_fk_type(field):
    target = util.foreign_key_target(field.type)
    anchor = target.lower()
    link = '<a href="#{}">{}</a>'.format(anchor, target)
    return "foreign key ({})".format(link)


def field_data(field):
    if 'foreign key' in field.type:
        ftype = fmt_fk_type(field)
    else:
        ftype = field.type
    return {
        'fclass': classes(field.tags),
        'name': field.name,
        'type': ftype ,
        'description': field.description,
    }


def entity_data(entity):
    fields_data = [field_data(f) for f in entity.fields]
    return {
        'anchor_name': entity.name.lower(),
       'name': entity.name,
        'description': entity.description,
        'fields': fields_data,
    }


templates.register(
    'html',
    templates.load_file('html.mustache'),
)


def index(title, entities, version):
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    entities_data = [entity_data(e) for e in entities]
    return templates.render(
        'html',
        { 'title': title,
          'entities': entities_data,
          'date': date,
          'version': version,
        }
    )


def make(schema_data, version, title="SHARED Schema (draft)"):
    entities = schema_data.raw_entities
    return index(title, entities, version)
