import datetime
import string

import schema.data as data
import schema.entity as entity


html5_tmpl = string.Template('''<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="http://neganp.github.io/shared-schema/style.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css?family=Droid+Sans" rel="stylesheet">
        <title>$title</title>
    </head>
    <body>
        <a name="top"></a>
        <h1>SHARED Schema</h1>
        <p>Draft (alpha1 version as of $date)</p>
        <h2>Schema</h2>
        <div id="schema">
            <embed type="image/svg+xml" src="schema.svg"></embed>
            <p><a href="http://neganp.github.io/shared-schema/schema.svg" target="_blank">bigger</a></p>
        </div>
        <h2>Data Dictionary</h2>
        <p>The fields in each table are described below. The data-types are used are:</p>

        <table>
            <tr>
                <th>Data Type</th>
                <th>Description</th>
            </tr>

            <tr>
                <td>integer</td>
                <td>A whole number.</td>
            </tr>
            <tr>
                <td>float</td>
                <td>A decimal number.</td>
            </tr>
            <tr>
                <td>string</td>
                <td>A piece of text.</td>
            </tr>
            <tr>
                <td>date</td>
                <td>A calendar date (YYYY-MM-DD).</td>
            </tr>
            <tr>
                <td>uuid</td>
                <td>An arbitrary unique identifier (e.g: 'cf66f56d-5bd0-477c-bca9-0fb712cf8753').</td>
            </tr>
            <tr>
                <td>bool</td>
                <td>True or False.</td>
            </tr>
            <tr>
                <td>enum (...)</td>
                <td>One of a set of values. For example, enthnicity might be represented by the data-type 'enum(caucasian, latino, asian, black, indigenous-american)'. An '...' indicates that the allowed values are to-be-determined.</td>
            </tr>
            <tr>
                <td>foreign key (tbl_name)</td>
                <td>Indicates a link to a different table. For example, viral isolate's record might include a 'foreign key (Person)' field to link the isolate to the participant who gave it.</td>
            </tr>
        </table>

        <hr/>

        $entities
    </body>
</html>''')


def index(title, entities):
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    return html5_tmpl.substitute(title=title, entities=entities, date=date)


# Create entries

def entity_tables(schema_data):
    raw_entities = schema_data.entities.values()
    entities = sorted(raw_entities, key=lambda e: e.name)
    entries = (entity.entry(e) for e in entities)
    return "\n".join(entries)


def make(schema_data, title="SHARED Schema (draft)"):
    return index(title, entity_tables(schema_data))
