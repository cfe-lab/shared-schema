"""Record standard compounds and treatment regimens"""

_compounds = [
    ("asunaprevir", "ASV"),
    ("boceprevir", "BOC"),
    ("daclatasvir", "DCV"),
    ("dasabuvir", "DAS"),
    ("elbasvir", "EBR"),
    ("glecaprevir", "GLP"),
    ("grazoprevir", "GZR"),
    ("ledipasvir", "LDV"),
    ("ombitasvir", "OMB"),
    ("paritaprevir", "PAR"),
    ("pegylated interferon", "PEG"),
    ("pibrentasvir", "PIB"),
    ("ribavirin", "RBV"),
    ("ritonavir", "RIT"),
    ("simeprevir", "SIM"),
    ("sofosbuvir", "SOF"),
    ("telaprevir", "TVR"),
    ("vaniprevir", "VAN"),
    ("velpatasvir", "VEL"),
    ("voxilaprevir", "VOX"),
]
compounds = {cmpnd: abbr for cmpnd, abbr in _compounds}
compound_keys = ("compound", "abbreviation")

_freqs = [
    ("QD", "once daily"),
    ("BID", "twice daily"),
    ("TID", "three times daily"),
    ("QID", "four times daily"),
    ("QWK", "weekly"),
]
freqs = {abbr: desc for abbr, desc in _freqs}
freq_keys = ("abbreviation", "description")

_regimens = [
    ("DAKLINZA", "60mg DCV QD 12 weeks"),
    ("EPCLUSA", "(400mg SOF + 100mg VEL) QD 12 weeks"),
    ("HARVONI", "(90mg LDV + 400mg SOF) QD 12 weeks"),
    ("INCIVEK", "750mg TVR TID 12 weeks"),
    ("MAVYRET", "(300mg GLP + 120mg PIB) QD 12 weeks"),
    ("OLYSIO", "150mg SIM QD 12 weeks"),
    ("SOVALDI", "400mg SOF QD 12 weeks"),
    ("SUNVEPRA", "100mg ASV BID 24 weeks"),
    ("TECHNIVIE", "(25mg OMB + 150mg PAR + 100mg RIT) QD 12 weeks"),
    ("VICTRELIS", "800mg BOC TID 32 weeks"),
    (
        "VIEKIRA PAK",
        "250mg DAS BID & (250mg OMB + 150mg PAR + 100mg RIT) QD 12 weeks",
    ),
    ("VIEKIRA XR", "(600mg DAS + 25mg OMB + 150mg PAR +100mg RIT) QD 12 weeks"),
    ("VOSEVI", "(400mg SOF + 100mg VEL + 100mg VOX) QD 12 weeks"),
    ("ZEPATIER", "(50mg EBR + 100mg GZR) QD 12 weeks"),
    ("PEGASYS", "0.180mg PEG QWK 48 weeks"),
    ("COPEGUS1000", "500mg RBV BID 48 weeks"),
    ("COPEGUS1200", "600mg RBV BID 48 weeks"),
]
regimens = {name: reg for name, reg in _regimens}
regimen_keys = ("name", "regimen")


def expand(src):
    """Replace standard regimen names with their contents.

    This function searchs a regimen source string for standard regimen
    names and replaces them with the long form of their contents, as
    understood by the grammar.
    """
    for name, explicit in regimens.items():
        if name in src:
            src = src.replace(name, explicit)
    return src
