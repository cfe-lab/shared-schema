import csv
import enum
import sys
import typing as ty
import uuid


class Gene(enum.Enum):
    ns3 = "ns3"
    ns5a = "ns5a"
    ns5b = "ns5b"


class RefSeq(ty.NamedTuple):
    genotype: str
    subgenotype: ty.Optional[str]
    gene: Gene
    shared_id: uuid.UUID
    genbank: str
    start: int
    end: int


def handler(_) -> None:
    HEADER_NAMES = {
        "genotype": "Genotype",
        "subgenotype": "Subgenotype",
        "gene": "Gene",
        "shared_id": "SHARED ID",
        "genbank": "Genbank Accession Number",
        "start": "Start Position",
        "end": "End Position",
    }
    HEADERS = [HEADER_NAMES[k] for k in RefSeq._fields]

    def mk_row(rs: RefSeq) -> ty.Dict[str, str]:
        dct = rs._asdict()
        dct["shared_id"] = "``{}``".format(dct["shared_id"])
        dct["gene"] = dct["gene"].name.upper()
        return {HEADER_NAMES[k]: v for k, v in dct.items()}

    writer = csv.DictWriter(sys.stdout, HEADERS)
    writer.writeheader()
    writer.writerows(map(mk_row, SEQS))


SEQS = [
    RefSeq(
        genotype="1",
        subgenotype="a",
        gene=Gene.ns3,
        shared_id=uuid.UUID("04deae83-fda3-4316-b6dc-4c29e2e79204"),
        genbank="NC_004102",
        start=3420,
        end=5474,
    ),
    RefSeq(
        genotype="1",
        subgenotype="a",
        gene=Gene.ns5a,
        shared_id=uuid.UUID("deb3a7b6-057d-4af3-b0f1-6d01ad350057"),
        genbank="NC_004102",
        start=6258,
        end=7601,
    ),
    RefSeq(
        genotype="1",
        subgenotype="a",
        gene=Gene.ns5b,
        shared_id=uuid.UUID("7ac4e78b-4c1e-4faf-9c17-aae0a3e0145f"),
        genbank="NC_004102",
        start=7602,
        end=9377,
    ),
    RefSeq(
        genotype="1",
        subgenotype="b",
        gene=Gene.ns3,
        shared_id=uuid.UUID("e3008a2d-fd6e-41cf-90e7-b3ef31788b79"),
        genbank="AJ238799",
        start=3420,
        end=5474,
    ),
    RefSeq(
        genotype="1",
        subgenotype="b",
        gene=Gene.ns5a,
        shared_id=uuid.UUID("9a720eb5-8f05-4787-bb43-398090612156"),
        genbank="AJ238799",
        start=6258,
        end=7598,
    ),
    RefSeq(
        genotype="1",
        subgenotype="b",
        gene=Gene.ns5b,
        shared_id=uuid.UUID("282d7594-abe8-496a-a9b1-e33c413935b7"),
        genbank="AJ238799",
        start=7599,
        end=9374,
    ),
    RefSeq(
        genotype="2",
        subgenotype=None,
        gene=Gene.ns3,
        shared_id=uuid.UUID("a8884935-1c1a-40b3-9dcf-ace0a3b1d116"),
        genbank="AB047639",
        start=3431,
        end=5485,
    ),
    RefSeq(
        genotype="2",
        subgenotype=None,
        gene=Gene.ns5a,
        shared_id=uuid.UUID("c79399ee-4cd0-4e7b-8d5c-f816798edbb9"),
        genbank="AB047639",
        start=6269,
        end=7666,
    ),
    RefSeq(
        genotype="2",
        subgenotype=None,
        gene=Gene.ns5b,
        shared_id=uuid.UUID("ed42ab5b-289e-46b2-b03d-167d6d8f9400"),
        genbank="AB047639",
        start=7667,
        end=9442,
    ),
    RefSeq(
        genotype="3",
        subgenotype=None,
        gene=Gene.ns3,
        shared_id=uuid.UUID("cf382d81-7296-4fd2-8ff5-51e00bed60ee"),
        genbank="GU814263",
        start=3436,
        end=5490,
    ),
    RefSeq(
        genotype="3",
        subgenotype=None,
        gene=Gene.ns5a,
        shared_id=uuid.UUID("2e485f94-d13a-4719-9a20-3cd3466888d6"),
        genbank="GU814263",
        start=6274,
        end=7629,
    ),
    RefSeq(
        genotype="3",
        subgenotype=None,
        gene=Gene.ns5b,
        shared_id=uuid.UUID("3ddd6687-88a6-4793-886b-b582dbdee708"),
        genbank="GU814263",
        start=7630,
        end=9402,
    ),
    RefSeq(
        genotype="4",
        subgenotype=None,
        gene=Gene.ns3,
        shared_id=uuid.UUID("5cc0ec43-973c-4f4f-946c-71855c43545a"),
        genbank="GU814265",
        start=3419,
        end=5473,
    ),
    RefSeq(
        genotype="4",
        subgenotype=None,
        gene=Gene.ns5a,
        shared_id=uuid.UUID("ac11658c-486a-4604-993a-f9a1079b5bb2"),
        genbank="GU814265",
        start=6257,
        end=7591,
    ),
    RefSeq(
        genotype="4",
        subgenotype=None,
        gene=Gene.ns5b,
        shared_id=uuid.UUID("20021586-8e8c-4840-86b5-0f333de37c08"),
        genbank="GU814265",
        start=7592,
        end=9364,
    ),
    RefSeq(
        genotype="5",
        subgenotype=None,
        gene=Gene.ns3,
        shared_id=uuid.UUID("28c6f42b-d5b2-4432-8c69-c141128ada23"),
        genbank="AF064490",
        start=3328,
        end=5382,
    ),
    RefSeq(
        genotype="5",
        subgenotype=None,
        gene=Gene.ns5a,
        shared_id=uuid.UUID("c2003ea8-1066-49a0-99c7-793ed34b8b7f"),
        genbank="AF064490",
        start=6166,
        end=7515,
    ),
    RefSeq(
        genotype="5",
        subgenotype=None,
        gene=Gene.ns5b,
        shared_id=uuid.UUID("660cf779-e8d7-47c5-b8c8-207cefb946b5"),
        genbank="AF064490",
        start=7516,
        end=9291,
    ),
    RefSeq(
        genotype="6",
        subgenotype=None,
        gene=Gene.ns3,
        shared_id=uuid.UUID("2cad08ea-5a40-4ce7-8cc5-b8cbd056679c"),
        genbank="Y12083",
        start=3374,
        end=5428,
    ),
    RefSeq(
        genotype="6",
        subgenotype=None,
        gene=Gene.ns5a,
        shared_id=uuid.UUID("6caca1c3-237a-4c6f-b293-4c263a2eab19"),
        genbank="Y12083",
        start=6212,
        end=7564,
    ),
    RefSeq(
        genotype="6",
        subgenotype=None,
        gene=Gene.ns5b,
        shared_id=uuid.UUID("9f09d6a0-4a08-4cc1-bc1f-bda0cccd6f4c"),
        genbank="Y12083",
        start=7565,
        end=9340,
    ),
]
