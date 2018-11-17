import tempfile
import unittest

import shared_schema.dao
import shared_schema.regimens


class TestCannonicalRegimenFromDao(unittest.TestCase):
    def new_initialized_dao(self):
        self.tmp_dbfile = tempfile.NamedTemporaryFile()
        db_url = f"sqlite:///{self.tmp_dbfile.name}"
        dao = shared_schema.dao.DAO(db_url)
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
        regimens = list(dao.query(dao.regimen.select()))
        self.assertGreater(
            len(regimens), 0, "Expected to have some standard regimens"
        )
        for reg in regimens:
            self.verify_that_standard_matches_loaded(dao, reg.name, reg.id)
