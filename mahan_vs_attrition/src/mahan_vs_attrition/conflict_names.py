"""Centralized mapping of internal war IDs to human-readable conflict names.

All paper generation scripts MUST use this mapping to ensure no raw dataset
identifiers appear in figures, tables, or rendered output.
"""

CONFLICT_NAME_MAP: dict[str, str] = {
    "cow_iw_1": "Franco-Spanish War (1823)",
    "cow_iw_4": "Russo-Turkish War (1828–1829)",
    "cow_iw_7": "Mexican–American War",
    "cow_iw_10": "Austro-Sardinian War",
    "cow_iw_16": "Roman Republic (1849–1850)",
    "cow_iw_19": "War of the Confederation",
    "cow_iw_28": "Second Italian War of Independence",
    "cow_iw_34": "Roman Question",
    "cow_iw_37": "Neapolitan War",
    "cow_iw_40": "Second French intervention in Mexico",
    "cow_iw_43": "Ecuadorian–Colombian War",
    "cow_iw_49": "Paraguayan War",
    "cow_iw_55": "Austro-Prussian War",
    "cow_iw_58": "Franco-Prussian War",
    "cow_iw_64": "War of the Pacific",
    "cow_iw_65": "Anglo-Egyptian War",
    "cow_iw_68": "Boer War",
    "cow_iw_73": "Russo-Turkish War (1877)",
    "cow_iw_76": "Greco-Turkish War (1897)",
    "cow_iw_82": "Boxer Rebellion",
    "cow_iw_83": "Russian invasion of Manchuria",
    "cow_iw_85": "Russo-Japanese War",
    "cow_iw_97": "Italo-Turkish War",
    "cow_iw_100": "First Balkan War",
    "cow_iw_103": "Second Balkan War",
    "cow_iw_106": "World War I",
    "cow_iw_115": "Greco-Turkish War (1919–1922)",
    "cow_iw_121": "Second Sino-Japanese War",
    "cow_iw_124": "Chaco War",
    "cow_iw_127": "Second Italo-Ethiopian War",
    "cow_iw_130": "Second Sino-Japanese War",
    "cow_iw_133": "Battle of Lake Khasan",
    "cow_iw_136": "Battles of Khalkhin Gol",
    "cow_iw_139": "World War II",
    "cow_iw_140": "World War II Europe",
    "cow_iw_141": "Poland 1939",
    "cow_iw_142": "Winter War",
    "cow_iw_147": "Indo-Pakistani War of 1947–1948",
    "cow_iw_148": "Korean War",
    "cow_iw_151": "1948 Arab–Israeli War",
    "cow_iw_155": "Suez Crisis",
    "cow_iw_156": "Hungarian Revolution of 1956",
    "cow_iw_163": "Vietnam War",
    "cow_iw_169": "Six-Day War",
    "cow_iw_172": "War of Attrition",
    "cow_iw_175": "Football War",
    "cow_iw_178": "Bangladesh Liberation War",
    "cow_iw_181": "Yom Kippur War",
    "cow_iw_187": "Yom Kippur War",
    "cow_iw_190": "Soviet-Afghan War",
    "cow_iw_199": "Iran–Iraq War",
    "cow_iw_202": "Falklands War",
    "cow_iw_211": "Gulf War",
    "cow_iw_217": "Cenepa War",
    "cow_iw_218": "Iraq War 2003",
    "cow_iw_220": "Falklands War",
    "cow_iw_223": "Kargil War",
    "cow_iw_225": "United States invasion of Afghanistan",
    "cow_iw_227": "Iraq War",
    "cow_iw_nw_29": "American Civil War",
}


def get_conflict_name(war_id: str) -> str:
    """Return a human-readable conflict name for an internal war ID.

    Falls back to the raw ID if no mapping exists (so callers can detect
    missing mappings at a glance).
    """
    return CONFLICT_NAME_MAP.get(war_id, war_id)
