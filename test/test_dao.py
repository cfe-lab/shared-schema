import unittest
import uuid

from shared_schema import dao


class TestUuidType(unittest.TestCase):

    def test_serialization_and_deserialization(self):
        for i in range(10000):
            u = uuid.uuid4()
            s = dao.UUID.as_str(u)
            assert uuid.UUID(s) == u


class TestDaoOperations(unittest.TestCase):
    '''Verify that saving, loading, and querying work as expected'''

    @classmethod
    def setUpClass(cls):
        cls.dao = dao.DAO('sqlite:///:memory:', echo=False)
        cls.dao.init_db()

    def test_insert_retrieve(self):
        test_person = {
            'id': uuid.uuid4(),
            'country': 'test_country',
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
