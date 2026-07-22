"""Actor identity resolution crosswalk.

Maps country/actor IDs across datasets (COW, UCDP, V-Dem, etc.)
Builds a comprehensive mapping from COW numeric codes to standard actor IDs,
including time-bounded entries for historical states.
"""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

CROSSWALK_SCHEMA = [
    "actor_id",
    "cow_code",
    "vdem_country_id",
    "world_bank_iso3",
    "ucdp_actor_id",
    "acled_actor_name",
    "wikidata_qid",
    "actor_name_standard",
    "start_year",
    "end_year",
    "notes",
]

# Map COW numeric codes → COW 3-letter abbreviation and standard country name
# These are from the NMC state system membership list
COW_CODE_MAP: dict[int, tuple[str, str]] = {
    2: ("USA", "United States of America"),
    20: ("CAN", "Canada"),
    31: ("BHM", "Bahamas"),
    40: ("CUB", "Cuba"),
    41: ("HAI", "Haiti"),
    42: ("DOM", "Dominican Republic"),
    51: ("JAM", "Jamaica"),
    52: ("TRI", "Trinidad and Tobago"),
    53: ("BAR", "Barbados"),
    54: ("DMA", "Dominica"),
    55: ("GRN", "Grenada"),
    56: ("SLU", "Saint Lucia"),
    57: ("SVG", "Saint Vincent and the Grenadines"),
    58: ("AAB", "Antigua and Barbuda"),
    60: ("SKN", "Saint Kitts and Nevis"),
    70: ("MEX", "Mexico"),
    80: ("BLZ", "Belize"),
    90: ("GUA", "Guatemala"),
    91: ("HON", "Honduras"),
    92: ("SAL", "El Salvador"),
    93: ("NIC", "Nicaragua"),
    94: ("COS", "Costa Rica"),
    95: ("PAN", "Panama"),
    100: ("COL", "Colombia"),
    101: ("VEN", "Venezuela"),
    110: ("GUY", "Guyana"),
    115: ("SUR", "Suriname"),
    130: ("ECU", "Ecuador"),
    135: ("PER", "Peru"),
    140: ("BRA", "Brazil"),
    145: ("BOL", "Bolivia"),
    150: ("PAR", "Paraguay"),
    155: ("CHL", "Chile"),
    160: ("ARG", "Argentina"),
    165: ("URU", "Uruguay"),
    200: ("UKG", "United Kingdom"),
    205: ("IRE", "Ireland"),
    210: ("NTH", "Netherlands"),
    211: ("BEL", "Belgium"),
    212: ("LUX", "Luxembourg"),
    220: ("FRN", "France"),
    221: ("MNC", "Monaco"),
    223: ("LIE", "Liechtenstein"),
    225: ("SWZ", "Switzerland"),
    230: ("SPN", "Spain"),
    232: ("AND", "Andorra"),
    235: ("POR", "Portugal"),
    240: ("HAN", "Hanover"),
    245: ("BAV", "Bavaria"),
    255: ("GMY", "Germany"),
    260: ("GFR", "West Germany"),
    265: ("GDR", "East Germany"),
    267: ("BAD", "Baden"),
    269: ("SAX", "Saxony"),
    271: ("WRT", "Württemberg"),
    273: ("HSE", "Hesse Electoral"),
    275: ("HSG", "Hesse Grand Ducal"),
    280: ("MEC", "Mecklenburg-Schwerin"),
    290: ("POL", "Poland"),
    300: ("AUH", "Austria"),
    305: ("AUS", "Austria"),
    310: ("HUN", "Hungary"),
    315: ("CZE", "Czechoslovakia"),
    316: ("CZR", "Czech Republic"),
    317: ("SLO", "Slovakia"),
    325: ("ITA", "Italy"),
    327: ("PAP", "Papal States"),
    329: ("SIC", "Two Sicilies"),
    331: ("SNM", "San Marino"),
    332: ("MOD", "Modena"),
    335: ("PMA", "Parma"),
    337: ("TUS", "Tuscany"),
    338: ("MLT", "Malta"),
    339: ("ALB", "Albania"),
    341: ("MNG", "Montenegro"),
    342: ("SER", "Serbia"),
    343: ("MAC", "Macedonia"),
    344: ("CRO", "Croatia"),
    345: ("YUG", "Yugoslavia"),
    346: ("BOS", "Bosnia"),
    347: ("KOS", "Kosovo"),
    349: ("SLV", "Slovenia"),
    350: ("GRC", "Greece"),
    352: ("CYP", "Cyprus"),
    355: ("BUL", "Bulgaria"),
    359: ("MLD", "Moldova"),
    360: ("ROM", "Romania"),
    365: ("RUS", "Russia"),
    366: ("EST", "Estonia"),
    367: ("LAT", "Latvia"),
    368: ("LIT", "Lithuania"),
    369: ("UKR", "Ukraine"),
    370: ("BLR", "Belarus"),
    371: ("ARM", "Armenia"),
    372: ("GRG", "Georgia"),
    373: ("AZE", "Azerbaijan"),
    375: ("FIN", "Finland"),
    380: ("SWD", "Sweden"),
    385: ("NOR", "Norway"),
    390: ("DEN", "Denmark"),
    395: ("ICE", "Iceland"),
    402: ("CAP", "Cape Verde"),
    403: ("STP", "São Tomé and Príncipe"),
    404: ("GNB", "Guinea-Bissau"),
    411: ("EQG", "Equatorial Guinea"),
    420: ("GAM", "Gambia"),
    432: ("MLI", "Mali"),
    433: ("SEN", "Senegal"),
    434: ("BEN", "Benin"),
    435: ("MAA", "Mauritania"),
    436: ("NIR", "Niger"),
    437: ("CDI", "Côte d'Ivoire"),
    438: ("GUI", "Guinea"),
    439: ("BFO", "Burkina Faso"),
    450: ("LBR", "Liberia"),
    451: ("SIE", "Sierra Leone"),
    452: ("GHA", "Ghana"),
    461: ("TOG", "Togo"),
    471: ("CAO", "Cameroon"),
    475: ("NIG", "Nigeria"),
    481: ("GAB", "Gabon"),
    482: ("CEN", "Central African Republic"),
    483: ("CHA", "Chad"),
    484: ("CON", "Congo"),
    490: ("DRC", "Democratic Republic of the Congo"),
    500: ("UGA", "Uganda"),
    501: ("KEN", "Kenya"),
    510: ("TAZ", "Tanzania"),
    511: ("ZAN", "Zanzibar"),
    516: ("BUI", "Burundi"),
    517: ("RWA", "Rwanda"),
    520: ("SOM", "Somalia"),
    522: ("DJI", "Djibouti"),
    530: ("ETH", "Ethiopia"),
    531: ("ERI", "Eritrea"),
    540: ("ANG", "Angola"),
    541: ("MZM", "Mozambique"),
    551: ("ZAM", "Zambia"),
    552: ("ZIM", "Zimbabwe"),
    553: ("MAW", "Malawi"),
    560: ("SAF", "South Africa"),
    565: ("NAM", "Namibia"),
    570: ("LES", "Lesotho"),
    571: ("BOT", "Botswana"),
    572: ("SWA", "Eswatini"),
    580: ("MAG", "Madagascar"),
    581: ("COM", "Comoros"),
    590: ("MAS", "Mauritius"),
    591: ("SEY", "Seychelles"),
    600: ("MOR", "Morocco"),
    615: ("ALG", "Algeria"),
    616: ("TUN", "Tunisia"),
    620: ("LIB", "Libya"),
    625: ("SUD", "Sudan"),
    626: ("SSD", "South Sudan"),
    630: ("IRN", "Iran"),
    640: ("TUR", "Turkey"),
    645: ("IRQ", "Iraq"),
    651: ("EGY", "Egypt"),
    652: ("SYR", "Syria"),
    660: ("LEB", "Lebanon"),
    663: ("JOR", "Jordan"),
    666: ("ISR", "Israel"),
    670: ("SAU", "Saudi Arabia"),
    678: ("YAR", "Yemen Arab Republic"),
    679: ("YEM", "Yemen"),
    680: ("YPR", "Yemen People's Republic"),
    690: ("KUW", "Kuwait"),
    692: ("BAH", "Bahrain"),
    694: ("QAT", "Qatar"),
    696: ("UAE", "United Arab Emirates"),
    698: ("OMA", "Oman"),
    700: ("AFG", "Afghanistan"),
    701: ("TKM", "Turkmenistan"),
    702: ("TAJ", "Tajikistan"),
    703: ("KYR", "Kyrgyzstan"),
    704: ("UZB", "Uzbekistan"),
    705: ("KZK", "Kazakhstan"),
    710: ("CHN", "China"),
    712: ("MON", "Mongolia"),
    713: ("TAW", "Taiwan"),
    730: ("KOR", "South Korea"),
    731: ("PRK", "North Korea"),
    732: ("ROK", "South Korea"),
    740: ("JPN", "Japan"),
    750: ("IND", "India"),
    760: ("BHU", "Bhutan"),
    770: ("PAK", "Pakistan"),
    771: ("BNG", "Bangladesh"),
    775: ("MYA", "Myanmar"),
    780: ("SRI", "Sri Lanka"),
    781: ("MAD", "Maldives"),
    790: ("NEP", "Nepal"),
    800: ("THI", "Thailand"),
    811: ("CAM", "Cambodia"),
    812: ("LAO", "Laos"),
    816: ("DRV", "Vietnam"),
    817: ("RVN", "South Vietnam"),
    820: ("MAL", "Malaysia"),
    830: ("SIN", "Singapore"),
    835: ("BRU", "Brunei"),
    840: ("PHI", "Philippines"),
    850: ("INS", "Indonesia"),
    860: ("ETM", "Timor-Leste"),
    900: ("AUL", "Australia"),
    910: ("PNG", "Papua New Guinea"),
    920: ("NEW", "New Zealand"),
    935: ("VAN", "Vanuatu"),
    940: ("SOL", "Solomon Islands"),
    946: ("KIR", "Kiribati"),
    947: ("TUV", "Tuvalu"),
    950: ("FIJ", "Fiji"),
    955: ("TON", "Tonga"),
    970: ("NAU", "Nauru"),
    983: ("MSI", "Marshall Islands"),
    986: ("PAL", "Palau"),
    987: ("FSM", "Micronesia"),
    990: ("WSM", "Samoa"),
}

