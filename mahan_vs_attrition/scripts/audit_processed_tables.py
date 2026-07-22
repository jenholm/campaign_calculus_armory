"""Audit script: map coverage, missingness, ID integrity, and cohort composition.

Acceptance criteria: No model changes until we know which records are usable
for which claim. Run before any DSS/SES rebuild.
"""

import json
import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = Path("data/processed")
INTERIM_DIR = Path("data/interim")
TABLES_DIR = Path("reports/tables")
TABLES_DIR.mkdir(parents=True, exist_ok=True)


def _read(name: str) -> pd.DataFrame:
    p = DATA_DIR / name
    if p.exists():
        return pd.read_parquet(p)
    return pd.DataFrame()


def audit_table_coverage() -> pd.DataFrame:
    """Number of wars by source / type / era / coverage."""
    wars = _read("wars.parquet")
    dss = _read("dss_scores.parquet")
    ses = _read("ses_scores.parquet")
    tc = _read("termination_classification.parquet")
    battles = _read("battles.parquet")
    wp = _read("war_participants.parquet")
    te = _read("termination_events.parquet")
    wy = _read("war_years.parquet")

    rows = []

    # By source
    if "source_primary" in wars.columns:
        for src, count in wars["source_primary"].value_counts().items():
            rows.append({"category": "by_source", "key": str(src), "count": int(count)})

    # By war type
    if "war_type" in wars.columns:
        for t, count in wars["war_type"].value_counts().items():
            rows.append({"category": "by_war_type", "key": str(t), "count": int(count)})

    # By era
    if "era" in wars.columns:
        for era, count in wars["era"].value_counts().items():
            rows.append({"category": "by_era", "key": str(era), "count": int(count)})

    # By confidence
    if "confidence" in wars.columns:
        for conf, count in wars["confidence"].value_counts().items():
            rows.append({"category": "by_confidence", "key": str(conf), "count": int(count)})

    # Coverage counts
    has_start = wars["start_date"].notna().sum() if "start_date" in wars.columns else 0
    has_end = wars["end_date"].notna().sum() if "end_date" in wars.columns else 0
    has_duration = wars["duration_days"].notna().sum() if "duration_days" in wars.columns else 0
    has_outcome = (
        wars["outcome_type"].astype(str).str.strip().ne("").sum()
        if "outcome_type" in wars.columns
        else 0
    )
    has_region = (
        (wars["region"].astype(str).str.strip() != "unknown").sum()
        if "region" in wars.columns
        else 0
    )

    dss_ids = set(dss["war_id"].dropna().unique()) if len(dss) > 0 else set()
    ses_ids = set(ses["war_id"].dropna().unique()) if len(ses) > 0 else set()
    tc_ids = set(tc["war_id"].dropna().unique()) if len(tc) > 0 else set()
    battle_ids = set(battles["war_id"].dropna().unique()) if len(battles) > 0 else set()
    participant_ids = set(wp["war_id"].dropna().unique()) if len(wp) > 0 else set()
    te_ids = set(te["war_id"].dropna().unique()) if len(te) > 0 else set()
    wy_ids = set(wy["war_id"].dropna().unique()) if len(wy) > 0 else set()

    both = dss_ids & ses_ids
    rows.append({"category": "coverage", "key": "total_wars", "count": int(len(wars))})
    rows.append({"category": "coverage", "key": "has_start_date", "count": int(has_start)})
    rows.append({"category": "coverage", "key": "has_end_date", "count": int(has_end)})
    rows.append({"category": "coverage", "key": "has_duration", "count": int(has_duration)})
    rows.append({"category": "coverage", "key": "has_outcome_label", "count": int(has_outcome)})
    rows.append({"category": "coverage", "key": "has_known_region", "count": int(has_region)})
    rows.append({"category": "coverage", "key": "with_dss", "count": int(len(dss_ids))})
    rows.append({"category": "coverage", "key": "with_ses", "count": int(len(ses_ids))})
    rows.append({"category": "coverage", "key": "with_both_dss_ses", "count": int(len(both))})
    rows.append({"category": "coverage", "key": "with_battle_data", "count": int(len(battle_ids))})
    rows.append({"category": "coverage", "key": "with_participants", "count": int(len(participant_ids))})
    rows.append({"category": "coverage", "key": "with_termination_events", "count": int(len(te_ids))})
    rows.append({"category": "coverage", "key": "with_war_years_data", "count": int(len(wy_ids))})

    df = pd.DataFrame(rows)
    df.to_csv(TABLES_DIR / "table_coverage.csv", index=False)
    logger.info(f"table_coverage.csv: {len(df)} rows")
    return df


