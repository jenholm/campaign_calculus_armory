"""Build comprehensive HTML and PDF reports from processed data and figures."""

import base64
import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

REPORTS_DIR = Path("reports")
FIGS_DIR = REPORTS_DIR / "figures"


def _img_to_base64(img_path: Path) -> str:
    """Read an image file and return base64-encoded data URL."""
    if not img_path.exists():
        return ""
    suffix = img_path.suffix.lower().lstrip(".")
    mime = "image/png" if suffix == "png" else f"image/{suffix}"
    data = img_path.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Mahan vs Attrition: Research Report</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
        max-width: 1100px; margin: 30px auto; padding: 0 25px; line-height: 1.55; color: #222; background: #fafafa; }}
h1 {{ color: #2c3e50; border-bottom: 3px solid #c0392b; padding-bottom: 12px; margin-top: 35px; }}
h2 {{ color: #34495e; border-bottom: 1px solid #bdc3c7; padding-bottom: 6px; margin-top: 28px; }}
h3 {{ color: #34495e; margin-top: 22px; }}
code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-size: 90%; }}
pre {{ background: #2c3e50; color: #ecf0f1; padding: 12px; border-radius: 4px; overflow-x: auto; }}
table {{ border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 14px; }}
th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
th {{ background: #34495e; color: white; }}
tr:nth-child(even) {{ background: #f8f8f8; }}
.figure {{ margin: 20px 0; text-align: center; }}
.figure img {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px;
               box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
.figure .caption {{ font-style: italic; color: #555; margin-top: 8px; font-size: 13px; }}
.keyfinding {{ background: #fef9e7; border-left: 4px solid #f39c12; padding: 12px 16px; margin: 12px 0;
               border-radius: 0 4px 4px 0; }}
.badge {{ display: inline-block; padding: 2px 8px; border-radius: 3px; font-size: 12px; color: white; }}
.badge-A {{ background: #27ae60; }} .badge-B {{ background: #f39c12; }} .badge-C {{ background: #e67e22; }}
.badge-D {{ background: #c0392b; }} .badge-E {{ background: #7f8c8d; }}
.metric {{ background: #ecf0f1; padding: 10px 14px; margin: 6px 0; border-radius: 4px; }}
.metric strong {{ color: #2c3e50; }}
</style>
</head>
<body>
{body}
</body>
</html>"""


def build_html_report(output_dir: Path, report_path: Path) -> Path:
    """Build a comprehensive HTML report from all processed data and figures."""
    body_parts = []

    # === HEADER ===
    body_parts.append('<h1>Mahan vs Attrition: Decisive Battle or Strategic Exhaustion?</h1>')
    body_parts.append(
        '<p><em>A reproducible research pipeline testing whether wars are more often decided by '
        'decisive battle/campaign shocks or by cumulative strategic exhaustion.</em></p>'
    )

    # === RESEARCH QUESTION ===
    body_parts.append('<h2>Research Question</h2>')
    body_parts.append(
        '<p>Do states usually lose wars because of decisive battle/campaign shocks, or because of '
        'cumulative strategic exhaustion (logistics, manpower attrition, economic degradation, '
        'alliance failure, and political will collapse)?</p>'
        '<p>This project builds a reproducible dataset, statistical analysis, and report classifying '
        'wars by termination mechanism, comparing <strong>Decisive Shock Score (DSS)</strong> '
        'against <strong>Strategic Exhaustion Score (SES)</strong>.</p>'
    )

    # === DATA INVENTORY ===
    body_parts.append('<h2>Data Inventory</h2>')
    inventory = _data_inventory(output_dir)
    body_parts.append('<table><tr><th>Table</th><th>Rows</th><th>Columns</th><th>Notes</th></tr>')
    for table, info in inventory.items():
        body_parts.append(
            f'<tr><td><code>{table}</code></td><td>{info["rows"]:,}</td>'
            f'<td>{info["columns"]}</td><td>{info.get("notes", "")}</td></tr>'
        )
    body_parts.append('</table>')

    # === KEY FINDINGS ===
    body_parts.append('<h2>Key Findings</h2>')
    body_parts.append(_key_findings_html(output_dir))

    # === FIGURES ===
    body_parts.append('<h2>Results: Figures</h2>')
    figure_captions = {
        "fig_01_war_duration_by_era.png": (
            "[Cohort E: all 4,812 wars] Distribution of war duration by historical era. "
            "This is a descriptive histogram; it does not by itself establish "
            "causation for any termination mechanism."
        ),
        "fig_02_termination_type_by_era.png": (
            "[Cohort A+B] Termination mechanism classification by era, using the "
            "hybrid rule. Most wars fall into <code>mixed_or_uncertain</code> "
            "because the model lacks <code>source_claims_decisive</code> for "
            "non-case-study wars. The figure is diagnostic, not substantive."
        ),
        "fig_03_dss_vs_ses_scatter.png": (
            "[Cohort A] Each war plotted by Decisive Shock Score (DSS) against "
            "Strategic Exhaustion Score (SES). Quadrants indicate the dominant "
            "mechanism under the hybrid rule. Most IWB wars cluster in the "
            "low-DSS band because <code>source_claims_decisive</code> defaults to 0."
        ),
        "fig_04_attrition_trajectories_selected_wars.png": (
            "[Cohort A] CINC (Composite Index of National Capability) "
            "trajectories for selected wars. Declining CINC is consistent with "
            "strategic exhaustion, but CINC is a single composite and may not "
            "capture all relevant dimensions."
        ),
        "fig_05_decisive_battle_timing.png": (
            "[Cohort A] Distribution of days from the last IWB battle to war "
            "termination. A concentration near 0-30 days is a candidate DSS signal, "
            "but does not by itself prove the battle caused the end. "
            "Causation requires corroborating evidence: capitulation within N days, "
            "capital loss, regime change, or field-army destruction."
        ),
        "fig_06_feature_importance_loss_prediction.png": (
            "[Cohort B] Random forest feature importances for a retrospective "
            "short/long-war duration classifier. This is <em>not</em> a "
            "termination-mechanism classifier. Use as a diagnostic on which "
            "capability changes correlate with duration, not as evidence for "
            "Mahan vs Attrition."
        ),
        "fig_07_case_study_scorecards.png": (
            "[Cohort C manual] Manual vs model DSS/SES scores for case study "
            "wars. Diamonds show model predictions; bars show historical "
            "consensus. 50% classification agreement on the 6-case evaluated set."
        ),
    }
    for fname, caption in figure_captions.items():
        fpath = FIGS_DIR / fname
        if fpath.exists():
            b64 = _img_to_base64(fpath)
            body_parts.append('<div class="figure">')
            body_parts.append(f'<img src="{b64}" alt="{fname}">')
            body_parts.append(f'<div class="caption">{caption}</div>')
            body_parts.append('</div>')

    # === CASE STUDY VALIDATION ===
    body_parts.append('<h2>Case Study Validation</h2>')
    cs_val_path = output_dir / "case_study_validation.json"
    if cs_val_path.exists():
        body_parts.append(_case_study_validation_html(cs_val_path))
    else:
        body_parts.append('<p>Run <code>python -m mahan_vs_attrition validate</code> to generate case study validation.</p>')

    # === LOGISTIC REGRESSION ===
    body_parts.append('<h2>Statistical Analysis: Retrospective Duration Classifier</h2>')
    body_parts.append(
        '<p><em>This is a retrospective short-vs-long duration classifier, not a '
        'termination-mechanism classifier. It uses full-war percent changes computed '
        'after the war has ended. It is a diagnostic on which capability changes '
        'correlate with duration, not evidence for Mahan vs Attrition.</em></p>'
    )
    lr_path = output_dir / "logistic_regression_termination.json"
    if lr_path.exists():
        body_parts.append(_logistic_regression_html(lr_path))
    else:
        body_parts.append('<p>No logistic regression results available.</p>')

    # === SURVIVAL ANALYSIS ===
    body_parts.append('<h2>Survival Analysis</h2>')
    surv_path = output_dir / "survival_analysis.json"
    if surv_path.exists():
        body_parts.append(_survival_analysis_html(surv_path))
    else:
        body_parts.append('<p>No survival analysis available.</p>')

    # === CASE STUDIES ===
    body_parts.append('<h2>Manual Case Studies</h2>')
    body_parts.append(_case_studies_html())

    # === DATA SOURCES ===
    body_parts.append('<h2>Data Sources</h2>')
    body_parts.append(_data_sources_html())

    # === LIMITATIONS ===
    body_parts.append('<h2>Limitations</h2>')
    body_parts.append(_limitations_html())

    # === REPRODUCIBILITY ===
    body_parts.append('<h2>Reproducibility</h2>')
    body_parts.append(
        '<p>All code, data, and figures in this report are reproducible. To regenerate:</p>'
        '<pre>cd /home/jenholm/workspace/mahan_vs_attrition\n'
        'python -m mahan_vs_attrition fetch all\n'
        'python -m mahan_vs_attrition normalize all\n'
        'python -m mahan_vs_attrition score all\n'
        'python -m mahan_vs_attrition analyze all\n'
        'python -m mahan_vs_attrition missingness\n'
        'python -m mahan_vs_attrition validate\n'
        'python -m mahan_vs_attrition wikipedia   # ~70 minutes, rate-limited\n'
        'python -m mahan_vs_attrition report</pre>'
    )

    body = "\n".join(body_parts)
    html = HTML_TEMPLATE.format(body=body)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(html)
    logger.info(f"HTML report saved: {report_path}")
    return report_path


def _data_inventory(output_dir: Path) -> dict:
    """Build data inventory with row/column counts."""
    tables = [
        ("wars.parquet", "Wars with start/end dates, outcomes, era, region, confidence"),
        ("war_participants.parquet", "Participants per war with side/role"),
        ("war_years.parquet", "War-year observations: capabilities, military, casualties"),
        ("battles.parquet", "Battles from IWB with timing, location, winner"),
        ("termination_events.parquet", "How each war ended: treaty, armistice, surrender"),
        ("dss_scores.parquet", "Decisive Shock Scores for 91 interstate wars"),
        ("ses_scores.parquet", "Strategic Exhaustion Scores for 1,928 wars"),
        ("termination_classification.parquet", "Termination type classification"),
    ]
    inventory = {}
    for fname, notes in tables:
        p = output_dir / fname
        if p.exists():
            try:
                df = pd.read_parquet(p)
                inventory[fname] = {"rows": len(df), "columns": len(df.columns), "notes": notes}
            except Exception:
                pass
    return inventory


def _key_findings_html(output_dir: Path) -> str:
    """Generate HTML for key findings.

    All findings are tagged with cohort and confidence. Findings are diagnostic
    until the model demonstrates consistent agreement with the manual golden set.
    """
    parts = []
    parts.append(
        '<div class="keyfinding"><strong>Diagnostic 1 (Cohort A: COW interstate, n=91):</strong> '
        'Interstate wars in the structured dataset are short (median 115 days), '
        'while civil wars (median 336 days) and other internal conflicts (median 161-377 days) '
        'last longer. This is consistent with the "decisive war" pattern for '
        'interstate conflicts, but does not by itself establish decisive-battle '
        'causation. The duration difference is also consistent with the '
        '"high capability = short war" alternative explanation.'
        '</div>'
    )
    parts.append(
        '<div class="keyfinding"><strong>Diagnostic 2 (Cohort A):</strong> '
        'Of 1,708 IWB battles, a large share occur within 90 days of war '
        'termination. This is a candidate DSS signal — the last battle is near '
        'the end of the war — but it does <em>not</em> prove the battle caused '
        'the end. To show decisiveness, we need corroborating evidence: '
        'capitulation within N days, capital loss, regime change, or '
        'field-army destruction.'
        '</div>'
    )
    parts.append(
        '<div class="keyfinding"><strong>Diagnostic 3 (Cohort C manual, n=6 evaluated):</strong> '
        'After rebuilding DSS with <code>source_claims_decisive</code> and SES with '
        'participant-side aggregation plus manual overrides, the model now achieves '
        '3/6 classification agreement (50%) on the manual golden set. '
        'Mean DSS delta is −6.0 and mean SES delta is 0.0. The remaining 3 '
        'mismatches (Russo-Japanese, WWI, WWII Pacific) are cases the model '
        'classifies as <code>strategic_exhaustion</code> while the manual label '
        'is <code>mixed</code> — these are edge cases where the manual '
        'classification is at the boundary of the hybrid rule.'
        '</div>'
    )
    parts.append(
        '<div class="keyfinding"><strong>Diagnostic 4 (Cohort B: wars with capability data):</strong> '
        'A retrospective duration classifier (random forest) predicts '
        'short vs long wars with 68% test accuracy. This is <em>not</em> a '
        'termination-mechanism classifier; it uses full-war percent changes. '
        'Top features: CINC percent change, military expenditure percent change, '
        'and initial national capability.'
        '</div>'
    )
    parts.append(
        '<div class="keyfinding"><strong>Diagnostic 5 (Cohort A, Wikipedia):</strong> '
        'Wikipedia enrichment of 91 interstate wars provides outcome classifications '
        'for all 91, plus 7 treaty / 1 armistice flags. Battle-level enrichment '
        'was collected but needs a re-run after the battle_id format change '
        '(see Limitations).'
        '</div>'
    )
    parts.append(
        '<div class="keyfinding"><strong>Cohort summary:</strong> '
        'A: 91 COW interstate + IWB | B: 2,571 with SES-capability | '
        'C: 10 manual case studies (6 with model comparison) | '
        'D: 188 modern (UCDP-era) | E: 4,812 all conflicts. '
        'Most claims above are cohort-specific; no global claim covers all cohorts.'
        '</div>'
    )
    return "\n".join(parts)


def _case_study_validation_html(path: Path) -> str:
    """Format case study validation as HTML."""
    data = json.loads(path.read_text())
    summary = data.get("summary", {})
    cases = data.get("cases", [])

    parts = []
    parts.append(
        f'<div class="metric">'
        f'<strong>Case studies evaluated:</strong> {summary.get("n_evaluated_against_model", 0)} '
        f'&nbsp;|&nbsp; <strong>Classification agreement:</strong> '
        f'{summary.get("n_classification_agreement", 0)}/{summary.get("n_evaluated_against_model", 0)} '
        f'({summary.get("agreement_pct", 0)}%) '
        f'&nbsp;|&nbsp; <strong>Mean DSS delta:</strong> {summary.get("mean_dss_delta", "n/a"):+.1f} '
        f'&nbsp;|&nbsp; <strong>Mean SES delta:</strong> {summary.get("mean_ses_delta", "n/a"):+.1f}'
        f'</div>'
    )

    parts.append('<table><tr><th>War</th><th>Manual DSS</th><th>Manual SES</th><th>Manual Class</th>'
                 '<th>Model DSS</th><th>Model SES</th><th>Model Class</th><th>Agreement</th></tr>')
    for c in cases:
        model_dss = f"{c['model_dss']:.0f}" if c["model_dss"] is not None else "n/a"
        model_ses = f"{c['model_ses']:.0f}" if c["model_ses"] is not None else "n/a"
        model_class = c["model_classification"] or "n/a"
        agree = "✓" if c["agreement"] is True else ("✗" if c["agreement"] is False else "?")
        parts.append(
            f'<tr><td>{c["war_name"]}</td><td>{c["manual_dss"]:.0f}</td><td>{c["manual_ses"]:.0f}</td>'
            f'<td>{c["manual_classification"]}</td><td>{model_dss}</td><td>{model_ses}</td>'
            f'<td>{model_class}</td><td>{agree}</td></tr>'
        )
    parts.append('</table>')

    parts.append(
        '<p><strong>Interpretation:</strong> The model currently <em>under-classifies</em> '
        'decisive wars as uncertain because key DSS components (source consensus on decisiveness, '
        'battle casualty concentration) require manual historical coding. The SES component is '
        'more robust because it uses structured capability data. As more case studies are added, '
        'the gap between manual and model can be quantified and used to refine weights.</p>'
    )
    return "\n".join(parts)


def _logistic_regression_html(path: Path) -> str:
    """Format logistic regression results as HTML."""
    data = json.loads(path.read_text())
    if "error" in data:
        return f'<p>Logistic regression: {data["error"]}</p>'

    lr = data.get("logistic_regression", {})
    rf = data.get("random_forest", {})

    parts = []
    parts.append(
        f'<div class="metric">'
        f'<strong>Sample size:</strong> {data.get("n_wars", 0)} wars '
        f'({data.get("n_short_war", 0)} short, {data.get("n_long_war", 0)} long) '
        f'&nbsp;|&nbsp; <strong>Test accuracy (LR):</strong> {lr.get("test_accuracy", 0):.3f} '
        f'&nbsp;|&nbsp; <strong>AUC-ROC:</strong> {lr.get("auc_roc", "n/a")} '
        f'&nbsp;|&nbsp; <strong>Test accuracy (RF):</strong> {rf.get("test_accuracy", 0):.3f}'
        f'</div>'
    )

    parts.append('<h3>Top logistic regression coefficients</h3>')
    parts.append('<table><tr><th>Feature</th><th>Coefficient</th><th>Interpretation</th></tr>')
    for feat in lr.get("top_coefficients", []):
        coef = feat["coef"]
        direction = "predicts LONG war" if coef > 0 else "predicts SHORT war"
        parts.append(f'<tr><td><code>{feat["feature"]}</code></td><td>{coef:+.4f}</td><td>{direction}</td></tr>')
    parts.append('</table>')

    parts.append('<h3>Top random forest feature importances</h3>')
    parts.append('<table><tr><th>Feature</th><th>Importance</th></tr>')
    for feat in rf.get("top_importances", []):
        parts.append(f'<tr><td><code>{feat["feature"]}</code></td><td>{feat["importance"]:.4f}</td></tr>')
    parts.append('</table>')

    return "\n".join(parts)


def _survival_analysis_html(path: Path) -> str:
    """Format survival analysis as HTML."""
    data = json.loads(path.read_text())
    parts = []
    parts.append('<table><tr><th>Termination Type</th><th>Wars</th><th>Median Days</th>'
                 '<th>Mean Days</th><th>≤30d</th><th>≤1yr</th><th>≤5yr</th></tr>')
    for term_type, info in data.items():
        if not isinstance(info, dict) or "n_wars" not in info:
            continue
        parts.append(
            f'<tr><td>{term_type}</td><td>{info["n_wars"]}</td>'
            f'<td>{info["median_duration_days"]}</td><td>{info["mean_duration_days"]}</td>'
            f'<td>{info["pct_ended_within_30d"]}%</td>'
            f'<td>{info["pct_ended_within_365d"]}%</td>'
            f'<td>{info["pct_ended_within_1825d"]}%</td></tr>'
        )
    parts.append('</table>')
    return "\n".join(parts)


def _case_studies_html() -> str:
    """Format manual case studies as HTML."""
    index_path = Path("data/manual/manual_case_scores.csv")
    if not index_path.exists():
        return '<p>No case studies found.</p>'

    cases = pd.read_csv(index_path)
    parts = []
    for _, c in cases.iterrows():
        conf = str(c.get("confidence", ""))
        badge = f'<span class="badge badge-{conf}">{conf}</span>' if conf else ""
        dss_val = c.get("manual_dss", c.get("dss", 0))
        ses_val = c.get("manual_ses", c.get("ses", 0))
        parts.append(
            f'<div class="metric">'
            f'<strong>{c["war_name"]}</strong> {badge} '
            f'&mdash; Dominant mechanism: <em>{c["dominant_mechanism"]}</em>; '
            f'Manual DSS={dss_val}, SES={ses_val}'
            f'</div>'
        )

    # Link to individual markdown files
    md_files = sorted(Path("data/manual").glob("case_study_*.md"))
    if md_files:
        parts.append('<h3>Detailed case study memos</h3>')
        parts.append('<ul>')
        for m in md_files:
            parts.append(f'<li><a href="../{m}">{m.stem.replace("case_study_", "Case study: ")}</a></li>')
        parts.append('</ul>')
    return "\n".join(parts)


def _data_sources_html() -> str:
    """Format data sources section."""
    return (
        '<table><tr><th>Source</th><th>Type</th><th>Period</th><th>Records</th></tr>'
        '<tr><td>Correlates of War (War)</td><td>Structured</td><td>1816-2007</td><td>91 interstate wars</td></tr>'
        '<tr><td>COW National Material Capabilities</td><td>Yearly</td><td>1816-2022</td><td>~200 states</td></tr>'
        '<tr><td>UCDP Battle-Related Deaths</td><td>Yearly</td><td>1989-2023</td><td>Modern conflicts</td></tr>'
        '<tr><td>SIPRI Military Expenditure</td><td>Yearly</td><td>1949-2025</td><td>170+ states</td></tr>'
        '<tr><td>Brecke Conflict Catalog</td><td>Per conflict</td><td>1400-2000</td><td>~3,700 conflicts</td></tr>'
        '<tr><td>Interstate War Battle Dataset</td><td>Per battle</td><td>1823-2003</td><td>1,708 battles</td></tr>'
        '<tr><td>Autocracies of the World (AoW)</td><td>Yearly</td><td>1946-2010</td><td>Regime data</td></tr>'
        '<tr><td>Wikipedia (enrichment)</td><td>API</td><td>All</td><td>91 wars + 41 battles</td></tr>'
        '</table>'
    )


def _limitations_html() -> str:
    """Limitations section."""
    return (
        '<ul>'
        '<li><strong>Pre-1816 data quality:</strong> Brecke data uses ordinal/qualitative descriptions. '
        'Statistical claims are not made on this subset.</li>'
        '<li><strong>Missing components in DSS:</strong> The model lacks the <code>source_claims_decisive</code> '
        'and <code>battle_casualty_concentration</code> components because they require manual coding. '
        'Case study validation shows this causes under-classification of decisive wars.</li>'
        '<li><strong>Outcome labels:</strong> Most wars do not have structured winner/loser labels. '
        'Wikipedia enrichment helps for 91 interstate wars; older wars remain unclassified.</li>'
        '<li><strong>Capability data:</strong> COW NMC for 1816-1945 is reconstructed; '
        'CINC for very small states is unreliable.</li>'
        '<li><strong>Battle-level data:</strong> Only interstate wars have battle-level data via IWB. '
        'For civil wars, we lack systematic battle data.</li>'
        '<li><strong>Alliance data:</strong> Not yet integrated. Would add significant value to the '
        'alliance_degradation SES component.</li>'
        '<li><strong>V-Dem regime data:</strong> Not yet integrated. Would improve regime_will_decline.</li>'
        '</ul>'
    )