# Time-bounded historical actors sharing a COW code
# (actor_id, cow_code, name, start, end, notes)
HISTORICAL_ENTRIES: list[tuple[str, int, str, int, int | None, str]] = [
    ("PRU", 255, "Prussia", 1701, 1871, "Part of German unification"),
    ("SOV", 365, "Soviet Union", 1922, 1991, ""),
    ("AUH", 300, "Austria-Hungary", 1867, 1918, "Also known as Habsburg Monarchy"),
    ("OTT", 640, "Ottoman Empire", 1299, 1922, ""),
    ("QIN", 710, "Qing Empire", 1644, 1912, ""),
]

# Non-state/rebel actor IDs from intrastate data (seed entries for common ones)
NON_STATE_ENTRIES: list[tuple[str, str]] = []


def _cow_abb(actor_name: str) -> str:
    """Generate a 3-letter actor_id from a name."""
    parts = actor_name.replace("-", " ").replace("'", "").split()
    if len(parts) >= 3:
        return "".join(p[0].upper() for p in parts[:3])
    abb = "".join(p[0].upper() for p in parts)
    if len(abb) < 3:
        abb = (abb + actor_name[:3].upper())[:3]
    return abb[:4]


def build_actor_crosswalk(
    output_dir: Path,
    cow_war_df: pd.DataFrame | None = None,
    seed_only: bool = False,
) -> pd.DataFrame:
    """Build comprehensive actor crosswalk from COW codes and war data.

    If seed_only=True, returns just the 26 hand-curated major-power entries.
    Otherwise generates a full crosswalk covering all COW codes found in war
    data plus time-bounded historical states.
    """
    records = []

    if seed_only:
        # Legacy mode: only the original 26 seed entries
        records = SEED_CROSSWALK
    else:
        # Add all COW-code entries
        for code, (abb, name) in sorted(COW_CODE_MAP.items()):
            records.append((abb, code, "", "", "", "", "", name, None, None, ""))

        # Remove duplicates from historical overrides
        hist_codes = {h[1] for h in HISTORICAL_ENTRIES}
        records = [r for r in records if r[1] not in hist_codes or r[3] != ""]

        # Add time-bounded historical entries
        for hid, hcode, hname, hstart, hend, hnotes in HISTORICAL_ENTRIES:
            records.append((hid, hcode, "", "", "", "", "", hname, hstart, hend, hnotes))
            # Also keep the modern entry for overlapping codes
            if hid.upper() != COW_CODE_MAP.get(hcode, ("", ""))[0]:
                abb, name = COW_CODE_MAP.get(hcode, ("", ""))
                if abb:
                    records.append((abb, hcode, "", "", "", "", "", name, None, None, ""))

        # Add intrastate non-state actors from COW data
        if cow_war_df is not None and len(cow_war_df) > 0:
            non_state = _extract_non_state_actors(cow_war_df)
            existing_names = {r[7].lower() for r in records}
            for actor_name in non_state:
                if actor_name.lower() not in existing_names:
                    aid = _cow_abb(actor_name)
                    row = (aid, -1, "", "", "", "", "", actor_name, None, None, "non-state")
                    records.append(row)
                    existing_names.add(actor_name.lower())

    df = pd.DataFrame(records, columns=CROSSWALK_SCHEMA)
    for col in df.select_dtypes(include=["object", "str"]).columns:
        df[col] = df[col].astype(str)

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "actor_crosswalk.parquet"
    df.to_parquet(out_path, index=False)
    logger.info(f"Actor crosswalk written to {out_path} ({len(df)} actors)")
    return df


