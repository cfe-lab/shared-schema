'''Create a REStructuredText source file for the data dictionary

This module and the `shared-doc` module should obviate the LaTeX
exporter, and potentially  the HTML exporter.
'''

import shared_schema.templates as templates


templates.register('rst', templates.load_file('rst.mustache'))


def field_data(field):
    reqd = '•' if ('required' in field.tags) else ''
    return {
        'name': field.name,
        'type': field.type,
        'description': field.description,
        'required': reqd,
    }


def entity_data(entity):
    fields_data = [field_data(f) for f in entity.fields]
    return {
        'fields': fields_data,
        'description': entity.description,
        'anchor_name': entity.name.lower(),
        'name': entity.name,
    }


def entities_data(entities):
    return (entity_data(e) for e in entities)


def make(schema_data=None, version=None):
    entities = entities_data(schema_data.raw_entities)
    return templates.render(
        'rst',
        {
            'entities': entities
        }
    )
