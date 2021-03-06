"""Test the hashable, equable, canonical regimen data object"""

import collections
import decimal
import unittest
import unittest.mock as mock
import uuid

import pypeg2 as pp

import shared_schema.regimens.cannonical as cannonical
import shared_schema.regimens.grammar as rg

# ---------------------------------------------------------------------
# Helpers


def methods_exist(obj):
    """Verify that __eq__ and __hash__ exist on an object"""
    method_names = ("__eq__", "__hash__")
    obj_methods = dir(obj)
    msg = "Expected '{}' to have {} method"
    msg.format(obj, ", ".join(method_names))
    return (all(nm in obj_methods for nm in method_names), msg)


def equivalent(a, b):
    """Verify that two objects are equal and have the same hash"""
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
dcv_dose = cannonical._dose(amount=decimal.Decimal(1), compound="dcv")
sof_dose = cannonical._dose(amount=decimal.Decimal(2), compound="sof")
boc_dose = cannonical._dose(amount=decimal.Decimal(3), compound="boc")

duration_12wks = decimal.Decimal(12 * 7)
duration_24wks = decimal.Decimal(24 * 7)

# ---------------------------------------------------------------------
# Data Object Construction


class TestParsingCompoundObjects(unittest.TestCase):
    def test_dose(self):
        src = "1mg dcv"
        parsed = parse_from_source(src, rg.Dose)
        self.assertTrue(*methods_exist(parsed))
        self.assertEqual(parsed, dcv_dose)

    def test_indication(self):
        src = "1mg dcv + 2mg sof qd"
        parsed = parse_from_source(src, rg.Indication)
        self.assertTrue(*methods_exist(parsed))
        self.assertEqual(
            parsed,
            cannonical._indication(
                frequency="qd", doselist=frozenset([dcv_dose, sof_dose])
            ),
        )

    def test_regimenpart(self):
        src = "2mg sof qd 12 weeks"
        parsed = parse_from_source(src, rg.RegimenPart)
        self.assertTrue(*methods_exist(parsed))
        self.assertEqual(
            parsed,
            cannonical._regimen_part(
                duration=duration_12wks,
                drug_combination=frozenset(
                    [
                        cannonical._indication(
                            frequency="qd", doselist=frozenset([sof_dose])
                        )
                    ]
                ),
            ),
        )


class TestParsingCollections(unittest.TestCase):
    def test_doselist_parses(self):
        src = "1mg dcv + 3mg boc"
        parsed = parse_from_source(src, rg.DoseList)
        self.assertIsInstance(parsed, frozenset)
        self.assertTrue(*methods_exist(parsed))
        self.assertEqual(parsed, frozenset([dcv_dose, boc_dose]))

    def test_doselist_canonical(self):
        dl1 = parse_from_source("2mg dcv", rg.DoseList)
        dl2 = parse_from_source("1mg dcv + 1mg dcv", rg.DoseList)
        self.assertTrue(*methods_exist(dl1))
        self.assertTrue(*methods_exist(dl2))
        self.assertTrue(*equivalent(dl1, dl2))

    def test_drugcombination(self):
        parsed = parse_from_source(
            "1mg dcv qd & 3mg boc tid", rg.DrugCombination
        )
        self.assertIsInstance(parsed, frozenset)
        self.assertTrue(*methods_exist(parsed))
        self.assertEqual(
            parsed,
            frozenset(
                [
                    cannonical._indication(
                        doselist=frozenset([dcv_dose]), frequency="qd"
                    ),
                    cannonical._indication(
                        doselist=frozenset([boc_dose]), frequency="tid"
                    ),
                ]
            ),
        )

    def test_regimen(self):
        parsed = parse_from_source(
            "(1mg dcv + 2mg sof) qd 12 week, 3mg boc qd 24 weeks", rg.Regimen
        )
        self.assertIsInstance(parsed, frozenset)
        self.assertTrue(*methods_exist(parsed))
        self.assertEqual(
            parsed,
            frozenset(
                [
                    cannonical._regimen_part(
                        duration=duration_12wks,
                        drug_combination=frozenset(
                            [
                                cannonical._indication(
                                    frequency="qd",
                                    doselist=frozenset([dcv_dose, sof_dose]),
                                )
                            ]
                        ),
                    ),
                    cannonical._regimen_part(
                        duration=duration_24wks,
                        drug_combination=frozenset(
                            [
                                cannonical._indication(
                                    frequency="qd",
                                    doselist=frozenset([boc_dose]),
                                )
                            ]
                        ),
                    ),
                ]
            ),
        )


