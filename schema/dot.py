'''Convert the schema data into a .dot source file.
'''

def node(entity):
    name = entity.name.capitalize()
    tooltip = entity.description
    href = "#{}".format(entity.name.lower())
    tmpl = '''{name} [href="{href}", tooltip="{tooltip}"];'''
    return tmpl.format(name=name, tooltip=tooltip, href=href)


def edge(relation):
    source, target = relation
    source_name = source.capitalize()
    target_name = target.capitalize()
    tmpl = '''{source_name} -> {target_name};'''
    return tmpl.format(source_name=source_name, target_name=target_name)


def nodes(schema_data):
    for entity in schema_data.entities.values():
        yield node(entity)


def edges(schema_data):
    for rsp in schema_data.relationships:
        yield edge(rsp)


dot_template = '''digraph "{title}" {{
{edge_lines}
{node_lines}
}}'''

def make(schema_data, title="schema"):
    edge_lines = "\n".join(nodes(schema_data))
    node_lines = "\n".join(edges(schema_data))
    return dot_template.format(
        title=title,
        edge_lines=edge_lines,
        node_lines=node_lines,
    )
