"""Normalization pipeline: builds wars, war_participants, war_years, battles, and termination_events tables."""

import logging
from pathlib import Path

import numpy as np
import pandas as pd

from mahan_vs_attrition.normalize.actor_crosswalk import build_actor_crosswalk, resolve_actor

logger = logging.getLogger(__name__)


def _to_year(val):
    """Extract a year integer from various formats."""
    if val is None:
        return None
    try:
        return int(float(str(val).strip()))
    except (ValueError, TypeError):
        return None


def _make_date(year, month=None, day=None):
    """Build a date from possibly-None components."""
    y = _to_year(year)
    if y is None:
        return pd.NaT
    if y < 100:
        return pd.NaT
    m = _to_year(month) if month is not None else 1
    d = _to_year(day) if day is not None else 1
    m = max(1, min(12, m)) if m else 1
    d = max(1, min(31, d)) if d else 1
    try:
        return pd.Timestamp(year=y, month=m, day=d)
    except (ValueError, TypeError):
        return pd.Timestamp(year=y, month=1, day=1)


def _assign_era(year):
    """Assign era label based on year."""
    if pd.isna(year):
        return "unknown"
    if year <= 1399:
        return "classical_to_1399"
    if year <= 1788:
        return "early_modern_1400_1788"
    if year <= 1815:
        return "revolutionary_napoleonic_1789_1815"
    if year <= 1913:
        return "industrial_1816_1913"
    if year <= 1945:
        return "world_war_1914_1945"
    if year <= 1991:
        return "cold_war_1946_1991"
    if year <= 2021:
        return "post_cold_war_1992_2021"
    return "current_2022_present"


def _assign_confidence(source_primary, war_type, date_precision="year"):
    """Assign a confidence grade A-E."""
    modern = {"cow", "ucdp", "sipri", "vdem"}
    if source_primary in modern and war_type in ("interstate", "intrastate"):
        return "A" if date_precision == "day" else "B"
    if source_primary == "brecke":
        return "C"
    return "D"


def _region_from_cow_code(cow_code):
    """Simple region mapping from COW country code geographic zones."""
    americas = range(2, 221)   # USA=2, Canada=20, Mexico=70, Central/South America
    europe = range(220, 400)
    africa = range(400, 600)
    asia_mideast = range(600, 800)
    if cow_code in americas:
        return "americas"
    if cow_code in europe:
        return "europe"
    if cow_code in africa:
        return "africa"
    if cow_code in asia_mideast:
        return "asia_mideast"
    return None


