'''Convert the schema data into a .dot source file.
'''
import shared_schema.templates as templates


def nodecolor(tags):
    if 'managed' in tags:
        return 'grey'
    elif 'clinical' in tags:
        return 'lightblue'
    elif 'phenotypic' in tags:
        return 'green'
    else:
        return 'transparent'


def node(entity):
    name = entity.name
    tooltip = entity.description
    tags = entity.tags
    href = "#{}".format(entity.name.lower())
    tmpl = ('{name} [href="{href}", '
            'tooltip="{tooltip}", '
            'target="_parent", '
            'style="filled", '
            'fillcolor="{bgcolor}"];')
    return tmpl.format(
        name=name,
        tooltip=tooltip,
        href=href,
        bgcolor=nodecolor(tags)
    )


def edge(relation):
    source, target = relation
    tmpl = '''{source} -> {target};'''
    return tmpl.format(source=source, target=target)


def nodes(schema_data):
    for entity in schema_data.entities.values():
        yield node(entity)


def edges(schema_data):
    for rsp in schema_data.relationships:
        yield edge(rsp)


templates.register(
    'dot',
    templates.load_file('dot.mustache'),
)


def make(schema_data, title="SHARED Schema", **kwargs):
    edge_lines = "\n".join(nodes(schema_data))
    node_lines = "\n".join(edges(schema_data))
    return templates.render(
        'dot',
        {
            'title': title,
            'edge_lines': edge_lines,
            'node_lines': node_lines,
        },
    )