class TestMonoidalOperations(unittest.TestCase):

    # NOTE(nknight): Skip testing cannonical.key; it's just an accessor

    dose_a1 = cannonical._dose(amount=1, compound="test")
    dose_a2 = cannonical._dose(amount=2, compound="test")
    dose_b1 = cannonical._dose(amount=1, compound="other test")

    druglist_a = frozenset([dose_a1])
    druglist_b = frozenset([dose_b1])
    druglist_ab = frozenset([dose_a1, dose_b1])

    indication_a = cannonical._indication(frequency="qd", doselist=druglist_a)
    indication_b = cannonical._indication(frequency="qd", doselist=druglist_b)
    indication_ab = cannonical._indication(
        frequency="qd", doselist=druglist_ab
    )

    def test_dose_add(self):
        self.assertEqual(
            cannonical.add(self.dose_a1, self.dose_a2),
            cannonical._dose(amount=3, compound="test"),
        )
        with self.assertRaises(ValueError):
            cannonical.add(self.dose_a1, self.dose_b1)

    def test_indication_add(self):
        key_mismatch_indication = cannonical._indication(
            frequency="qwk", doselist=self.druglist_a
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
            duration=decimal.Decimal(1), drug_combination=drugcombo_a
        )
        regpart_b = cannonical._regimen_part(
            duration=decimal.Decimal(1), drug_combination=drugcombo_b
        )
        regpart_ab = cannonical._regimen_part(
            duration=decimal.Decimal(1), drug_combination=drugcombo_ab
        )
        keymismatch_regpart = cannonical._regimen_part(
            duration=decimal.Decimal(2), drug_combination=drugcombo_a
        )
        self.assertEqual(cannonical.add(regpart_a, regpart_b), regpart_ab)
        with self.assertRaises(ValueError):
            cannonical.add(regpart_a, keymismatch_regpart)

    def test_consolidating_insert(self):
        self.assertEqual(
            cannonical.consolidating_insert(self.druglist_a, self.dose_b1),
            self.druglist_ab,
        )
        self.assertEqual(
            cannonical.consolidating_insert(self.druglist_a, self.dose_a1),
            frozenset([self.dose_a2]),
        )
        self.assertEqual(
            cannonical.consolidating_insert(self.druglist_ab, self.dose_a1),
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
        src = "SOVALDI"
        parsed = cannonical.from_string(src)
        self.is_regimen(parsed)

    def test_parse_regimen(self):
        src = (
            "(200mg sof + 800mg dcv) qd & 100mg boc tid 2 weeks, "
            "1mg par qwk 11days"
        )
        parsed = cannonical.from_string(src)
        self.is_regimen(parsed)

    def test_error(self):
        src = "ill-formed regimen"
        with self.assertRaises(SyntaxError):
            cannonical.from_string(src)


fake_result = collections.namedtuple(
    "RowProxy", ["dose", "medication_id", "frequency", "duration"]
)


class TestFromDao(unittest.TestCase):

    doses = {
        "sof100": cannonical._dose(amount=100, compound="sof"),
        "dcv100": cannonical._dose(amount=100, compound="dcv"),
    }

    indications = {
        "sof100qd": cannonical._indication(
            frequency="qd", doselist=frozenset([doses["sof100"]])
        ),
        "sof100tid": cannonical._indication(
            frequency="tid", doselist=frozenset([doses["sof100"]])
        ),
        "dcv100qd": cannonical._indication(
            frequency="qd", doselist=frozenset([doses["dcv100"]])
        ),
    }

    def verify_loaded(self, loaded, expected):
        query_mock = mock.Mock(return_value=loaded)
        dao_mock = mock.Mock()
        dao_mock.query = query_mock

        uid = uuid.uuid4()
        sql_mod = "shared_schema.regimens.cannonical.sql"
        with mock.patch(sql_mod):
            result = cannonical.from_dao(dao_mock, uid)
        query_mock.assert_called()
        self.assertEqual(result, expected)

    def test_simple_load(self):
        loaded = [
            fake_result(
                dose=100, medication_id="sof", frequency="qd", duration=10
            )
        ]
        expected = frozenset(
            [
                cannonical._regimen_part(
                    duration=10,
                    drug_combination=frozenset([self.indications["sof100qd"]]),
                )
            ]
        )
        self.verify_loaded(loaded, expected)

    def test_merging_indication_load(self):
        loaded = [
            fake_result(
                dose=100, medication_id="sof", frequency="qd", duration=10
            ),
            fake_result(
                dose=100, medication_id="sof", frequency="tid", duration=10
            ),
        ]
        expected = frozenset(
            [
                cannonical._regimen_part(
                    duration=10,
                    drug_combination=frozenset(
                        [
                            self.indications["sof100qd"],
                            self.indications["sof100tid"],
                        ]
                    ),
                )
            ]
        )
        self.verify_loaded(loaded, expected)


class TestInclusions(unittest.TestCase):
    def test_simple_inclusions(self):
        drug_src = "100mg sof bid 2 weeks"
        regimen = parse_from_source(drug_src, rg.Regimen)
        inclusion = next(cannonical.drug_inclusions(regimen))
        self.assertEqual(inclusion.medication_id, "sof")
        self.assertEqual(inclusion.dose, 100)
        self.assertEqual(inclusion.frequency, "bid")
        self.assertEqual(inclusion.duration, 14)

    def test_multiple_indication_inclusion(self):
        drug_src = "100mg sof + 200mg dcv bid 1 day"
        regimen = parse_from_source(drug_src, rg.Regimen)
        inclusions = cannonical.drug_inclusions(regimen)
        for incl in inclusions:
            self.assertEqual(incl.frequency, "bid")
            if incl.medication_id == "sof":
                self.assertEqual(incl.dose, 100)
            elif incl.medication_id == "dcv":
                self.assertEqual(incl.dose, 200)
            else:
                self.fail("unexpected inclusion: {}".format(incl))

    def test_multiple_duration_inclusion(self):
        drug_src = "100mg sof qwk 1 day, 200mg dcv tid 2 days"
        regimen = parse_from_source(drug_src, rg.Regimen)
        inclusions = cannonical.drug_inclusions(regimen)
        for incl in inclusions:
            if incl.medication_id == "sof":
                self.assertEqual(incl.dose, 100)
                self.assertEqual(incl.duration, 1)
                self.assertEqual(incl.frequency, "qwk")
            elif incl.medication_id == "dcv":
                self.assertEqual(incl.dose, 200)
                self.assertEqual(incl.duration, 2)
                self.assertEqual(incl.frequency, "tid")
            else:
                self.fail("unexpected inclusions: {}".format(incl))
