import unittest

import shared_schema.dao
import shared_schema.regimens


class TestCannonicalRegimenFromDao(unittest.TestCase):

    def new_initialized_dao(self):
        dao = shared_schema.dao.DAO("sqlite:///:memory:")
        dao.init_db()
        dao.load_standard_regimens()
        return dao

    def verify_that_standard_matches_loaded(self, dao, reg_name, reg_id):
        standard_str = shared_schema.regimens.standard.regimens[reg_name]
        standard = shared_schema.regimens.cannonical.from_string(standard_str)
        loaded = shared_schema.regimens.cannonical.from_dao(dao, reg_id)
        self.assertEqual(standard, loaded)

    def test_integration_from_dao_works_as_expected(self):
        dao = self.new_initialized_dao()
        regimens = dao.execute(dao.regimen.select()).fetchall()
        self.assertGreater(
            len(regimens),
            0,
            "Expected to have some standard regimens",
        )
        for reg in regimens:
            self.verify_that_standard_matches_loaded(
                dao,
                reg.name,
                reg.id,
            )
