from schema.data import entity, field

entities = [
    entity("foo",
           "A foo",
           [field("foo1",
                  "integer",
                  "The first field of foo")]),
    entity("bar",
            "A bar",
            [field("bar1",
                   "string",
                   "The first field of a bar"),
             field("bar2",
                   "date",
                   "The second field of a bar")]),
    entity("baz",
           "A baz",
           [field("baz1",
                  "foreign key(foo)",
                  "The bar the baz belongs to")])]
           

