from shared_schema.data import Entity, field

entities = [
    Entity.make(
        "foo",
        "A foo",
        [
            field(
                "foo1",
                "integer",
                "The first field of foo",
            )
        ],
        meta={'primary key': 'foo1'}
    ),
    Entity.make(
        "bar",
        "A bar",
        [
            field(
                "bar1",
                "string",
                "The first field of a bar"
            ),
            field(
                "bar2",
                "date",
                "The second field of a bar"
            ),
        ],
        meta={'primary key': 'bar1'}
    ),
    Entity.make(
        "baz",
        "A baz",
        [
            field(
                "baz1",
                "foreign key(foo)",
                "The bar the baz belongs to"
                ),
        ],
        meta={'primary key': 'baz1'}
    ),
]
