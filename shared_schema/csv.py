import csv
import io

COLUMNS = ['entity', 'field', 'field type', 'field description']


def printable_field(entity_name, field):
    return {
        "entity": entity_name,
        "field": field.name,
        "field type": field.type,
        "field description": field.description,
    }


def fields_of(entity):
    entity_name = entity.name
    for field in entity.fields:
        yield printable_field(entity_name, field)


def entity_fields(entities):
    for entity in entities:
        for row in fields_of(entity):
            yield row


def make(schema_data, **kwargs):
    entities = sorted(schema_data.raw_entities, key=lambda e: e.name)
    outbuffer = io.StringIO()
    out = csv.DictWriter(outbuffer, COLUMNS)
    for row in entity_fields(entities):
        out.writerow(row)
    return outbuffer.getvalue()
