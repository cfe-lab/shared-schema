#encoding: utf8

import collections

import schema.util as util


# Data Parsing

entity = collections.namedtuple("entity", ["name", "description", "fields"])
field = collections.namedtuple("field", ["name", "type", "description"])


class Schema(object):

    types = {"integer", "float", "string", "foreign key", "date",
             "uuid", "enum", "bool"}

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
            targets = [util.foreign_key_target(f) for f in foreign_keys]
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
            fk_target = util.foreign_key_target(t)
            err_msg = "invalid foreign key target: {}".format(fk_target)
            assert  fk_target in entities, err_msg
            return True
        else:
            return True


schema_data = Schema([

    entity(
        "Medication",
        "Anti-HCV drugs. Phenotypic resistance tests and treatment records reference this table.",
        [field("full_name", "string", "The medication's name"),
         field("short_name", "string", "The medication's three-letter abbreviation"),
        ]),

    # ==================================================
    # Collaborator and Study/Trial data

    entity(
        "Collaborator",
        "A collaborating site (provides participant data)",
        [field("id", "uuid", "Unique identifier"),
         field("name", "string", "Name of the collaborating entity"),
         field("country", "string", "The collaborator's physical location (country)"),
        ]),

    entity(
        "SourceStudy",
        "A study, trial, or other batch of data from a collaborator",
        [field("collaborator", "foreign key (Collaborator)", "The collaborator providing the data"),
         field("name", "string", "The name of the study or trial"),
         field("collection_start", "date", "The beginning of data collection"),
         field("collection_end", "date", "The end of data collection (if applicable)"),
         field("notes", "string", "Notes on data from this project"),
        ]),


    # ==================================================
    # Participant Data (demographic, clinical, behavioral, treatment)

    entity(
        "Person",
        "A study participant",
        [field("id", "uuid", "Unique identifier"),
         field("date_entered", "date", "Date the participant entered the study"),
         field("country", "string", "The country where the person participated in the study"),
         field("city", "string", "The city where the person participated in the study"),
         field("year_of_birth", "date", "Participant's year of birth"),
         field("sex", "enum(male, female, other)", "The participant's sex at birth"),
         field("ethnicity",
               "enum(black, caucasian, latino, native-north-american,"
               "east-asian, south-asian, southeast-asian)",
               "The participant's ethnicity"),
        ]),

    entity(
        "BehaviorData",
        "Behavioral information about a participant",
        [field("id", "uuid", "Unique identifier"),
         field("person_id", "foreign key (Person)", "The participant this data pertains to"),
         field(
             "study_id",
             "foreign key (SourceStudy)",
             "The study or trial that includes this information"),
         field("date_collected", "date", "The date this data was collected"),
         field("sexual_orientation", "enum (heterosexual, homosexual, bisexual, other)",
               "Participant's sexual orientation"),
         field("region", "string", "The participant's region of residence"),
         field("idu", "bool", "Injection drug use? (ever)"),
         field("ndu", "bool", "Non-injection drug use? (ever)"),
         field("idu_recent", "bool", "Injection drug use in the past 6 months?"),
         field("ndu_recent", "bool", "None-injection drug use in the past 6 months?"),
         field("prison", "bool", "Has the participant been in prison (ever)?"),
        ]),

    entity(
        "ClinicalTest",
        "Meta-data for clinical tests (e.g. viral-load assays, fibroscans, etc.)",
        [field("kind", "string", "The test's name"),
         field("unit", "string", "The unit the test's results are reported in"),
         field("detection_limit", "float", "The assay's detection limit"),
         field("notes", "string", "Additional notes regarding this test"),
        ]),

    entity(
        "TestResult",
        "Results of a participant's clinical tests",
        [field("person_id", "foreign key(Person)", "The participant the test was performed on"),
         field("study_id", "foreign key(SourceStudy)", "The study or trial that provided this data"),
         field("kind",
               "foreign key(ClinicalTest)",
               "The kind of test performed (e.g. viral-load assay, CTP assessment)"),
         field("date", "date", "The date of the test. For lab tests, the date the sample was taken"),
         field("result", "float", "The test's result"),
        ]),

    entity(
        "TreatmentData",
        "Information about a participant's treatment",
        [field("id", "uuid", "Unique identifier"),
         field("person_id", "foreign key (Person)", "The participant that this data pertains to"),
         field("study_id", "foreign key (SourceStudy)", "The study or trial this data comes from"),
         field("first_treatment", "bool", "Is this the first treatment "),
         field("start_dt", "date", "Schedule treatment start date"),
         field("end_dt_sch", "date", "Scheduled treatment end date"),
         field("duration_sch", "float", "Schedule treatment duration (weeks)"),
         field("end_dt_act", "date", "Actual treatment end date"),
         field("end_dt_bound", "enum(<, >, =)", "Uncertainty on 'end_dt_act'"),
         field(
             "pi",
             "bool",
             ("Has the participant ever been treated with pegylated interferon "
              "drugs before?")),
         field(
             "daa1",
             "bool",
             ("Has the participant ever been treated with first-line "
              "direct-acting antivirals drugs before?")),
         field(
             "daa2",
             "bool",
             ("Has the participant ever been treated with second-line "
              "direct-acting antiviral drugs before?")),
        ]),

    entity(
        "TreatmentMedicationData",
        "How much and what kind of medications were included in a treatment regimen",
        [field(
            "treatment_id",
            "foreign key (TreatmentData)",
            "Which treatment this prescription was included in"),
         field("medication_id", "foreign key (Medication)", "Which medication was prescribed"),
         field("dose", "float", "Dosage of the medication prescribed (in mg)"),
         field("dose_number", "float", "Number of doses taken per dose_period"),
         field("dose_period", "enum(day, week, course)", "Period over which dosage is measured"),
         field("start_dt",
               "date",
               "Start date for this drug (if different than treatment regimen"),
         field("end_dt_sch",
               "date",
               "Scheduled end date (if different than the treatment regimen"),
         field("end_dt_act",
               "date",
               "Actual end date (if different than the treatment regimen"),
         field("end_dt_bound",
               "enum(<,=,>)",
               "Uncertainty on 'end_dt_act'"),
        ]),

    entity(
        "TreatmentOutcome",
        "Outcome of a participant's treatment",
        [field(
             "treatment_id",
             "foreign key (TreatmentData)",
             "The treatment whose outcome is being described"),
         field("svr", "bool", "Sustained Viral Response (undetectable viral load at 12 weeks)"),
         field(
             "etr",
             "bool",
             "End-of-Treatment Response (undetectable viral load at end-of-treatment)"),
         field("early_stop", "bool", "Was the treatment stopped early?"),
         field(
             "stop_reason",
             "string",
             "Reason for stopping treatment (blank if treatment ended on schedule)"),
         field("notes", "string", "Additional notes (if applicable)"),
        ]),

    entity(
        "DeathAndLastFollowup",
        "Records data about participants leaving the study",
        [field("person_id", "foreign key (Person)", ""),
         field("study_id", "foreign key (SourceStudy)", "The study or trial this data comes from"),
         field("ltfu_dt", "date", "Date the participant was lost to follow-up"),
         field(
             "ltfu_reason",
             "string",
             "Reason the participant was lost to follow-up (if applicable)"),
         field("died", "bool", "Is the participant deceased?"),
         field("died_dt", "date", "The participant's date of death"),
         field("cod", "string", "Cause of death (e.g. ICD-10 code)"),
        ]),

    # ==================================================
    # Isolates & Sequences

    entity(
        "Isolate",
        "Virus isolate (from an individual or used in a lab experiment)",
        [field("id", "uuid", "Unique id"),
         field("type", "enum (clinical, lab)", "The kind of isolate. (additional data is available depending on kind "),
         field("entered_date", "date", "Date the isolate was entered into the database"),
         field("genbank_id", "string", "GenBank ID (if applicable)"),
         field("genotype", "enum(1,2,3,4,5,6,mixed,recombinant,indeterminate)", "The isolate's genotype"),
         field("subgenotype", "string", "The isolate's sub-genotype"),
         field("strain", "string", "The isolate's strain (if applicable/known)"),
        ]),

    entity(
        "Sequence",
        "Sequences and data needed for rapid alignment",
        [field("id", "uuid", "Unique identifier"),
         field("isolate_id", "foreign key (Isolate)", "Isolate the sequence was obtained from"),
         field("nt_seq", "string", "Raw nucleotide sequence (if available)"),
         field(
             "nt_start",
             "integer",
             "The starting position of the nucleotide sequence (with respect to the reference)"),
         field(
             "nt_end",
             "integer",
             "The end position of the nucleotide sequence (with respect to the reference)"),
         field("aa_seq", "string", "The sequence's raw amino-acid sequence"),
         field("aa_start",
               "integer",
               "The starting position of the amino acid sequence (with respect to the reference)"),
         field(
             "aa_end",
             "integer",
             "The end position of the amino acid sequence (with respect to the reference)"),
         field(
             "aa_derived",
             "bool",
             "Was the amino-acid sequence derived from the nucleotide sequence?"),
         field(
             "reference",
             "string",
             "The reference genome this sequence is described with respect to"),
         field("notes", "string", "Additional notes on this sequence (if applicable)"),
        ]),

    entity(
        "ClinicalIsolate",
        "Isolate information",
        [field("isolate_id", "foreign key (Isolate)", "The isolate this data pertains to"),
         field("person_id", "foreign key (Person)", "The participant who gave the isolate"),
         field("study_id", "foreign key (SourceStudy)", "The study that provided this isolate"),
         field("isolation_date", "date", "Date the virus was isolated"),
        ]),

    entity(
        "LabIsolate",
        "Isolates created in the lab",
        [field("isolate_id", "foreign key (Isolate)", "The isolate this data pertains to"),
         field("ref_id", "foreign key (Reference)", "A reference describing this lab isolate"),
         field("parent_sequence", "string", "The sequence from which this isolate is derived"),
         field("parent_gt",
               "enum(1,2,3,4,5,6,mixed,recombinant,indeterminate)",
               "The parent sequence's genotype"),
         field("parent_sgt",
               "string",
               "The parent sequence's subgenotype"),
         field(
             "kind",
             "enum(full-virus, full-replicon, stable-subgenomic, transient-subgenomic)",
             ("The kind of isolate created (full synthetic genome, transient subgenomic replicon, "
              "or stable subgenomic cell-line)")),
         field(
             "ins",
             "foreign key (Sequence)",
             "A sequence inserted into this isolate's parent sequence"),
         field(
             "ins_src_start",
             "integer",
             ("Start position of the inserted section of the source sequence "
              "(0 if the whole sequence was inserted))")),
         field(
             "ins_src_end",
             "integer",
             "End position of the inserted section of the source sequence"),
         field(
             "ins_pos_start",
             "integer",
             "Inserted sequence's start position"),
         field(
             "ins_pos_end",
             "integer",
             "Inserted sequence's end position in the constructed sequence"),
         field("ins_gene", "string", "Name of the inserted sequence's gene"),
         field(
             "ins_gt",
             "enum(1,2,3,4,5,6,mixed,recombinant,indeterminate)",
             "The inserted sequence's genotype"),
         field(
             "ins_sgt",
             "string",
             "The inserted sequence's subgenotype"),
         field("mutations", "string", "A list of site-directed mutations applied to the isolate"),
        ]),


    # ==================================================
    # Substitution tags

    entity(
        "Substitution",
        "A substitution, insertion, or deletion in an RNA sequence",
        [field("id", "uuid", "Unique identifier"),
         field("name", "string", "Name of the substitution"),
         field("reference_sequence", "string", "Name of the consensus wild-type reference sequence"),
         field("position", "integer", "Nucleotide position (with respect to the reference sequence)"),
         field("length", "integer", "Length of the substitution"),
         field("content", "string", "The nucleotide content of the substitution"),
         field("resistance_associated", "bool", "Is this a resistance associated substitution observed in virologic failures in the clinic?"),
        ]),

    entity(
        "SequenceSubstitution",
        "Indicates that the attached sequence has the attached substitution",
        [field("sequence_id", "foreign key (Sequence)", "The sequence being tagged"),
         field("substitution_id", "foreign key (Substitution)", "The substitution identified in the tagged sequence"),
        ]),


    # ==================================================
    # Susceptibility results

    entity(
        "Susceptibility",
        "Susceptibility test results",
        [field("id", "uuid", "Unique id"),
         field("isolate_id", "foreign key (Isolate)", "The isolate being tested"),
         field("reference_id", "foreign key (Reference)", "Source (if applicable)"),
         field(
             "method_id",
             "foreign key (SusceptibilityMethod)",
             "Method used to measure susceptibility"),
         field("medication_id", "foreign key (Medication)", "The medication being tested"),
         field("result", "float", "Concentration of medication required for inhibition (in nM)"),
         field("result_bound", "enum (<, =, >)", ""),
         field("IC", "enum (50, 90, 95)", "% inhibition"),
         field("fold", "float", "Fold-change compared to wild type"),
         field("fold_bound", "enum (<, =, >)", "Represents uncertainty in the fold-change measurement"),
        ]),

    entity(
        "SusceptibilityMethod",
        "Susceptibility testing methods",
        [field("id", "uuid", "Unique id"),
         field("name", "string", "Name of the method"),
         field("reference_id", "foreign key (Reference)", "Reference describing the method"),
         field("notes", "string", "Free-text notes about the testing method"),
        ]),

    entity(
        "Reference",
        "A reference to a publication",
        [field("id", "uuid", "Unique id"),
         field("author", "string", ""),
         field("title", "string", ""),
         field("journal", "string", ""),
         field("url", "string", "URL to the reference online"),
         field("publication_dt", "date", "Null for unpublished results"),
         field("pubmed_id", "string", ""),
        ]),

])