def audit_missingness() -> pd.DataFrame:
    """Column-level missingness for each table."""
    tables = {
        "wars.parquet": _read("wars.parquet"),
        "war_participants.parquet": _read("war_participants.parquet"),
        "war_years.parquet": _read("war_years.parquet"),
        "battles.parquet": _read("battles.parquet"),
        "termination_events.parquet": _read("termination_events.parquet"),
        "dss_scores.parquet": _read("dss_scores.parquet"),
        "ses_scores.parquet": _read("ses_scores.parquet"),
        "termination_classification.parquet": _read("termination_classification.parquet"),
    }
    rows = []
    for name, df in tables.items():
        if len(df) == 0:
            rows.append({"table": name, "column": "(all)", "n_rows": 0, "n_missing": 0, "pct_missing": 100.0})
            continue
        for col in df.columns:
            n = len(df)
            miss = int(df[col].isna().sum())
            empty = int((df[col].astype(str).str.strip() == "").sum()) if df[col].dtype == "object" else 0
            total_missing = miss + empty
            rows.append({
                "table": name,
                "column": col,
                "n_rows": n,
                "n_missing": total_missing,
                "pct_missing": round(100 * total_missing / n, 2) if n else 0.0,
            })
    out = pd.DataFrame(rows)
    out.to_csv(TABLES_DIR / "missingness_by_table.csv", index=False)
    logger.info(f"missingness_by_table.csv: {len(out)} rows")
    return out


def audit_id_integrity() -> pd.DataFrame:
    """Duplicate IDs, referential integrity checks."""
    rows = []
    wars = _read("wars.parquet")
    wp = _read("war_participants.parquet")
    battles = _read("battles.parquet")
    te = _read("termination_events.parquet")
    dss = _read("dss_scores.parquet")
    ses = _read("ses_scores.parquet")
    tc = _read("termination_classification.parquet")

    # Duplicate war_id in wars
    if "war_id" in wars.columns:
        dup = int(wars["war_id"].duplicated().sum())
        rows.append({"check": "duplicate_war_id_in_wars", "n": dup, "status": "PASS" if dup == 0 else "FAIL"})

    # Duplicate battle_id
    if "battle_id" in battles.columns and len(battles) > 0:
        dup = int(battles["battle_id"].duplicated().sum())
        rows.append({"check": "duplicate_battle_id_in_battles", "n": dup, "status": "PASS" if dup == 0 else "FAIL"})

    # Referential integrity: war_id in participants references wars
    if len(wp) > 0 and "war_id" in wp.columns:
        wp_ids = set(wp["war_id"].dropna().unique())
        war_ids = set(wars["war_id"].dropna().unique()) if "war_id" in wars.columns else set()
        orphans = wp_ids - war_ids
        rows.append({
            "check": "wp.war_id_orphans",
            "n": len(orphans),
            "status": "PASS" if len(orphans) == 0 else "FAIL",
            "example_orphans": list(orphans)[:5],
        })

    # Referential integrity: war_id in DSS references wars
    if len(dss) > 0 and "war_id" in dss.columns:
        dss_ids = set(dss["war_id"].dropna().unique())
        war_ids = set(wars["war_id"].dropna().unique()) if "war_id" in wars.columns else set()
        orphans = dss_ids - war_ids
        rows.append({
            "check": "dss.war_id_orphans",
            "n": len(orphans),
            "status": "PASS" if len(orphans) == 0 else "FAIL",
        })

    # Referential integrity: war_id in SES references wars
    if len(ses) > 0 and "war_id" in ses.columns:
        ses_ids = set(ses["war_id"].dropna().unique())
        war_ids = set(wars["war_id"].dropna().unique()) if "war_id" in wars.columns else set()
        orphans = ses_ids - war_ids
        rows.append({
            "check": "ses.war_id_orphans",
            "n": len(orphans),
            "status": "PASS" if len(orphans) == 0 else "FAIL",
        })

    # war_years rows per war distribution
    wy = _read("war_years.parquet")
    if len(wy) > 0 and "war_id" in wy.columns:
        per_war = wy.groupby("war_id").size()
        rows.append({
            "check": "war_years_rows_per_war_min", "n": int(per_war.min()),
            "status": "INFO",
        })
        rows.append({
            "check": "war_years_rows_per_war_median", "n": int(per_war.median()),
            "status": "INFO",
        })
        rows.append({
            "check": "war_years_rows_per_war_max", "n": int(per_war.max()),
            "status": "INFO",
        })
        rows.append({
            "check": "war_years_unique_wars", "n": int(per_war.shape[0]),
            "status": "INFO",
        })

    out = pd.DataFrame(rows)
    out.to_csv(TABLES_DIR / "id_integrity_report.csv", index=False)
    logger.info(f"id_integrity_report.csv: {len(out)} rows")
    return out