def build_wars_table(
    cow_war_df: pd.DataFrame,
    brecke_df: pd.DataFrame,
    output_dir: Path,
) -> pd.DataFrame:
    """Build unified wars table from COW and Brecke datasets."""
    records = []

    # COW war data: split by source (warnum=interstate, WarNum=intrastate)
    if len(cow_war_df) > 0:
        inter = cow_war_df[cow_war_df["warnum"].notna()].drop_duplicates(
            subset=["warnum"]
        )
        for _, row in inter.iterrows():
            start = _make_date(
                row.get("warstrtyr"),
                row.get("warstrtmnth"),
                row.get("warstrtday"),
            )
            end = _make_date(
                row.get("warendyr"),
                row.get("warendmnth"),
                row.get("warenday"),
            )
            era = _assign_era(start.year if pd.notna(start) else None)
            confidence = _assign_confidence("cow", "interstate", "day")
            region = _region_from_cow_code(int(float(row.get("statea", 0))) if pd.notna(row.get("statea")) else None)
            records.append(
                {
                    "war_id": f"cow_iw_{int(row['warnum'])}",
                    "war_name": "",
                    "source_primary": "cow",
                    "source_war_id": str(int(row["warnum"])),
                    "war_type": "interstate",
                    "start_date": start,
                    "end_date": end,
                    "outcome_type": row.get("outcomea", ""),
                    "region": region or "unknown",
                    "era": era,
                    "termination_type_manual": "",
                    "termination_type_model": "",
                    "confidence": confidence,
                    "notes": "",
                }
            )

        # Per-WarNum sequence for unique war_id (WarNum is the war number, not unique per sub-war)
        war_num_seq: dict[int, int] = {}
        intra_rows = cow_war_df[cow_war_df["WarNum"].notna()].to_dict("records")
        for row in intra_rows:
            wn = int(float(row["WarNum"]))
            war_num_seq[wn] = war_num_seq.get(wn, 0) + 1
            seq = war_num_seq[wn]
            unique_id = f"{wn}_{seq}"
            start = _make_date(
                row.get("StartYr1"),
                row.get("StartMo1"),
                row.get("StartDy1"),
            )
            end = _make_date(
                row.get("EndYr1"),
                row.get("EndMo1"),
                row.get("EndDy1"),
            )
            era = _assign_era(start.year if pd.notna(start) else None)
            confidence = _assign_confidence("cow", str(row.get("WarType", "intrastate")), "day")
            region = _region_from_cow_code(int(float(row.get("CcodeA", 0))) if pd.notna(row.get("CcodeA")) else None)
            records.append(
                {
                    "war_id": f"cow_s_{unique_id}",
                    "war_name": row.get("WarName", ""),
                    "source_primary": "cow",
                    "source_war_id": str(int(row["WarNum"])),
                    "war_type": str(row.get("WarType", "intrastate")),
                    "start_date": start,
                    "end_date": end,
                    "outcome_type": "",
                    "region": region or "unknown",
                    "era": era,
                    "termination_type_manual": "",
                    "termination_type_model": "",
                    "confidence": confidence,
                    "notes": "",
                }
            )

    # Brecke conflict data
    if len(brecke_df) > 0:
        for idx, row in brecke_df.iterrows():
            name = row.get("Name") or row.get("Common Name", "") or ""
            cname = row.get("Common Name")
            cname = cname if pd.notna(cname) else ""
            start = _make_date(
                row.get("StartYear"),
                row.get("StartMonth"),
                row.get("StartDay"),
            )
            end = _make_date(
                row.get("EndYear"),
                row.get("EndMonth"),
                row.get("EndDay"),
            )
            era = _assign_era(start.year if pd.notna(start) else None)
            records.append(
                {
                    "war_id": f"brecke_{idx}",
                    "war_name": str(name).strip(),
                    "source_primary": "brecke",
                    "source_war_id": str(idx),
                    "war_type": "non_state",
                    "start_date": start,
                    "end_date": end,
                    "outcome_type": "",
                    "region": "unknown",
                    "era": era,
                    "termination_type_manual": "",
                    "termination_type_model": "",
                    "confidence": "C",
                    "notes": "",
                }
            )

    wars = pd.DataFrame(records)

    for col in wars.select_dtypes(include=["object", "str"]).columns:
        if col in ("start_date", "end_date"):
            continue
        wars[col] = wars[col].astype(str)

    if len(wars) > 0 and "start_date" in wars.columns:
        wars["duration_days"] = (
            wars["end_date"] - wars["start_date"]
        ).dt.days

    output_dir.mkdir(parents=True, exist_ok=True)
    wars.to_parquet(output_dir / "wars.parquet", index=False)
    logger.info(f"Wars table: {len(wars)} wars")
    return wars


