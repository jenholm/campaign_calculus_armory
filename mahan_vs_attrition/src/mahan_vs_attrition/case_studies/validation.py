"""Case study validation: compare manual historical classifications to model output."""

import json
import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def map_case_to_war_id(war_name: str) -> str:
    """Map a case study war name to the COW war_id used in the model.

    Returns cow_iw_XX for matching interstate wars, or the original id otherwise.
    """
    NAME_TO_WAR_ID = {
        "Franco-Prussian War": "cow_iw_58",
        "Russo-Japanese War": "cow_iw_85",
        "Gulf War 1991": "cow_iw_211",
        "World War I": "cow_iw_106",
        "World War II Pacific": "cow_iw_139",
        "World War II Eastern Front": "cow_iw_139",
        "World War II Europe": "cow_iw_140",
        "Vietnam War": "cow_iw_163",
        "Six Day War": "cow_iw_178",
        "Iran-Iraq War": "cow_iw_199",
        "Korean War": "cow_iw_148",
        "Soviet-Afghan War": "cow_iw_190",
        "American Civil War": "cow_iw_nw_29",
        "Yom Kippur War": "cow_iw_187",
        "Iraq War 2003": "cow_iw_218",
        "Poland 1939": "cow_iw_141",
        "Boer War": "cow_iw_68",
        "Chechen War First": "ucdp_26",
        "French Indochina": "manual_french_indochina",
        "Eritrean War": "manual_eritrean_war",
        "Seven Years War": "manual_seven_years",
        "War of 1812": "manual_war_1812",
        "Winter War": "manual_winter_war",
        "Falklands War": "cow_iw_220",
        "Chinese Civil War (Final Phase)": "manual_korean_chinese",
        "Napoleonic Wars": "manual_napoleonic",
        "Russo-Turkish War 1877": "cow_iw_73",
        "Second Punic War": "manual_second_punic",
        "Peloponnesian War": "manual_peloponnesian",
        "Thirty Years War": "manual_thirty_years",
    }
    return NAME_TO_WAR_ID.get(war_name, "")


def classify_manual(mechanism: str) -> tuple:
    """Map manual mechanism to model classification label.

    Returns (classification_label, data_quality).
    Manual classifications are expert judgments, so data_quality="high".
    """
    MAP = {
        "decisive_battle": "decisive_battle_or_campaign",
        "decisive_campaign": "decisive_battle_or_campaign",
        "strategic_exhaustion": "strategic_exhaustion",
        "logistics_collapse": "strategic_exhaustion",
        "will_collapse": "strategic_exhaustion",
        "alliance_failure": "strategic_exhaustion",
        "mixed": "mixed",
        "negotiated_stalemate": "uncertain_or_negotiated",
    }
    return MAP.get(mechanism, "uncertain_or_negotiated"), "high"


def classify_model_score(dss: float, ses: float) -> str:
    """Apply hybrid classification rule to a DSS/SES pair."""
    dss_missing = dss is None or pd.isna(dss)
    ses_missing = ses is None or pd.isna(ses)
    if dss_missing and ses_missing:
        return "data_insufficient"
    if dss_missing and not ses_missing:
        return "ses_only_insufficient"
    if not dss_missing and ses_missing:
        return "dss_only_insufficient"
    ses_val = ses if not ses_missing else 0
    min_one = 45
    both_above = 65
    dec_margin = 20
    exh_margin = 20
    if max(dss, ses_val) < min_one:
        return "uncertain_or_negotiated"
    if dss >= both_above and ses_val >= both_above:
        return "mixed"
    if dss - ses_val >= dec_margin:
        return "decisive_battle_or_campaign"
    if ses_val - dss >= exh_margin:
        return "strategic_exhaustion"
    return "mixed_or_uncertain"


