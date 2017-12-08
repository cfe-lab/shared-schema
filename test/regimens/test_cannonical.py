'''Test the hashable, equable, canonical regimen data object'''

import collections
import decimal
import unittest
import unittest.mock as mock
import uuid

import pypeg2 as pp

import shared_schema.regimens.grammar as rg
import shared_schema.regimens.cannonical as cannonical


# ---------------------------------------------------------------------
# Helpers

def methods_exist(obj):
    '''Verify that __eq__ and __hash__ exist on an object'''
    method_names = ('__eq__', '__hash__')
    obj_methods = dir(obj)
    msg = "Expected '{}' to have {} method"
    msg.format(obj, ", ".join(method_names))
    return (all(nm in obj_methods for nm in method_names), msg)


def equivalent(a, b):
    '''Verify that two objects are equal and have the same hash'''
    if a != b:
        msg = "Expected {} == {}"
        return (False, msg.format(a, b))
    if hash(a) != hash(b):
        msg = "Expected hash({}) == hash({})"
        return (False, msg.format(a, b))
    return True, ""


def parse_from_source(src, grammar_node):
    grammar_obj = pp.parse(src, grammar_node)
    parsed = cannonical.parse(grammar_obj)
    return parsed


# ---------------------------------------------------------------------
# Example Data
dcv_dose = cannonical._dose(amount=decimal.Decimal(1), compound='DCV')
sof_dose = cannonical._dose(amount=decimal.Decimal(2), compound='SOF')
boc_dose = cannonical._dose(amount=decimal.Decimal(3), compound='BOC')

duration_12wks = decimal.Decimal(12 * 7)
duration_24wks = decimal.Decimal(24 * 7)


# ---------------------------------------------------------------------
# Data Object Construction

class TestParsingCompoundObjects(unittest.TestCase):

    def test_dose(self):
        src = "1mg DCV"
        parsed = parse_from_source(src, rg.Dose)
        self.assertTrue(*methods_exist(parsed))
        self.assertEqual(parsed, dcv_dose)

    def test_indication(self):
        src = "1mg DCV + 2mg SOF QD"
        parsed = parse_from_source(src, rg.Indication)
        self.assertTrue(*methods_exist(parsed))
        self.assertEqual(
            parsed,
            cannonical._indication(
                frequency="QD",
                doselist=frozenset([dcv_dose, sof_dose]),
            ),
        )

    def test_regimenpart(self):
        src = "2mg SOF QD 12 weeks"
        parsed = parse_from_source(src, rg.RegimenPart)
        self.assertTrue(*methods_exist(parsed))
        self.assertEqual(
            parsed,
            cannonical._regimen_part(
                duration=duration_12wks,
                drug_combination=frozenset([
                    cannonical._indication(
                        frequency='QD',
                        doselist=frozenset([sof_dose]),
                    )
                ]),
            )
        )


class TestParsingCollections(unittest.TestCase):

    def test_doselist_parses(self):
        src = "1mg DCV + 3mg BOC"
        parsed = parse_from_source(src, rg.DoseList)
        self.assertIsInstance(parsed, frozenset)
        self.assertTrue(*methods_exist(parsed))
        self.assertEqual(
            parsed,
            frozenset([dcv_dose, boc_dose]),
        )

    def test_doselist_canonical(self):
        dl1 = parse_from_source("2mg DCV", rg.DoseList)
        dl2 = parse_from_source("1mg DCV + 1mg DCV", rg.DoseList)
        self.assertTrue(*methods_exist(dl1))
        self.assertTrue(*methods_exist(dl2))
        self.assertTrue(*equivalent(dl1, dl2))

    def test_drugcombination(self):
        parsed = parse_from_source(
            "1mg DCV QD & 3mg BOC TID",
            rg.DrugCombination,
        )
        self.assertIsInstance(parsed, frozenset)
        self.assertTrue(*methods_exist(parsed))
        self.assertEqual(
            parsed,
            frozenset([
                cannonical._indication(
                    doselist=frozenset([dcv_dose]),
                    frequency="QD",
                ),
                cannonical._indication(
                    doselist=frozenset([boc_dose]),
                    frequency="TID",
                ),
            ]),
        )

    def test_regimen(self):
        parsed = parse_from_source(
            "(1mg DCV + 2mg SOF) QD 12 week, 3mg BOC QD 24 weeks",
            rg.Regimen,
        )
        self.assertIsInstance(parsed, frozenset)
        self.assertTrue(*methods_exist(parsed))
        self.assertEqual(
            parsed,
            frozenset([
                cannonical._regimen_part(
                    duration=duration_12wks,
                    drug_combination=frozenset([
                        cannonical._indication(
                            frequency='QD',
                            doselist=frozenset([dcv_dose, sof_dose]),
                        )
                    ]),
                ),
                cannonical._regimen_part(
                    duration=duration_24wks,
                    drug_combination=frozenset([
                        cannonical._indication(
                            frequency='QD',
                            doselist=frozenset([boc_dose]),
                        )
                    ]),
                )
            ]),
        )


