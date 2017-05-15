from schema.data import Entity, field

entities = [
    Entity.make("foo",
           "A foo",
           [field("foo1",
                  "integer",
                  "The first field of foo")]),
    Entity.make("bar",
            "A bar",
            [field("bar1",
                   "string",
                   "The first field of a bar"),
             field("bar2",
                   "date",
                   "The second field of a bar")]),
    Entity.make("baz",
           "A baz",
           [field("baz1",
                  "foreign key(foo)",
                  "The bar the baz belongs to")])]
           

