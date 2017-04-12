#encoding: utf8
import collections
import re

# Data Parsing

entity = collections.namedtuple("entity", ["name", "description", "fields"])
field = collections.namedtuple("field", ["name", "type", "description"])


def foreign_key_target(field_type):
    '''What entity does a foreign key target?'''
    matches = re.findall("\((.+)\)", field_type)
    return matches[0]


class Schema(object):

    types = {"integer", "float", "string", "foreign key", "date",
             "year", "uuid", "enum", "bool"}

    def __init__(self, raw_entities):
        self.raw_entities = raw_entities
        self.entities = {e.name: e for e in raw_entities}
        err_msg = "Duplicate entities?"
        assert len(self.entities) == len(self.raw_entities), err_msg
        types = (f.type for e in self.entities.values() for f in e.fields)
        for t in types:
            err_msg = "invalid type: {}".format(t)
            assert self.type_is_valid(t, self.entities), err_msg

    @property
    def relationships(self):
        rels = set()
        for ename, entity in self.entities.items():
            types = (f.type for f in entity.fields)
            foreign_keys = [t for t in types if "foreign key" in t]
            targets = [foreign_key_target(f) for f in foreign_keys]
            for target in targets:
                rel = (entity.name, target)
                rels.add(rel)
        return rels

    @classmethod
    def type_is_valid(cls, t, entities):
        known_type = t in cls.types
        fk = "foreign key" in t
        enum = "enum" in t
        if not (known_type or fk or enum):
            return False
        elif fk:
            fk_target = foreign_key_target(t)
            err_msg = "invalid foreign key target: {}".format(fk_target)
            assert  fk_target in entities, err_msg
            return True
        else:
            return True

# TODO(nknight): Unify patient and person

