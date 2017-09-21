'''Record standard compounds and treatment regimens'''

_compound_keys = ('compound', 'abbreviation')
_compounds = [
    ("asunaprevir", "ASV"),
    ("boceprevir", "BOC"),
    ("daclatasvir", "DAC"),
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
compounds = [dict(zip(_compound_keys, c)) for c in _compounds]

_freq_keys = ("abbreviation", "description")
_freqs = [
    ("QD", "once daily"),
    ("BID", "twice daily"),
    ("TID", "three times daily"),
    ("QID", "four times daily"),
    ("QWK", "weekly"),
]
freqs = [dict(zip(_freq_keys, f)) for f in _freqs]

_regimen_keys = ("name", "regimen")
_regimens = [
    ("DAKLINZA", "60mg DAC QD 12 weeks"),
    ("EPCLUSA", "400mg SOF + 100mg VEL QD 12 weeks"),
    ("HARVONI", "90mg LDV + 400mg SOF QD 12 weeks"),
    ("INCIVEK", "750mg TVR TID 12 weeks"),
    ("MAVYRET", "300mg GLP + 120mg PIB QD 12 weeks"),
    ("OLYSIO", "150mg SIM QD 12 weeks"),
    ("SOVALDI", "400mg SOF QD 12 weeks"),
    ("SUNVEPRA", "100mg ASV BID 24 weeks"),
    ("TECHNIVIE", "25mg OMB + 150mg PAR + 100mg RIT QD 12 weeks"),
    ("VICTRELIS", "800mg BOC TID 32 weeks"),
    ("VIEKIRA PAK",
     "250mg DAS BID & 250mg OMB + 150mg PAR + 100mg RIT QD 12 weeks"),
    ("VIEKIRA XR", "600mg DAS + 25mg OMB + 150mg PAR +100mg RIT QD 12 weeks"),
    ("VOSEVI", "400mg SOF + 100mg VEL + 100mg VOX QD 12 weeks"),
    ("ZEPATTIER", "50mg EBR + 100mg GZR QD 12 weeks"),
    ("PEGASYS", "0.180mg PEG QWK 48 weeks"),
    ("COPEGUS1000", "500mg RBV BID 48 weeks"),
    ("COPEGUS1200", "600mg RBV BID 48 weeks    "),
]
regimens = [dict(zip(_regimen_keys, r)) for r in _regimens]
