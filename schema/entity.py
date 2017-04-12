#encoding: utf8
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


#<a class="to-top" href="#top">back to top</a>
entity_tmpl = string.Template('''
<div class="entity" id="$anchor_name">
  <a name="$anchor_name"></a>
  <h3>$name <a href="#$anchor_name">🔗</a></h3>
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
