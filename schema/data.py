#encoding: utf8

import collections

import schema.util as util


# Data Parsing


_entity = collections.namedtuple(
    "entity",
    ["name", "description", "fields", "tags"],
)

class Entity(_entity):
    @classmethod
    def make(cls, name, description, fields, tags=None):
        if tags is None:
            tags = set()
        return cls(name, description, fields, tags)

_field = collections.namedtuple(
    "field",
    ["name", "type", "description", "tags"],
)

class Field(_field):
    @classmethod
    def make(cls, name, type, description, tags=None):
        if tags is None:
            tags = set()
        return cls(name, type, description, tags)

field = Field.make


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

    Entity.make(
        "Medication",
        "Anti-HCV drugs. Phenotypic resistance tests and treatment records reference this table.",
        [field(
            "full_name",
            "string",
            "The medication's name",
            tags={'required'},
        ),
         field(
             "short_name",
             "string",
             "The medication's three-letter abbreviation",
         ),
        ],
        tags={'managed'},
    ),

    # ==================================================
    # Collaborator and Study/Trial data

    Entity.make(
        "Collaborator",
        "A collaborating site (provides participant data)",
        [field("id", "uuid", "Unique identifier", tags={'managed', 'required'}),
         field("name", "string", "Name of the collaborating entity", tags={'required'}),
        ],
        tags={'managed'},
    ),

    Entity.make(
        "SourceStudy",
        "A study, trial, or other batch of data from a collaborator",
        [field(
            "collaborator",
            "foreign key (Collaborator)",
            "The collaborator providing the data",
            tags={'required'},
        ),
         field("ref_id", "foreign key (Reference)", "Publication describing this study (if applicable)"),
         field("name", "string", "The name of the study or trial"),
         field("collection_start", "date", "The beginning of data collection"),
         field("collection_end", "date", "The end of data collection (if applicable)"),
         field("notes", "string", "Notes on data from this project"),
        ],
        tags={'managed'},
    ),


    # ==================================================
    # Participant Data (demographic, clinical, behavioral, treatment)

    Entity.make(
        "Person",
        "A study participant",
        [field("id", "uuid", "Unique identifier", tags={'managed', 'required'}),
         field(
             "study_id",
             "foreign key (SourceStudy)",
             "The study the participant entered the database with",
         ),
         field("country", "string", "The country where the person participated in the study"),
         field("city", "string", "The city where the person participated in the study"),
         field("year_of_birth", "date", "Participant's year of birth"),
         field("sex", "enum(male, female, other)", "The participant's sex at birth"),
         field("ethnicity",
               "enum(am-nat, asian, black, hisp, pa-isl, white)",
               ("The participant's ethnicity: American Native, Asian, "
                "Black/African American, Hispanic/Latino, Pacific Islander, "
                "or White")
         ),
        ],
        tags={'clinical'},
    ),

    Entity.make(
        "BehaviorData",
        "Behavioral information about a participant",
        [field("id", "uuid", "Unique identifier", tags={'managed', 'required'}),
         field(
             "person_id",
             "foreign key (Person)",
             "The participant this data pertains to",
             tags={'required'},
         ),
         field("date_collected", "date", "The date this data was collected"),
         field("sexual_orientation", "enum (heterosexual, homosexual, bisexual, other)",
               "Participant's sexual orientation"),
         field("idu", "bool", "Injection drug use? (ever)"),
         field("ndu", "bool", "Non-injection drug use? (ever)"),
         field("idu_recent", "bool", "Injection drug use in the past 6 months?"),
         field("ndu_recent", "bool", "None-injection drug use in the past 6 months?"),
         field("prison", "bool", "Has the participant been in prison (ever)?"),
        ],
        tags={'clinical'},
    ),

    Entity.make(
        "ClinicalData",
        "Participants' test results and relevant medical history",
        [field("person_id", "foreign key(Person)", "The person to whom this data pertains"),
         field("hiv", "bool", "Is the participant co-infected with HIV?"),
         field("hbv", "bool", "Is the participant co-infected with HBV?"),
         field("ost", "bool", "Has the participant undergone opioid substitution therapy in the last six months?"),
         field("chir", "bool", "Does the participant have cirrhosis?"),
         field(
             "metavir",
             "enum(A0, A1, A2, A3, F0, F1, F2, F3, F4)",
             "Metavir score",
         ),
         field(
             "metavir_by",
             "enum(fibroscan, biopsy, clinical, other)",
             "Method used to determine metavir score: ",
         ),
         field("stiff", "float", "Liver stiffness (in kPa)."),
         field("alt", "float", "Alanine aminotransferase level (in U/L)."),
         field("ast", "float", "Aspartate aminotransferase level (in U/L)."),
         field("crt", "float", "Creatinine level (in $\mu$M/L)."),
         field("egfr", "float", "Estimated glomerular filtration rate (in mL/minBSAc)."),
         field("ctp", "float", "Child-Turcotte-Pugh score."),
         field("meld", "float", "MELD score."),
         field("ishak", "float", "Ishak score."),
         field("bil", "float", "Bilirubin test result, in mg/dL."),
         field("hemo", "float", "Hemoglobin test result, in g/dL."),
         field("alb", "float", "Albumin test result, in g/dL."),
         field("inr", "float", "International Normalized Ratio test result."),
         field("phos", "float", "Phosphate test result, in mg/dL."),
         field("urea", "float", "Urea test result, in ng/dL."),
         field("plate", "float", "Platelet count, in cells/mm$^3$."),
         field("CD4", "float", "CD4 count, in cells/mm$^3$."),
         field("crp", "float", "C-Reactive Protein test result, in mg/L."),
         field("il28b", "string", "The participant's IL28B-rs12979860 genotype: TT, TC, CC"),
         field("asc", "bool", "Did the participant have ascites before or during treatment?"),
         field("var_bleed", "bool", "Did the participant have variceal bleeding before or during treatment?"),
         field("hep_car", "bool", "Did the participant have hepatocellular carcinoma before or during treatment?"),
         field("transpl", "bool", "Has the participant had a liver transplant?"),
        ],
        tags={'clinical'},
    ),

    Entity.make(
        "TreatmentData",
        "Information about a participant's treatment",
        [field("id", "uuid", "Unique identifier", tags={'managed'}),
         field(
             "person_id",
             "foreign key (Person)",
             "The participant that this data pertains to",
             tags={'required'},
         ),
         field("first_treatment", "bool", "Is this the participant's first treatment "),
         field("start_dt", "date", "Schedule treatment start date"),
         field("end_dt_sch", "date", "Scheduled treatment end date"),
         field("end_dt_act", "date", "Actual treatment end date"),
         field("end_dt_bound", "enum(<, >, =)", "Uncertainty on `end_dt_act`"),
         field(
             "int",
             "bool",
             ("Has the participant ever been treated with pegylated interferon "
              "drugs before?")),
         field(
             "response",
             "enum(svr, nr, eot, bt, rl, ri)",
             ("Viral response: sustained, non-responsive, detectable viral "
              "load at end-of-treatment, viral-breakthrough during treatment,"
              "eventual relapse, eventual reinfection)")
         ),
         field(
             "regimen",
             "foreign key (Regimen)",
             "The drug regimen taken by the participant",
             tags={'required'},
         ),
         field(
             "prev_regimen",
             "foreign key (Regimen)",
             ("If the participant has been treated before, what is the last "
              "regimen they were on?"),
         ),
         field(
             "pprev_regimen",
             "foreign key (Regimen)",
             ("If the participant has been treated before, what regimen were "
              "they on before-last?"),
         ),
         field("notes", "string", "Additional notes (if applicable)"),
        ],
        tags={'clinical'},
    ),

    Entity.make(
        "Regimen",
        "How much and what kind of medications were included in a treatment regimen",
        [field(
             "medication_id",
             "foreign key (Medication)",
             "Which medication was prescribed",
             tags={'required'},
         ),
         field("dose", "float", "Dosage of the medication prescribed (in mg)"),
         field("dose_number", "float", "Number of doses taken per `dose_period`"),
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
               "enum(<, =, >)",
               "Uncertainty on `end_dt_act`"),
        ],
        tags={'clinical'},
    ),

    Entity.make(
        "LossToFollowUp",
        "Records data about participants leaving the study",
        [field(
            "person_id",
            "foreign key (Person)",
            "",
            tags={'required'},
        ),
         field("ltfu_dt", "date", "Date the participant was lost to follow-up"),
         field("died", "bool", "Is the participant deceased?"),
         field(
             "cod",
             "enum(liv, aid, odo, can, cir, res, dia, gen, tra, cer, dig, oth)",
             "Cause of death (if applicable)"
         ),
        ],
        tags={'clinical'},
    ),

    # ==================================================
    # Isolates & Sequences

    Entity.make(
        "Isolate",
        "Virus isolate (from an individual or used in a lab experiment)",
        [field("id", "uuid", "Unique id", tags={'managed', 'required'}),
         field(
             "type",
             "enum (clinical, lab)",
             "The kind of isolate. (additional data is available depending on kind)",
             tags={'required', 'managed'},
         ),
         field(
             "entered_date",
             "date",
             "Date the isolate was entered into the database",
             tags={'managed'},
         ),
         field(
             "genotype",
             "enum(1, 2, 3, 4, 5, 6, mixed, recombinant, indeterminate)",
             "The isolate's genotype",
         ),
         field("subgenotype", "string", "The isolate's sub-genotype"),
         field("strain", "string", "The isolate's strain (if applicable/known)"),
        ]),

    Entity.make(
        "Sequence",
        "Sequences and data needed for rapid alignment",
        [field("id", "uuid", "Unique identifier", tags={'managed'}),
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

    Entity.make(
        "ClinicalIsolate",
        "Isolate information",
        [field(
            "isolate_id",
            "foreign key (Isolate)",
            "The isolate this data pertains to",
            tags={'required', 'managed'},
        ),
         field(
             "person_id",
             "foreign key (Person)",
             "The participant who gave the isolate",
             tags={'required'}
         ),
         field("isolation_date", "date", "Date the virus was isolated"),
        ],
        tags={'clinical'},
    ),

    Entity.make(
        "LabIsolate",
        "Isolates created in the lab",
        [field("isolate_id", "foreign key (Isolate)", "The isolate this data pertains to"),
         field("ref_id", "foreign key (Reference)", "A reference describing this lab isolate"),
         field("genbank_id", "string", "GenBank ID (if applicable)"),
         field("parent_sequence", "string", "The sequence from which this isolate is derived"),
         field("parent_gt",
               "enum(1, 2, 3, 4, 5, 6, mixed, recombinant, indeterminate)",
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
             "enum(1, 2, 3, 4, 5, 6, mixed, recombinant, indeterminate)",
             "The inserted sequence's genotype"),
         field(
             "ins_sgt",
             "string",
             "The inserted sequence's subgenotype"),
         field("mutations", "string", "A list of site-directed mutations applied to the isolate"),
        ],
        tags={'phenotypic'},
    ),


    # ==================================================
    # Substitution tags

    Entity.make(
        "Substitution",
        "A substitution, insertion, or deletion in an RNA sequence",
        [field("id", "uuid", "Unique identifier", tags={'managed'}),
         field("name", "string", "Name of the substitution"),
         field("reference_sequence", "string", "Name of the consensus wild-type reference sequence"),
         field("position", "integer", "Nucleotide position (with respect to the reference sequence)"),
         field("length", "integer", "Length of the substitution"),
         field("content", "string", "The nucleotide content of the substitution"),
         field("resistance_associated", "bool", "Is this a resistance associated substitution observed in virologic failures in the clinic?"),
        ],
        tags={'managed'},
    ),

    Entity.make(
        "SequenceSubstitution",
        "Indicates that the attached sequence has the attached substitution",
        [field("sequence_id", "foreign key (Sequence)", "The sequence being tagged"),
         field("substitution_id", "foreign key (Substitution)", "The substitution identified in the tagged sequence"),
        ],
        tags={'managed'},
    ),


    # ==================================================
    # Susceptibility results

    Entity.make(
        "Susceptibility",
        "Susceptibility test results",
        [field("id", "uuid", "Unique id", tags={'managed'}),
         field("isolate_id", "foreign key (Isolate)", "The isolate being tested"),
         field("reference_id", "foreign key (Reference)", "Source (if applicable)"),
         field(
             "method_id",
             "foreign key (SusceptibilityMethod)",
             "Method used to measure susceptibility"),
         field("medication_id", "foreign key (Medication)", "The medication being tested"),
         field("result", "float", "Concentration of medication required for inhibition (in nM)"),
         field("result_bound", "enum (<, =, >)", ""),
         field("IC", "enum (50, 90, 95)", "percent inhibition"),
         field("fold", "float", "Fold-change compared to wild type"),
         field("fold_bound", "enum (<, =, >)", "Represents uncertainty in the fold-change measurement"),
        ],
        tags={'phenotypic'},
    ),

    Entity.make(
        "SusceptibilityMethod",
        "Susceptibility testing methods",
        [field("id", "uuid", "Unique id", tags={'managed'}),
         field("name", "string", "Name of the method"),
         field("reference_id", "foreign key (Reference)", "Reference describing the method"),
         field("notes", "string", "Free-text notes about the testing method"),
        ],
        tags={'phenotypic', 'managed'},
    ),

    Entity.make(
        "Reference",
        "A reference to a publication",
        [field("id", "uuid", "Unique id", tags={'managed'}),
         field("author", "string", ""),
         field("title", "string", ""),
         field("journal", "string", ""),
         field("url", "string", "URL to the reference online"),
         field("publication_dt", "date", "Null for unpublished results"),
         field("pubmed_id", "string", ""),
        ]),

])