def validate_case_studies(
    case_studies_path: Path,
    dss_path: Path,
    ses_path: Path,
    output_path: Path,
) -> dict:
    """Validate manual case study classifications against model output.

    Args:
        case_studies_path: CSV index of manual case studies.
        dss_path: Parquet of model DSS scores.
        ses_path: Parquet of model SES scores.
        output_path: Where to write the validation report (JSON).

    Returns:
        Dict with validation results.
    """
    cases = pd.read_csv(case_studies_path)
    dss_df = pd.read_parquet(dss_path) if dss_path.exists() else pd.DataFrame()
    ses_df = pd.read_parquet(ses_path) if ses_path.exists() else pd.DataFrame()

    # Detect schema: new manual_case_scores.csv vs old case_studies_index.csv
    is_new_schema = "manual_dss" in cases.columns
    if is_new_schema:
        dss_col = "manual_dss"
        ses_col = "manual_ses"
        class_col = "manual_class"
        mechanism_col = "dominant_mechanism"
    else:
        dss_col = "dss"
        ses_col = "ses"
        class_col = "dominant_mechanism"
        mechanism_col = "dominant_mechanism"

    results = []
    for _, case in cases.iterrows():
        war_id = str(case.get("war_id", ""))
        # If war_id starts with "manual_", it is a manual-only war; no model comparison
        model_wid = war_id if not war_id.startswith("manual_") else ""
        # Fallback: try name mapping for mapped names
        if not model_wid:
            mapped = map_case_to_war_id(case["war_name"])
            if mapped and not mapped.startswith("manual_"):
                model_wid = mapped
        manual_dss = float(case[dss_col])
        manual_ses = float(case[ses_col])
        manual_mech = str(case[mechanism_col])
        if is_new_schema:
            manual_class = str(case.get("manual_class", ""))
            manual_data_quality = "high"
            if not manual_class:
                manual_class, manual_data_quality = classify_manual(manual_mech)
        else:
            manual_class, manual_data_quality = classify_manual(manual_mech)

        # Get model scores
        model_dss = None
        model_ses = None
        if model_wid and len(dss_df) > 0:
            d = dss_df[dss_df["war_id"] == model_wid]
            if len(d) > 0:
                model_dss = float(d.iloc[0]["dss_score"])
        if model_wid and len(ses_df) > 0:
            s = ses_df[ses_df["war_id"] == model_wid]
            if len(s) > 0:
                model_ses = float(s.iloc[0]["ses_score"])

        # Compute deltas
        dss_delta = model_dss - manual_dss if model_dss is not None else None
        ses_delta = model_ses - manual_ses if model_ses is not None else None

        # Compute model classification
        model_class = classify_model_score(model_dss, model_ses) if (model_dss is not None or model_ses is not None) else None

        # Class agreement
        agreement = (model_class == manual_class) if model_class else None

        # Quadrant check (which model quadrant do manual scores fall into)
        manual_class_from_scores = classify_model_score(manual_dss, manual_ses)

        # Notes
        notes = []
        if dss_delta is not None and abs(dss_delta) > 25:
            notes.append(f"Large DSS gap (model={model_dss:.0f} vs manual={manual_dss:.0f})")
        if ses_delta is not None and abs(ses_delta) > 25:
            notes.append(f"Large SES gap (model={model_ses:.0f} vs manual={manual_ses:.0f})")
        if model_class and agreement is False:
            notes.append(f"Classification mismatch: manual={manual_class} vs model={model_class}")
        if manual_class != manual_class_from_scores:
            notes.append(
                f"Manual mechanism '{case['dominant_mechanism']}' classifies as {manual_class} "
                f"but manual DSS/SES thresholds would give {manual_class_from_scores}"
            )

        results.append({
            "war_id": model_wid or war_id or "manual",
            "war_name": case["war_name"],
            "manual_dss": manual_dss,
            "manual_ses": manual_ses,
        "manual_classification": manual_class,
        "manual_data_quality": manual_data_quality,
        "manual_mechanism": manual_mech,
            "model_dss": model_dss,
            "model_ses": model_ses,
            "dss_delta": round(dss_delta, 1) if dss_delta is not None else None,
            "ses_delta": round(ses_delta, 1) if ses_delta is not None else None,
            "model_classification": model_class,
            "agreement": agreement,
            "notes": "; ".join(notes) if notes else "OK",
        })

    # Aggregate
    n_evaluated = sum(1 for r in results if r["model_dss"] is not None)
    n_agreement = sum(1 for r in results if r["agreement"] is True)
    summary = {
        "n_case_studies": len(results),
        "n_evaluated_against_model": n_evaluated,
        "n_classification_agreement": n_agreement,
        "agreement_pct": round(100 * n_agreement / n_evaluated, 1) if n_evaluated > 0 else 0,
        "mean_dss_delta": round(
            sum(r["dss_delta"] for r in results if r["dss_delta"] is not None) /
            sum(1 for r in results if r["dss_delta"] is not None), 1
        ) if any(r["dss_delta"] is not None for r in results) else None,
        "mean_ses_delta": round(
            sum(r["ses_delta"] for r in results if r["ses_delta"] is not None) /
            sum(1 for r in results if r["ses_delta"] is not None), 1
        ) if any(r["ses_delta"] is not None for r in results) else None,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps({"summary": summary, "cases": results}, indent=2, default=str))
    logger.info(
        f"Case study validation: {summary['n_classification_agreement']}/{summary['n_evaluated_against_model']} "
        f"classifications match ({summary['agreement_pct']}%)"
    )
    return {"summary": summary, "cases": results}


def case_study_validation_report_text(validation: dict) -> str:
    """Format validation results as readable text."""
    lines = []
    lines.append("# Case Study Validation Report")
    lines.append("")
    summary = validation["summary"]
    lines.append("## Summary")
    lines.append(f"- Total case studies: {summary['n_case_studies']}")
    lines.append(f"- Evaluated against model: {summary['n_evaluated_against_model']}")
    lines.append(f"- Classification agreement: {summary['n_classification_agreement']}/{summary['n_evaluated_against_model']} ({summary['agreement_pct']}%)")
    if summary["mean_dss_delta"] is not None:
        lines.append(f"- Mean DSS delta (model - manual): {summary['mean_dss_delta']:+.1f}")
    if summary["mean_ses_delta"] is not None:
        lines.append(f"- Mean SES delta (model - manual): {summary['mean_ses_delta']:+.1f}")
    lines.append("")
    lines.append("## Per-case comparison")
    lines.append("")
    lines.append("| War | Manual DSS | Manual SES | Manual Class | Model DSS | Model SES | Model Class | Agreement | Notes |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|:---:|---|")
    for r in validation["cases"]:
        model_dss = f"{r['model_dss']:.0f}" if r["model_dss"] is not None else "n/a"
        model_ses = f"{r['model_ses']:.0f}" if r["model_ses"] is not None else "n/a"
        model_class = r["model_classification"] or "n/a"
        agree = "OK" if r["agreement"] is True else ("X" if r["agreement"] is False else "?")
        lines.append(
            f"| {r['war_name']} | {r['manual_dss']:.0f} | {r['manual_ses']:.0f} | "
            f"{r['manual_classification']} | {model_dss} | {model_ses} | {model_class} | "
            f"{agree} | {r['notes']} |"
        )
    return "\n".join(lines) + "\n"