class TestMonoidalOperations(unittest.TestCase):

    # NOTE(nknight): Skip testing cannonical.key; it's just an accessor

    dose_a1 = cannonical._dose(amount=1, compound='test')
    dose_a2 = cannonical._dose(amount=2, compound='test')
    dose_b1 = cannonical._dose(amount=1, compound='other test')

    druglist_a = frozenset([dose_a1])
    druglist_b = frozenset([dose_b1])
    druglist_ab = frozenset([dose_a1, dose_b1])

    indication_a = cannonical._indication(
        frequency='QD',
        doselist=druglist_a,
    )
    indication_b = cannonical._indication(
        frequency='QD',
        doselist=druglist_b,
    )
    indication_ab = cannonical._indication(
        frequency='QD',
        doselist=druglist_ab,
    )

    def test_dose_add(self):
        self.assertEqual(
            cannonical.add(self.dose_a1, self.dose_a2),
            cannonical._dose(amount=3, compound='test'),
        )
        with self.assertRaises(ValueError):
            cannonical.add(self.dose_a1, self.dose_b1)

    def test_indication_add(self):
        key_mismatch_indication = cannonical._indication(
            frequency='QWK',
            doselist=self.druglist_a,
        )
        self.assertEqual(
            cannonical.add(self.indication_a, self.indication_b),
            self.indication_ab,
        )
        with self.assertRaises(ValueError):
            cannonical.add(self.indication_a, key_mismatch_indication)

    def test_regimen_part_add(self):
        drugcombo_a = frozenset([self.indication_a])
        drugcombo_b = frozenset([self.indication_b])
        drugcombo_ab = frozenset([self.indication_ab])
        regpart_a = cannonical._regimen_part(
            duration=decimal.Decimal(1),
            drug_combination=drugcombo_a,
        )
        regpart_b = cannonical._regimen_part(
            duration=decimal.Decimal(1),
            drug_combination=drugcombo_b,
        )
        regpart_ab = cannonical._regimen_part(
            duration=decimal.Decimal(1),
            drug_combination=drugcombo_ab,
        )
        keymismatch_regpart = cannonical._regimen_part(
            duration=decimal.Decimal(2),
            drug_combination=drugcombo_a,
        )
        self.assertEqual(
            cannonical.add(regpart_a, regpart_b),
            regpart_ab,
        )
        with self.assertRaises(ValueError):
            cannonical.add(regpart_a, keymismatch_regpart)

    def test_consolidating_insert(self):
        self.assertEqual(
            cannonical.consolidating_insert(
                self.druglist_a,
                self.dose_b1,
            ),
            self.druglist_ab,
        )
        self.assertEqual(
            cannonical.consolidating_insert(
                self.druglist_a,
                self.dose_a1,
            ),
            frozenset([self.dose_a2]),
        )
        self.assertEqual(
            cannonical.consolidating_insert(
                self.druglist_ab,
                self.dose_a1,
            ),
            frozenset([self.dose_a2, self.dose_b1]),
        )


# ---------------------------------------------------------------------
# Integrated Parsing


class TestFromString(unittest.TestCase):

    def is_regimen(self, parsed):
        self.assertIsInstance(parsed, frozenset)
        reg_part = next(iter(parsed))
        self.assertIsInstance(reg_part, cannonical._regimen_part)

    def test_parse_standard_reg(self):
        src = 'SOVALDI'
        parsed = cannonical.from_string(src)
        self.is_regimen(parsed)

    def test_parse_regimen(self):
        src = ("(200mg SOF + 800mg DCV) QD & 100mg BOC TID 2 weeks, "
               "1mg PAR QWK 11days")
        parsed = cannonical.from_string(src)
        self.is_regimen(parsed)

    def test_error(self):
        src = 'ill-formed regimen'
        with self.assertRaises(SyntaxError):
            cannonical.from_string(src)


fake_result = collections.namedtuple(
    'RowProxy',
    ['dose', 'medication_id', 'frequency', 'duration'],
)


class TestFromDao(unittest.TestCase):

    doses = {
        'sof100': cannonical._dose(amount=100, compound='SOF'),
        'dcv100': cannonical._dose(amount=100, compound='DCV'),
    }

    indications = {
        'sof100qd': cannonical._indication(
            frequency='QD',
            doselist=frozenset([doses['sof100']]),
        ),
        'sof100tid': cannonical._indication(
            frequency='TID',
            doselist=frozenset([doses['sof100']]),
        ),
        'dcv100qd': cannonical._indication(
            frequency='QD',
            doselist=frozenset([doses['dcv100']]),
        )
    }

    def verify_loaded(self, loaded, expected):
        fetch_mock = mock.Mock()
        fetch_mock.fetchall = mock.Mock(return_value=loaded)
        exec_mock = mock.Mock(return_value=fetch_mock)
        dao_mock = mock.Mock()
        dao_mock.execute = exec_mock

        uid = uuid.uuid4()
        sql_mod = 'shared_schema.regimens.cannonical.sql'
        with mock.patch(sql_mod) as sa_sql_mock:
            result = cannonical.from_dao(dao_mock, uid)
            sa_sql_mock.select.assert_called()
        exec_mock.assert_called()
        fetch_mock.fetchall.assert_called()
        self.assertEqual(result, expected)

    def test_simple_load(self):
        loaded = [
            fake_result(
                dose=100,
                medication_id='SOF',
                frequency='QD',
                duration=10,
            )
        ]
        expected = frozenset([
            cannonical._regimen_part(
                duration=10,
                drug_combination=frozenset([
                    self.indications['sof100qd'],
                ]),
            )
        ])
        self.verify_loaded(loaded, expected)

    def test_merging_indication_load(self):
        loaded = [
            fake_result(
                dose=100,
                medication_id='SOF',
                frequency='QD',
                duration=10,
            ),
            fake_result(
                dose=100,
                medication_id='SOF',
                frequency='TID',
                duration=10,
            ),
        ]
        expected = frozenset([
            cannonical._regimen_part(
                duration=10,
                drug_combination=frozenset([
                    self.indications['sof100qd'],
                    self.indications['sof100tid'],
                ]),
            ),
        ])
        self.verify_loaded(loaded, expected)