def audit_cohorts() -> pd.DataFrame:
    """Define the five named cohorts and report size of each."""
    wars = _read("wars.parquet")
    dss = _read("dss_scores.parquet")
    ses = _read("ses_scores.parquet")
    battles = _read("battles.parquet")
    wp = _read("war_participants.parquet")
    wy = _read("war_years.parquet")
    tc = _read("termination_classification.parquet")

    dss_ids = set(dss["war_id"].dropna().unique()) if len(dss) > 0 else set()
    ses_ids = set(ses["war_id"].dropna().unique()) if len(ses) > 0 else set()
    battle_ids = set(battles["war_id"].dropna().unique()) if len(battles) > 0 else set()
    participant_ids = set(wp["war_id"].dropna().unique()) if len(wp) > 0 else set()
    wy_ids = set(wy["war_id"].dropna().unique()) if len(wy) > 0 else set()

    # Cohort A: COW interstate wars with IWB battle data
    if len(wars) > 0 and "war_type" in wars.columns and "source_primary" in wars.columns:
        cow_inter = wars[
            (wars["war_type"] == "interstate") & (wars["source_primary"] == "cow")
        ]
        a_ids = set(cow_inter["war_id"].dropna().unique())
    else:
        a_ids = set()

    # Cohort B: wars with SES-capability data
    b_ids = ses_ids

    # Cohort C: manually coded case studies
    cs_path = Path("data/manual/case_studies_index.csv")
    c_ids = set()
    if cs_path.exists():
        cs = pd.read_csv(cs_path)
        c_ids = set(cs["war_id"].dropna().unique())

    # Cohort D: modern conflicts with UCDP event data
    ucdp = _read("ucdp_battle_deaths.parquet")
    if "year" in ucdp.columns and len(ucdp) > 0:
        modern_years = set(ucdp["year"].dropna().unique())
    else:
        modern_years = set()
    if len(wy) > 0 and "year" in wy.columns:
        modern_wars = set(wy[wy["year"].isin(modern_years)]["war_id"].dropna().unique())
    else:
        modern_wars = set()
    d_ids = modern_wars

    # Cohort E: all conflicts (descriptive)
    e_ids = set(wars["war_id"].dropna().unique()) if len(wars) > 0 else set()

    rows = [
        {
            "cohort": "A: COW interstate + IWB battles",
            "n": len(a_ids),
            "size_of_intersection_with_B": len(a_ids & b_ids),
            "size_of_intersection_with_C": len(a_ids & c_ids),
            "use_case": "battle-decisive causation tests (DSS)",
        },
        {
            "cohort": "B: wars with SES-capability data",
            "n": len(b_ids),
            "size_of_intersection_with_A": len(a_ids & b_ids),
            "size_of_intersection_with_C": len(b_ids & c_ids),
            "use_case": "strategic exhaustion tests (SES)",
        },
        {
            "cohort": "C: manual case studies",
            "n": len(c_ids),
            "size_of_intersection_with_A": len(a_ids & c_ids),
            "size_of_intersection_with_B": len(b_ids & c_ids),
            "use_case": "validation / ground truth",
        },
        {
            "cohort": "D: modern (UCDP, 1989+)",
            "n": len(d_ids),
            "size_of_intersection_with_A": len(a_ids & d_ids),
            "size_of_intersection_with_B": len(b_ids & d_ids),
            "use_case": "modern conflict event-level analysis",
        },
        {
            "cohort": "E: all conflicts (descriptive only)",
            "n": len(e_ids),
            "size_of_intersection_with_A": len(a_ids & e_ids),
            "size_of_intersection_with_B": len(b_ids & e_ids),
            "use_case": "descriptive statistics only",
        },
    ]
    out = pd.DataFrame(rows)
    out.to_csv(TABLES_DIR / "cohort_coverage.csv", index=False)
    logger.info(f"cohort_coverage.csv: {len(out)} cohorts")
    return out


