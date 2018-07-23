import unittest
import uuid

from shared_schema import dao, tables
from sqlalchemy import sql


class TestUuidType(unittest.TestCase):
    def test_serialization_and_deserialization(self):
        for i in range(10000):
            u = uuid.uuid4()
            s = dao.UUID.as_str(u)
            assert uuid.UUID(s) == u


class TestTableConversion(unittest.TestCase):
    def test_compound_primary_keys(self):
        entity = tables.Entity.make(
            "TestEntity",
            "The test entity",
            [
                tables.Field.make("a", "integer", "Test field 'a'"),
                tables.Field.make("b", "integer", "Test field 'b'"),
            ],
            meta={"primary key": ["a", "b"]},
        )
        schema_data = tables.Schema([entity])
        test_dao = dao.DAO("sqlite:///:memory:", schema_data=schema_data)

        table = test_dao.testentity
        keys = table.primary_key.columns.keys()
        self.assertIn("a", keys)
        self.assertIn("b", keys)


class TestLoadStandardRegimens(unittest.TestCase):
    '''Verify that standard regimens can be loaded'''

    def test_regimens_can_be_loaded(self):
        d = dao.DAO("sqlite:///:memory:", engine_args={"echo": False})
        d.init_db()
        first_qry = d.engine.execute(d.regimen.select()).fetchall()
        self.assertEqual(
            0,
            len(first_qry),
            "Expected no regimens in an un-loaded database",
        )
        d.load_standard_regimens()
        second_qry = d.engine.execute(d.regimen.select()).fetchall()
        self.assertGreater(
            len(second_qry),
            0,
            "Expected some regimens in a loaded database",
        )


class TestDaoOperations(unittest.TestCase):
    '''Verify that saving, loading, and querying work as expected'''

    def setUp(cls):
        cls.dao = dao.DAO('sqlite:///:memory:', engine_args={"echo": False})
        cls.dao.init_db()

    def test_insert_retrieve(self):
        test_person = {
            'id': uuid.uuid4(),
            'sex': 'other',
            'year_of_birth': 1999,
        }

        insert = self.dao.person.insert().values(**test_person)
        insert_result = self.dao.execute(insert)
        self.assertIsNotNone(
            insert_result,
            'Test Person insert returned None',
        )

        select = self.dao.person.select().where(
            self.dao.person.c.id == test_person['id'])
        select_result = self.dao.execute(select).first()
        self.assertIsNotNone(
            select_result,
            "Couldn't retrieve created test person",
        )
        self.assertEqual(test_person['id'], select_result['id'])
        self.assertEqual(
            type(test_person['id']),
            type(select_result['id']),
            "UUID didn't corretly serialize/deserialize",
        )

    def assert_entity_exists_with_properties(self, entity_name, **props):
        tbl = getattr(self.dao, entity_name)
        preds = [tbl.columns[k] == v for k, v in props.items()]
        pred = sql.and_(*preds)
        select = tbl.select().where(pred)
        result = self.dao.execute(select).first()
        self.assertIsNotNone(result)

    def test_insert_or_check_identical_with_existing(self):
        test_person = {
            "id": uuid.uuid4(),
            "sex": "other",
            "year_of_birth": 1999,
        }
        self.dao.insert("person", test_person)
        self.assert_entity_exists_with_properties("person", **test_person)
        self.dao.insert_or_check_identical("person", test_person)
        self.assert_entity_exists_with_properties("person", **test_person)

    def test_insert_or_check_identical_with_new(self):
        test_person = {
            "id": uuid.uuid4(),
            "sex": "other",
            "year_of_birth": 1999,
        }
        self.dao.insert("person", test_person)
        self.dao.insert_or_check_identical("person", test_person)
        self.assert_entity_exists_with_properties("person", **test_person)

    def test_insert_or_check_identical_with_mismatch(self):
        test_person = {
            "id": uuid.uuid4(),
            "sex": "other",
            "year_of_birth": 1999,
        }
        self.dao.insert("person", test_person)
        self.assert_entity_exists_with_properties("person", **test_person)
        test_person["year_of_birth"] = 2000
        with self.assertRaises(Exception):
            self.assert_entity_exists_with_properties("person", **test_person)

    def test_insert_or_check_identical_with_multipart_primary_key(self):
        test_sourcestudy = {
            "name": "Test Study",
            "start_year": 2000,
            "end_year": 2000,
            "notes": None,
        }
        test_collaborator = {
            "id": uuid.uuid4(),
            "name": "Test Collaborator",
        }
        self.dao.insert("sourcestudy", test_sourcestudy)
        self.dao.insert("collaborator", test_collaborator)

        test_sourcestudycollaborator = {
            "collaborator_id": test_collaborator["id"],
            "study_name": test_sourcestudy["name"],
        }
        self.dao.insert_or_check_identical(
            "sourcestudycollaborator",
            test_sourcestudycollaborator,
        )
        self.assert_entity_exists_with_properties(
            "sourcestudycollaborator",
            **test_sourcestudycollaborator,
        )
        self.dao.insert_or_check_identical(
            "sourcestudycollaborator",
            test_sourcestudycollaborator,
        )
        # NOTE(nknight): None of the tables with multiple primary keys have
        # other fields, so the "check identical" function of this method
        # doesn't really apply. Any value that's different from the existing
        # value is a legitimate new value, and would be inserted.
