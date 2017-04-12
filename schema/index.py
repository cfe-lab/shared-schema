import string

import schema.data as data
import schema.entity as entity


html5_tmpl = string.Template('''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="style.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css?family=Droid+Sans" rel="stylesheet">
    <title>$title</title>
  </head>
  <body>
    <a name="top"></a>
    <h1>SHARED Schema</h1>
    <p>Draft version</p>
    <h2>Schema</h2>
    <div id="schema">
      <embed type="image/svg+xml" src="schema.svg"></embed>
      <p><a href="schema.svg" target="_blank">bigger</a></p>
    </div>
    <h2>Data Dictionary</h2>
    <p>In no particular order, the fields associated with each table.</p>
    $entities
  </body>
</html>''')


def index(title, entities):
    return html5_tmpl.substitute(title=title, entities=entities)


# Create entries

def entity_tables(schema_data):
    entities = schema_data.entities.values()
    entries = (entity.entry(e) for e in entities)
    return "\n".join(entries)


def make(schema_data, title="SHARED Schema (draft)"):
    return index(title, entity_tables(schema_data))