def audit_manual_vs_model() -> pd.DataFrame:
    """Compare manual DSS/SES to model DSS/SES for the case studies."""
    from mahan_vs_attrition.case_studies.validation import map_case_to_war_id, classify_manual

    cs_path = Path("data/manual/case_studies_index.csv")
    if not cs_path.exists():
        return pd.DataFrame()
    cases = pd.read_csv(cs_path)
    dss = _read("dss_scores.parquet")
    ses = _read("ses_scores.parquet")
    tc = _read("termination_classification.parquet")

    dss_map = dss.set_index("war_id")["dss_score"].to_dict() if len(dss) > 0 else {}
    ses_map = ses.set_index("war_id")["ses_score"].to_dict() if len(ses) > 0 else {}
    tc_map = (
        tc.set_index("war_id")["termination_type_model"].to_dict()
        if len(tc) > 0 and "termination_type_model" in tc.columns
        else {}
    )

    rows = []
    for _, c in cases.iterrows():
        wid = map_case_to_war_id(c["war_name"])
        rows.append({
            "war_id_mapped": wid or "manual_only",
            "war_name": c["war_name"],
            "manual_dss": float(c["dss"]),
            "manual_ses": float(c["ses"]),
            "model_dss": float(dss_map[wid]) if wid in dss_map else None,
            "model_ses": float(ses_map[wid]) if wid in ses_map else None,
            "manual_class": classify_manual(c["dominant_mechanism"]),
            "model_class": tc_map.get(wid) if wid else None,
            "dss_delta": (
                float(dss_map[wid]) - float(c["dss"]) if wid in dss_map else None
            ),
            "ses_delta": (
                float(ses_map[wid]) - float(c["ses"]) if wid in ses_map else None
            ),
        })
    out = pd.DataFrame(rows)
    out.to_csv(TABLES_DIR / "manual_vs_model_deltas.csv", index=False)
    logger.info(f"manual_vs_model_deltas.csv: {len(out)} cases")
    return out


def main():
    audit_table_coverage()
    audit_missingness()
    audit_id_integrity()
    audit_cohorts()
    audit_manual_vs_model()
    logger.info(f"Audit complete. Outputs in {TABLES_DIR}/")


if __name__ == "__main__":
    main()