def build_war_years(
    wars_df: pd.DataFrame,
    nmc_df: pd.DataFrame,
    ucdp_df: pd.DataFrame,
    actor_crosswalk: pd.DataFrame,
    output_dir: Path,
    cow_war_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Build participant-year table from NMC/UCDP indicators.

    Merges COW battle deaths from interstate (batdtha/batdthb -> deaths_best)
    and intrastate (TotalBDeaths -> deaths_best) data into the war-years table
    so SES has access to casualties for pre-1989 wars.
    """
    if len(nmc_df) == 0:
        logger.warning("No NMC data available for war_years build")
        return pd.DataFrame()

    war_year_ranges = []
    for _, war in wars_df.iterrows():
        start = war.get("start_date")
        end = war.get("end_date")
        if pd.isna(start) or pd.isna(end):
            continue
        if start.year < 1816 or end.year > 2022:
            continue
        years = range(start.year, end.year + 1)
        for y in years:
            war_year_ranges.append(
                {
                    "war_id": war["war_id"],
                    "year": y,
                    "war_name": war.get("war_name", ""),
                }
            )

    war_years = pd.DataFrame(war_year_ranges)
    if len(war_years) == 0:
        logger.warning("No war years matched NMC time range (1816-2022)")
        return war_years

    war_years = war_years.merge(nmc_df, on="year", how="left")

    # Merge UCDP battle deaths (covers 1989+)
    if len(ucdp_df) > 0 and "year" in ucdp_df.columns:
        ucdp_agg = ucdp_df.groupby("year").agg(
            battle_deaths=("deaths_best", "sum")
        ).reset_index()
        war_years = war_years.merge(ucdp_agg, on="year", how="left")

    # Backfill COW battle deaths for pre-1989 wars
    if cow_war_df is not None and len(cow_war_df) > 0:
        cow_deaths: dict[str, float] = {}

        # Interstate: batdths column (total battle deaths per dyadic row)
        inter = cow_war_df[cow_war_df["warnum"].notna()]
        if len(inter) > 0 and "batdths" in inter.columns:
            for _, row in inter.iterrows():
                wid = f"cow_iw_{int(float(row['warnum']))}"
                d = row.get("batdths")
                if pd.notna(d) and d > 0:
                    cow_deaths[wid] = max(cow_deaths.get(wid, 0), float(d))

        # Intrastate: TotalBDeaths column. Per-WarNum sequence to match build_wars_table.
        war_num_seq_d: dict[int, int] = {}
        intra = cow_war_df[cow_war_df["WarNum"].notna()]
        if len(intra) > 0 and "TotalBDeaths" in intra.columns:
            for _, row in intra.iterrows():
                wn = int(float(row["WarNum"]))
                war_num_seq_d[wn] = war_num_seq_d.get(wn, 0) + 1
                wid = f"cow_s_{wn}_{war_num_seq_d[wn]}"
                d = row.get("TotalBDeaths")
                if pd.notna(d) and d > 0:
                    cow_deaths[wid] = max(cow_deaths.get(wid, 0), float(d))

        if cow_deaths:
            cow_deaths_df = pd.DataFrame(
                list(cow_deaths.items()), columns=["war_id", "cow_total_deaths"]
            )
            war_years = war_years.merge(cow_deaths_df, on="war_id", how="left")
            # Fill NaN battle_deaths from COW totals (evenly distributed across years)
            war_years["battle_deaths"] = war_years["battle_deaths"].fillna(
                war_years.groupby("war_id")["cow_total_deaths"].transform(
                    lambda x: x.iloc[0] / len(x) if x.notna().any() else None
                )
            )
            war_years = war_years.drop(columns=["cow_total_deaths"])

    output_dir.mkdir(parents=True, exist_ok=True)
    war_years.to_parquet(output_dir / "war_years.parquet", index=False)
    logger.info(f"War-years table: {len(war_years)} rows")
    return war_years


def build_participants(
    wars_df: pd.DataFrame,
    cow_war_df: pd.DataFrame,
    actor_crosswalk: pd.DataFrame,
    output_dir: Path,
) -> pd.DataFrame:
    """Build war_participants table from COW war data."""
    records = []

    # Interstate participants: from directed dyadic data (statea/stateb = COW numeric)
    inter = cow_war_df[cow_war_df["warnum"].notna()]
    if len(inter) > 0:
        for _, row in inter.iterrows():
            warnum = row.get("warnum")
            side_a = row.get("statea")
            side_b = row.get("stateb")
            year = row.get("warstrtyr")
            if pd.notna(side_a) and float(side_a) > 0:
                aid = resolve_actor(
                    actor_crosswalk, cow_code=int(float(side_a)), year=_to_year(year)
                )
                records.append({
                    "war_id": f"cow_iw_{int(float(warnum))}",
                    "actor_id": aid,
                    "role": "combatant",
                    "side": "A",
                })
            if pd.notna(side_b) and float(side_b) > 0:
                bid = resolve_actor(
                    actor_crosswalk, cow_code=int(float(side_b)), year=_to_year(year)
                )
                records.append({
                    "war_id": f"cow_iw_{int(float(warnum))}",
                    "actor_id": bid,
                    "role": "combatant",
                    "side": "B",
                })

    # Intrastate participants: from SideA/SideB text names
    intra = cow_war_df[cow_war_df["WarNum"].notna()]
    if len(intra) > 0:
        war_num_seq_p: dict[int, int] = {}
        for _, row in intra.iterrows():
            warnum = row.get("WarNum")
            side_a = row.get("SideA")
            side_b = row.get("SideB")
            side_a_code = row.get("CcodeA")
            year = row.get("StartYr1")
            wn_p = int(float(warnum))
            war_num_seq_p[wn_p] = war_num_seq_p.get(wn_p, 0) + 1
            war_id = f"cow_s_{wn_p}_{war_num_seq_p[wn_p]}"

            if pd.notna(side_a_code) and float(side_a_code) > 0:
                aid = resolve_actor(
                    actor_crosswalk, cow_code=int(float(side_a_code)), year=_to_year(year)
                )
                records.append({
                    "war_id": war_id, "actor_id": aid,
                    "role": "combatant", "side": "A",
                })
            elif pd.notna(side_a):
                name = str(side_a).strip()
                if name and name not in ("-9", "-8", "nan"):
                    aid = resolve_actor(
                        actor_crosswalk, actor_name=name, year=_to_year(year)
                    )
                    if aid and not aid.startswith("UNKNOWN"):
                        records.append({
                            "war_id": war_id, "actor_id": aid,
                            "role": "combatant", "side": "A",
                        })

            if pd.notna(side_b):
                name = str(side_b).strip()
                if name and name not in ("-9", "-8", "nan"):
                    bid = resolve_actor(
                        actor_crosswalk, actor_name=name, year=_to_year(year)
                    )
                    if bid and not bid.startswith("UNKNOWN"):
                        records.append({
                            "war_id": war_id, "actor_id": bid,
                            "role": "combatant", "side": "B",
                        })

    participants = pd.DataFrame(records)
    for col in participants.select_dtypes(include=["object", "str"]).columns:
        participants[col] = participants[col].astype(str)

    output_dir.mkdir(parents=True, exist_ok=True)
    participants.to_parquet(output_dir / "war_participants.parquet", index=False)
    logger.info(f"War participants table created: {len(participants)} rows")
    return participants


def build_battles_table(
    iwb_df: pd.DataFrame,
    wars_df: pd.DataFrame,
    output_dir: Path,
) -> pd.DataFrame:
    """Build standardized battles.parquet from IWB data."""
    if len(iwb_df) == 0:
        logger.warning("No IWB data available for battles table")
        return pd.DataFrame()

    iwb = iwb_df.copy()

    # Ensure endDate is datetime
    iwb["endDate"] = pd.to_datetime(iwb["endDate"], errors="coerce")

    # Map war_id from cowNum
    iwb["war_id"] = "cow_iw_" + iwb["cowNum"].astype(int).astype(str)

    # Get war end dates for distance_to_war_end_days
    war_end_dates = {}
    for _, r in wars_df.iterrows():
        if pd.notna(r.get("end_date")):
            war_end_dates[r["war_id"]] = pd.to_datetime(r["end_date"])

    # Per-war sequence counter for unique battle_id (iwdNum is dyad, not unique)
    war_seq: dict[str, int] = {}
    battle_records = []
    for _, row in iwb.iterrows():
        wid = row["war_id"]
        war_end = war_end_dates.get(wid)
        battle_end = row.get("endDate")
        distance = None
        if pd.notna(battle_end) and war_end is not None:
            distance = (war_end - battle_end).days

        war_seq[wid] = war_seq.get(wid, 0) + 1
        seq = war_seq[wid]

        battle_records.append({
            "battle_id": f"battle_{row['cowNum']}_{row['iwdNum']}_{seq}",
            "war_id": wid,
            "battle_name": str(row.get("battleName", "")),
            "start_date": row.get("startDate"),
            "end_date": battle_end,
            "location": "",
            "winner": str(row.get("victor", "")),
            "loser": "",
            "participants": f"{row.get('attacker', '')} vs {row.get('defender', '')}",
            "distance_to_war_end_days": distance,
            "decisive_claimed_by_sources": "",
            "source_confidence": "B",
        })

    battles = pd.DataFrame(battle_records)
    output_dir.mkdir(parents=True, exist_ok=True)
    battles.to_parquet(output_dir / "battles.parquet", index=False)
    logger.info(f"Battles table: {len(battles)} battles")
    return battles


def build_termination_events(
    wars_df: pd.DataFrame,
    battles_df: pd.DataFrame,
    output_dir: Path,
) -> pd.DataFrame:
    """Build termination_events.parquet (populated from IWB last-battle data)."""
    records = []
    battle_winners = {}
    if len(battles_df) > 0:
        for _, b in battles_df.iterrows():
            wid = b.get("war_id")
            if not wid:
                continue
            prev = battle_winners.get(wid)
            end_date = b.get("end_date")
            if prev is None or (pd.notna(end_date) and pd.notna(prev.get("end_date")) and end_date > prev["end_date"]):
                battle_winners[wid] = {
                    "battle_id": b.get("battle_id"),
                    "winner": b.get("winner"),
                    "end_date": end_date,
                    "last_battle_name": b.get("battle_name"),
                }

    for _, war in wars_df.iterrows():
        wid = war["war_id"]
        last = battle_winners.get(wid, {})
        termination_date = war.get("end_date")
        rec = {
            "war_id": wid,
            "termination_date": termination_date,
            "termination_event_name": last.get("last_battle_name", ""),
            "termination_event_type": "battle" if last else "unknown",
            "battle_id_if_applicable": last.get("battle_id", ""),
            "capital_seized": "",
            "government_collapsed": "",
            "treaty_signed": "",
            "armistice_signed": "",
            "surrender_signed": "",
            "regime_change": "",
            "alliance_exit": "",
            "notes": "",
        }
        if last and pd.notna(last.get("end_date")) and pd.notna(termination_date):
            days_diff = (pd.to_datetime(termination_date) - last["end_date"]).days
            if days_diff is not None and abs(days_diff) <= 30:
                rec["surrender_signed"] = "1"
        records.append(rec)

    result = pd.DataFrame(records)
    output_dir.mkdir(parents=True, exist_ok=True)
    result.to_parquet(output_dir / "termination_events.parquet", index=False)
    logger.info(f"Termination events: {len(result)} rows")
    return result


def generate_missingness_report(output_dir: Path) -> dict:
    """Generate missingness report for all processed tables."""
    report = {}
    tables = ["wars.parquet", "war_participants.parquet", "war_years.parquet",
              "battles.parquet", "termination_events.parquet",
              "dss_scores.parquet", "ses_scores.parquet", "termination_classification.parquet"]
    for table_name in tables:
        path = output_dir / table_name
        if not path.exists():
            report[table_name] = {"status": "missing", "rows": 0, "missing_pct": {}}
            continue
        df = pd.read_parquet(path)
        missing = df.isna().mean().mul(100).round(1).to_dict()
        report[table_name] = {
            "status": "present",
            "rows": len(df),
            "columns": len(df.columns),
            "missing_pct": {k: v for k, v in missing.items() if v > 0},
        }
    report["total_missing_tables"] = sum(1 for v in report.values() if v["status"] == "missing")
    report["total_tables_checked"] = len(tables)
    import json
    (output_dir / "missingness_report.json").write_text(json.dumps(report, indent=2, default=str))
    logger.info(f"Missingness report generated: {report['total_tables_checked']} tables")
    return report


def run(
    cow_war_path: Path,
    cow_nmc_path: Path,
    ucdp_path: Path,
    brecke_path: Path,
    iwb_path: Path | None = None,
    output_dir: Path | None = None,
) -> dict:
    """Run full normalization pipeline."""
    if output_dir is None:
        output_dir = Path("data/processed")
    cow_war = pd.read_parquet(cow_war_path) if cow_war_path.exists() else pd.DataFrame()
    nmc = pd.read_parquet(cow_nmc_path) if cow_nmc_path.exists() else pd.DataFrame()
    ucdp = pd.read_parquet(ucdp_path) if ucdp_path.exists() else pd.DataFrame()
    brecke = pd.read_parquet(brecke_path) if brecke_path.exists() else pd.DataFrame()
    iwb = pd.read_parquet(iwb_path) if iwb_path and iwb_path.exists() else pd.DataFrame()

    crosswalk = build_actor_crosswalk(output_dir, cow_war_df=cow_war)
    wars = build_wars_table(cow_war, brecke, output_dir)
    participants = build_participants(wars, cow_war, crosswalk, output_dir)
    war_years = build_war_years(wars, nmc, ucdp, crosswalk, output_dir, cow_war_df=cow_war)
    battles = build_battles_table(iwb, wars, output_dir)
    termination_events = build_termination_events(wars, battles, output_dir)
    missingness = generate_missingness_report(output_dir)

    return {
        "wars": len(wars),
        "participants": len(participants),
        "war_years": len(war_years),
        "battles": len(battles),
        "termination_events": len(termination_events),
        "crosswalk": len(crosswalk),
        "missing_tables": missingness["total_missing_tables"],
    }