schema_data = Schema([

    entity(
        "Collaborator",
        "A collaborating site (provides patient data)",
        [field("id", "uuid", "Unique identifier"),
         field("name", "string", "Name of the collaborating entity"),
         # TODO(nknight): figure out how to represent location (how accurate do we need to be?)
         field("location", "string", "The collaborator's physical location"),
         ]),

    # ==================================================
    # Patient Data
    entity(
        "Person",
        "A study participant",
        [field("id", "uuid", "Unique identifier"),
        ]),

    # TODO(nknight): Center? (as distrinct from collaborator)

    entity(
        "Drug",
        "A drug taken by a participant",
        [field("id", "uuid", "Unique identifier"),
         field("name", "string", "The drug's name"),
         # TODO(nknight): some kind of key to a drug db?
        ]),

    entity(
        "ClinicalData",
        "Diagnostic information about a participant",
        [field("id", "uuid", "Unique identifier"),
         field("patient_id", "foreign key (Person)", "The patient to whom the data pertains"),
         field("collaborator_id", "foreign key (Collaborator)", "The source of the data"),
         field("date_collected", "date", "Date the data was collected"),
         # TODO(nknight): clinical fields 😱
         # TODO(nknight): separate lab results table?
        ]),

    entity(
        "DemographicData",
        "Demographic information about a participant",
        [field("id", "uuid", "Unique identifier"),
         field("patient_id", "foreign key (Person)", "The patient to whom the data pertains"),
         field("collaborator_id", "foreign key (Collaborator)", "The source of the data"),
         field("date_collected", "date", "The date this data was collected"),
         field("date_of_birth", "date", "Participant's date of birth"),
         field("highest_education", "enum(...)", "Participant's highest level of education to date"),
         # TODO(nknight): think carefully about this, consult
         field("gender", "enum (cis-male, cis-female, trans-male, trans-female, other)", ""),
         # TODO(nknight): construct these enums
         field("sexual_orientation", "enum (...)", "Participant's sexual orientation"),
         field("ethnicity", "enum (...)", ""),
         # TODO(nknight): exposure
         # TODO(nknight): seroconversion
         # TODO(nknight): comorbid conditions
         field("depression", "bool", "Has the patient ever been diagnosed with depression"),
         field("idu", "bool", "History of injection drug use? (ever)"),
         field("idu_first", "year", "Year of first injection drug use"),
         field("idu_last", "date", "Date of most recent injection drug use"),
         # TODO(nknight): idu other fields (sharing, ...)
         # TODO(nknight): alcohol
         # TODO(nknight): sexual activity
         # TODO(nknight): opiod use
        ]),

    # TODO(nknight): split behavioural data?

    entity(
        "TreatmentData",
        "Information about a participant's treatment",
        [field("id", "uuid", "Unique identifier"),
         field("patient_id", "foreign key (Person)", "Patient to whom the data pertains"),
         field("collaborator_id", "foreign key (Collaborator)", "Collaborator who collected this data"),
         field("start_dt", "date", "Schedule treatment start date"),
         field("end_dt", "date", "Scheduled treatment end date"),
         # TODO(nknight): response fields
         # TODO(nknight): adherance?
         # TODO(nknight): outcome
         # TODO(nknight): modifications
        ]),

    entity(
        "TreatmentDrugData",
        "How much and what kind of a drug was included in a treatment regimen",
        [field("treatment_id", "foreign key (TreatmentData)", "Which treatment this prescription was included in"),
         field("drug_id", "foreign key (Drug)", "Which drug was prescribed"),
         field("dosage", "integer", "Dosage of the drug perscribed (in μg)"),
         # TODO(nknight): frequency? (sustained prescriptions + single administrations)
        ]),

    
    # TODO(nknight): death and last followup entity


    # ==================================================
    # References

    entity(
        "Reference",
        "A reference to a publication",
        [field("id", "uuid", "Unique id"),
         field("author", "string", ""),
         field("title", "string", ""),
         field("journal", "string", ""),
         field("pubmed_id", "string", ""),
         field("published", "bool", ""),
        ]),
    # QUESTION(nknight): reflink (to display on website?)
    # TODO(nknight): other kinds of reference (other than pubmed)


    # ==================================================
    # Isolates & Sequences

    entity(
        "Isolate",
        "Virus isolate (from an individual or used in a lab experiment)",
        [field("id", "uuid", "Unique id"),
         field("isolation_date", "date", "Date the virus was isoated"),
         field("type", "enum (clinical, lab)", "The kind of isolate. (extra data available depending on kind "),
        ]),
    # TODO(nknight): external references for isolates?
    # QUESTION(nknight): Do we need a type for constructed isolates?
    # QUESTION(nknight): Do isolates have a single viral component (e.g. do we need to handle multiple genotypes per isolate)?
    # TODO(nknight): How do we record genotyp/subtype information?

    entity(
        "ClinicalIsolate",
        "Isolate information",
        [field("isolate_id", "foreign key (Isolate)", "The isolate this data pertains to"),
         field("patient_id", "foreign key (Person)", "The patient who gave the isolate"),
         # QUESTION(nknight): clinical isolate fields
        ]),

    # QUESTION(nknight): Do lab isolates come from patients?

    entity(
        "LabIsolate",
        "Isolates created in the lab",
        [field("isolate_id", "foreign key (Isolate)", "The isolate this data pertains to"),
         field("mutations", "string", "A list of the mutations applied to the isolate"),  # TODO(nknight): better data typ?e
        ]),

    entity(
        "Sequence",
        "Sequences and data needed for rapid alignment",
        [field("id", "uuid", "Unique identifier"),
         field("isolate_id", "foreign key (Isolate)", "Isolate the sequence was obtained from"),
         # TODO(nknight): sequence fields
        ]),

    # QUESTION(nknight): sequence types?


    # ==================================================
    # Susceptibility results

    entity(
        "SusceptibilityResult",
        "Drug susceptibility test results",
        [field("id", "uuid", "Unique id"),
         field("isolate_id", "foreign key (Isolate)", "The isolate being tested"),
         field("reference_id", "foreign key (Reference)", "Source (if applicable)"),
         field("drug_id", "foreign key (Drug)", "The drug being tested"),
         field("method_id", "foreign key (SusceptibilityMethod)", "Name of the susceptibility test method"),
         field("result", "float", "Drug concentration required for in hibition (in nM)"), # QUESTION(nknight): precision?
         field("result_bound", "enum (<, =, >)", ""),
         field("IC", "enum (50, 90, 95)", "% inhibition"),
         field("fold", "float", "Fold-change compared to wild type"),
         field("fold_bound", "enum (<, = >)", ""),
        ]),

    entity(
        "SusceptibilityMethod",
        "Susceptibility testing methods",
        [field("id", "uuid", "Unique id"),
         field("reference_id", "foreign key (Reference)", "Reference describing the method"),
         field("notes", "string", "Free-text notes about the testing method"),
        ]),

])
