#encoding: utf8
import string

import schema.util as util


fk_link_tmpl = string.Template(
    '''<a href="#$fk_anchor">$fk_name</a>'''
)
def fk_link(fk_name):
    fk_anchor = fk_name.lower()
    return fk_link_tmpl.substitute(
        fk_name=fk_name,
        fk_anchor=fk_anchor,
    )


fk_field_tmpl = string.Template(
    '''<tr> <td>$name</td> <td>foreign key ($link)</td></tr>'''
)

def fk_field_row(field):
    fk_target = util.foreign_key_target(field.type)
    link = fk_link(fk_target)
    return fk_field_tmpl.substitute(
        name=field.name,
        fk_target=fk_target,
        link=link,
    )


field_tmpl = string.Template(
    '''<tr> <td>$name</td> <td>$type</td> <td>$description</td> </tr>'''
)

def field_row(field):
    if 'foreign key' in field.type:
        return fk_field_row(field)
    else:
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


#<a class="to-top" href="#top">back to top</a>
entity_tmpl = string.Template('''
<div class="entity" id="$anchor_name">
  <a name="$anchor_name"></a>
  <h3>$name <a href="#$anchor_name">🔗</a> <a href="#top">🠉</a></h3>
  <p>$description</p>
  $fields_table
</div>''')

def entry(entity):
    tmpl_data = {
        "anchor_name": entity.name.lower(),
        "name": entity.name,
        "description": entity.description,
        "fields_table": fields_table(entity.fields),
    }
    return entity_tmpl.substitute(**tmpl_data)
