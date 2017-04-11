import string


field_tmpl = string.Template(
    '''<tr> <td>$name</td> <td>$type</td> <td>$description</td> </tr>'''
)

def field_row(field):
    fs = field._asdict()
    return field_tmpl.substitute(**fs)


fields_tmpl = string.Template('''
<table>
<tr><th>Name</th><th>Type</th><th>Description</th></tr>
$rows
</table>''')

def fields_table(fields):
    field_rows = (field_row(field) for field in fields)
    rows = "\n".join(field_rows)
    return fields_tmpl.substitute(rows=rows)


entity_tmpl = string.Template('''
<a name="$anchor_name" />
<h3>$name</h3>
<p>$description</p>
$fields_table''')

def entry(entity):
    tmpl_data = {
        "anchor_name": entity.name,
        "name": entity.name.capitalize(),
        "description": entity.description,
        "fields_table": fields_table(entity.fields),
    }
    return entity_tmpl.substitute(**tmpl_data)
