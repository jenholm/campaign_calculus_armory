"""War termination classification using DSS, SES, and LSS.

Hybrid rule: dominant-axis + closeness band.
- Both scores missing (NaN/None): data_insufficient
- Only DSS exists (SES missing): dss_only_insufficient
- Only SES exists (DSS missing): ses_only_insufficient
- Both exist:
  - max(DSS,SES) < 45 -> uncertain_or_negotiated
  - both >= 65 -> mixed
  - DSS - SES >= 20 -> decisive_battle_or_campaign
  - SES - DSS >= 20 -> strategic_exhaustion
  - else -> mixed_or_uncertain

Each classification result includes a `data_quality` field:
- "high": both DSS and SES scored
- "medium": only one axis scored
- "low": no empirical scores available
"""

import logging
from pathlib import Path
from typing import Optional

import pandas as pd
import yaml

logger = logging.getLogger(__name__)

METRIC_WEIGHTS_PATH = Path(__file__).parents[3] / "config" / "metric_weights.yml"

# Hybrid rule constants (configurable via config/metric_weights.yml)
HYBRID = {
    "min_one_axis": 45,        # both below -> uncertain
    "mixed_both_above": 65,    # both above -> mixed
    "decisive_margin": 20,     # DSS - SES >= 20 -> decisive
    "exhaustion_margin": 20,   # SES - DSS >= 20 -> exhaustion
}


def load_thresholds() -> dict:
    with open(METRIC_WEIGHTS_PATH) as f:
        config = yaml.safe_load(f)
    return config.get("classification_thresholds_hybrid", HYBRID)


def classify_termination(
    dss_score: Optional[float] = None,
    ses_score: Optional[float] = None,
    lss_score: Optional[float] = None,
) -> dict:
    """Classify war termination type using hybrid rule."""
    t = load_thresholds()

    min_one = t.get("min_one_axis", HYBRID["min_one_axis"])
    both_above = t.get("mixed_both_above", HYBRID["mixed_both_above"])
    dec_margin = t.get("decisive_margin", HYBRID["decisive_margin"])
    exh_margin = t.get("exhaustion_margin", HYBRID["exhaustion_margin"])

    dss_missing = dss_score is None or (isinstance(dss_score, float) and pd.isna(dss_score))
    ses_missing = ses_score is None or (isinstance(ses_score, float) and pd.isna(ses_score))

    dss = dss_score if not dss_missing else 0.0
    ses = ses_score if not ses_missing else 0.0

    # Missing data handling
    if dss_missing and ses_missing:
        result = {
            "termination_type_model": "data_insufficient",
            "primary_mechanism": "data_insufficient",
            "decision_logic": "both DSS and SES missing",
        }
    elif dss_missing and not ses_missing:
        result = {
            "termination_type_model": "ses_only_insufficient",
            "primary_mechanism": "data_insufficient",
            "decision_logic": "DSS missing, only SES available",
        }
    elif not dss_missing and ses_missing:
        result = {
            "termination_type_model": "dss_only_insufficient",
            "primary_mechanism": "data_insufficient",
            "decision_logic": "SES missing, only DSS available",
        }
    elif max(dss, ses) < min_one:
        result = {
            "termination_type_model": "uncertain_or_negotiated",
            "primary_mechanism": "uncertain",
            "decision_logic": f"max(DSS,SES)={max(dss, ses):.1f} < {min_one}",
        }
    elif dss >= both_above and ses >= both_above:
        result = {
            "termination_type_model": "mixed",
            "primary_mechanism": "mixed",
            "decision_logic": f"both DSS={dss:.1f} and SES={ses:.1f} >= {both_above}",
        }
    elif dss - ses >= dec_margin:
        result = {
            "termination_type_model": "decisive_battle_or_campaign",
            "primary_mechanism": "decisive_shock",
            "decision_logic": f"DSS-SES={dss - ses:.1f} >= {dec_margin}",
        }
    elif ses - dss >= exh_margin:
        result = {
            "termination_type_model": "strategic_exhaustion",
            "primary_mechanism": "strategic_exhaustion",
            "decision_logic": f"SES-DSS={ses - dss:.1f} >= {exh_margin}",
        }
    else:
        result = {
            "termination_type_model": "mixed_or_uncertain",
            "primary_mechanism": "mixed_or_uncertain",
            "decision_logic": f"close (|DSS-SES|={abs(dss - ses):.1f} < margin)",
        }

    # Determine data quality
    if not dss_missing and not ses_missing:
        data_quality = "high"
    elif not dss_missing or not ses_missing:
        data_quality = "medium"
    else:
        data_quality = "low"

    result["data_quality"] = data_quality
    result["dss_score"] = dss_score if not dss_missing else None
    result["ses_score"] = ses_score if not ses_missing else None
    return result


def classify_all(
    dss_df: pd.DataFrame,
    ses_df: pd.DataFrame,
    output_dir: Path,
) -> pd.DataFrame:
    """Classify termination type for all scored wars."""
    if "war_id" not in dss_df.columns and "war_id" not in ses_df.columns:
        logger.warning("No war_id in either DSS or SES data")
        return pd.DataFrame()

    if "war_id" not in dss_df.columns:
        merged = ses_df.copy()
        merged["dss_score"] = None
    elif "war_id" not in ses_df.columns:
        merged = dss_df.copy()
        merged["ses_score"] = None
    else:
        merged = dss_df.merge(ses_df, on="war_id", how="outer", suffixes=("_dss", "_ses"))

    classifications = []
    for _, row in merged.iterrows():
        dss_val = row.get("dss_score")
        ses_val = row.get("ses_score")
        result = classify_termination(
            dss_score=dss_val,
            ses_score=ses_val,
        )
        classifications.append(
            {
                "war_id": row["war_id"],
                "dss_score": dss_val if not (dss_val is None or (isinstance(dss_val, float) and pd.isna(dss_val))) else None,
                "ses_score": ses_val if not (ses_val is None or (isinstance(ses_val, float) and pd.isna(ses_val))) else None,
                **result,
            }
        )

    result_df = pd.DataFrame(classifications)
    output_dir.mkdir(parents=True, exist_ok=True)
    result_df.to_parquet(output_dir / "termination_classification.parquet", index=False)

    counts = result_df["termination_type_model"].value_counts()
    logger.info(f"Termination classifications:\n{counts.to_string()}")
    return result_df
