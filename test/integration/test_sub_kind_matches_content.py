"""Validate the logic in the Substitution table's check constraint

The constraint is meant to ensure that data in the record is consistent with
the kind of the record (i.e. simple, insertion, and deletion records contain
the data for substitutions, insertions, and deletions respectively.)
"""
import tempfile
import unittest
import uuid

import sqlalchemy as sa

from shared_schema import dao


class BaseDaoTest(unittest.TestCase):
    def setUp(self):
        self.db_file = tempfile.NamedTemporaryFile()
        db_url = f"sqlite:///{self.db_file.name}"
        self.dao = dao.DAO(db_url)
        self.dao.init_db()
        self.fixtures = self.get_fixtures()
        for nm, ent in self.fixtures.items():
            self.dao.insert(nm, ent)

    @staticmethod
    def get_fixtures():
        fixtures = {}
        fixtures["isolate"] = {"id": uuid.uuid4(), "type": "clinical"}
        fixtures["sequence"] = {
            "id": uuid.uuid4(),
            "isolate_id": fixtures["isolate"]["id"],
            "genotype": None,
            "subgenotype": None,
            "strain": None,
            "seq_method": "sanger",
            "cutoff": 0.05,
            "raw_nt_seq": "fake sequence",
        }
        fixtures["referencesequence"] = {
            "id": uuid.uuid4(),
            "name": "fake refseq name",
            "genebank": "fake_genbank_id",
            "nt_seq": "fake sequence",
        }
        fixtures["alignment"] = {
            "id": uuid.uuid4(),
            "sequence_id": fixtures["sequence"]["id"],
            "reference_id": fixtures["referencesequence"]["id"],
            "nt_start": 587,
            "nt_end": 1583,
            "gene": "ns3",
        }
        return fixtures


class TestConstraintAcceptance(BaseDaoTest):

    cases = [
        {"kind": "simple", "sub_aa": "h"},
        {"kind": "insertion", "insertion": "gattaca"},
        {"kind": "deletion", "deletion_length": 3},
    ]

    def test_acceptable_entities(self):
        for values in self.cases:
            ent = {
                "alignment_id": self.fixtures["alignment"]["id"],
                "position": 123,
                **values,
            }
            self.dao.insert("substitution", ent)
            self.dao.command(self.dao.substitution.delete())


class TestContraintRejection(BaseDaoTest):

    incomplete_cases = [
        {"kind": "simple"},
        {"kind": "insertion"},
        {"kind": "deletion"},
    ]

    def test_incomplete_entities(self):
        for values in self.incomplete_cases:
            ent = {
                "alignment_id": self.fixtures["alignment"]["id"],
                "position": "123",
                **values,
            }
            with self.assertRaises(sa.exc.IntegrityError):
                self.dao.insert("substitution", ent)

    incompatible_cases = [
        {"kind": "simple", "insertion": "gattaca"},
        {"kind": "simple", "deletion_length": 10},
        {"kind": "insertion", "sub_aa": "h"},
        {"kind": "insertion", "deletion_length": 10},
        {"kind": "deletion", "sub_aa": "g"},
        {"kind": "deletion", "insertion": "gattaca"},
    ]

    def test_incompatible_values(self):
        for values in self.incompatible_cases:
            ent = {
                "alignment_id": self.fixtures["alignment"]["id"],
                "position": "123",
                **values,
            }
            with self.assertRaises(sa.exc.IntegrityError):
                self.dao.insert("substitution", ent)