def _extract_non_state_actors(cow_war_df: pd.DataFrame) -> set[str]:
    """Extract unique non-state actor names from intrastate COW data."""
    actors: set[str] = set()
    for col in ["SideA", "SideB"]:
        if col not in cow_war_df.columns:
            continue
        vals = cow_war_df[col].dropna().unique()
        for v in vals:
            name = str(v).strip()
            if name and not name.isdigit() and name not in ("-9", "-8", "nan", ""):
                actors.add(name)
    return actors


# Legacy seed crosswalk kept for backward compatibility
SEED_CROSSWALK = [
    (abb, code, "", "", "", "", "", name, None, None, "")
    for code, (abb, name) in sorted(COW_CODE_MAP.items())
] + [
    (hid, hcode, "", "", "", "", "", hname, hstart, hend, hnotes)
    for hid, hcode, hname, hstart, hend, hnotes in HISTORICAL_ENTRIES
]


def resolve_actor(
    crosswalk: pd.DataFrame,
    cow_code: int | None = None,
    actor_name: str | None = None,
    year: int | None = None,
) -> str:
    """Resolve an actor to standard actor_id given available identifiers.

    For COW codes that map to multiple historical actors (e.g., 365 → Russia
    or Soviet Union), uses year to disambiguate when possible.
    """
    if cow_code is not None and cow_code > 0:
        matches = crosswalk[crosswalk["cow_code"] == cow_code]
        if len(matches) == 0:
            return f"UNKNOWN_{cow_code}"
        if len(matches) == 1:
            return matches.iloc[0]["actor_id"]
        # Multiple entries for this cow_code — use year to disambiguate
        if year is not None:
            for _, row in matches.iterrows():
                sy = row.get("start_year")
                ey = row.get("end_year")
                start = int(sy) if pd.notna(sy) and sy else None
                end = int(ey) if pd.notna(ey) and ey else None
                if (start is None or year >= start) and (end is None or year <= end):
                    return row["actor_id"]
        return matches.iloc[0]["actor_id"]

    if actor_name is not None:
        match = crosswalk[
            crosswalk["actor_name_standard"].str.contains(actor_name, case=False, na=False)
        ]
        if len(match) > 0:
            return match.iloc[0]["actor_id"]

    return f"UNKNOWN_{cow_code or actor_name or 'NA'}"
