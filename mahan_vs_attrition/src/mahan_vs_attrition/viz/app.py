"""Streamlit dashboard for Mahan vs Attrition project.

Run with:
    streamlit run src/mahan_vs_attrition/viz/app.py
"""

import json
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Mahan vs Attrition",
    page_icon=":military_helmet:",
    layout="wide",
)

DATA_DIR = Path("data/processed")
FIGS_DIR = Path("reports/figures")
REPORTS_DIR = Path("reports")
CASE_DIR = Path("data/manual")


@st.cache_data
def load_table(name: str) -> pd.DataFrame:
    p = DATA_DIR / name
    if p.exists():
        return pd.read_parquet(p)
    return pd.DataFrame()


@st.cache_data
def load_json(name: str) -> dict:
    p = DATA_DIR / name
    if p.exists():
        return json.loads(p.read_text())
    return {}


def main():
    st.title("Mahan vs Attrition: Decisive Battle or Strategic Exhaustion?")

    st.sidebar.header("Navigation")
    page = st.sidebar.radio(
        "Page",
        ["Overview", "War Browser", "Decisive Shock Rankings", "Strategic Exhaustion Rankings",
         "Case Studies", "Validation", "Source Confidence"],
    )

    # Load data
    wars = load_table("wars.parquet")
    dss = load_table("dss_scores.parquet")
    ses = load_table("ses_scores.parquet")
    classifications = load_table("termination_classification.parquet")
    battles = load_table("battles.parquet")
    te = load_table("termination_events.parquet")
    case_studies = pd.DataFrame()
    cs_path = CASE_DIR / "manual_case_scores.csv"
    if cs_path.exists():
        case_studies = pd.read_csv(cs_path)

    if page == "Overview":
        show_overview(wars, dss, ses, classifications, battles, te, case_studies)
    elif page == "War Browser":
        show_war_browser(wars, dss, ses, classifications, battles, te)
    elif page == "Decisive Shock Rankings":
        show_dss_rankings(dss, ses, wars)
    elif page == "Strategic Exhaustion Rankings":
        show_ses_rankings(dss, ses, wars)
    elif page == "Case Studies":
        show_case_studies(case_studies, dss, ses)
    elif page == "Validation":
        show_validation()
    elif page == "Source Confidence":
        show_source_confidence(wars)


def show_overview(wars, dss, ses, classifications, battles, te, case_studies):
    st.header("Project Overview")
    st.markdown(
        """
        This dashboard explores whether wars are more often decided by **decisive battle/campaign
        shocks** (Mahan) or by **cumulative strategic exhaustion** (logistics, manpower, economic
        degradation, will collapse).
        """
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Wars in dataset", f"{len(wars):,}")
    with col2:
        st.metric("Interstate wars with DSS", f"{len(dss):,}")
    with col3:
        st.metric("Wars with SES", f"{len(ses):,}")
    with col4:
        st.metric("Manual case studies", f"{len(case_studies):,}")

    st.subheader("Duration distribution by era")
    fig1_path = FIGS_DIR / "fig_01_war_duration_by_era.png"
    if fig1_path.exists():
        st.image(str(fig1_path), use_container_width=True)

    st.subheader("DSS vs SES scatter")
    fig3_path = FIGS_DIR / "fig_03_dss_vs_ses_scatter.png"
    if fig3_path.exists():
        st.image(str(fig3_path), use_container_width=True)


def show_war_browser(wars, dss, ses, classifications, battles, te):
    st.header("War Browser")
    st.markdown("Filter and explore individual wars.")

    col1, col2, col3 = st.columns(3)
    with col1:
        era_options = sorted([e for e in wars["era"].unique() if pd.notna(e)])
        era = st.selectbox("Era", ["All"] + era_options)
    with col2:
        region_options = sorted([r for r in wars["region"].unique() if pd.notna(r)])
        region = st.selectbox("Region", ["All"] + region_options)
    with col3:
        war_types = sorted([t for t in wars["war_type"].unique() if pd.notna(t)])
        war_type = st.selectbox("War type", ["All"] + war_types)

    filtered = wars.copy()
    if era != "All":
        filtered = filtered[filtered["era"] == era]
    if region != "All":
        filtered = filtered[filtered["region"] == region]
    if war_type != "All":
        filtered = filtered[filtered["war_type"] == war_type]

    st.write(f"Showing {len(filtered):,} wars")

    # Merge with DSS/SES
    if len(dss) > 0:
        filtered = filtered.merge(
            dss[["war_id", "dss_score"]], on="war_id", how="left"
        )
    if len(ses) > 0:
        filtered = filtered.merge(
            ses[["war_id", "ses_score"]], on="war_id", how="left"
        )

    display_cols = ["war_id", "war_name", "era", "region", "war_type", "start_date",
                    "end_date", "duration_days", "outcome_type", "dss_score", "ses_score"]
    display_cols = [c for c in display_cols if c in filtered.columns]

    st.dataframe(
        filtered[display_cols].head(200),
        use_container_width=True,
        height=600,
    )

    # Click to drill down
    selected_wid = st.text_input("Enter war_id for details:")
    if selected_wid:
        war_row = wars[wars["war_id"] == selected_wid]
        if len(war_row) > 0:
            st.subheader(f"Details for {selected_wid}")
            st.json(war_row.iloc[0].to_dict())


def show_dss_rankings(dss, ses, wars):
    st.header("Decisive Shock Score Rankings")
    st.markdown("Wars with highest Decisive Shock Score (DSS) — most battle-driven terminations.")

    if len(dss) == 0:
        st.warning("No DSS data available.")
        return

    scored = dss.merge(ses[["war_id", "ses_score"]], on="war_id", how="left")
    scored = scored.merge(wars[["war_id", "era", "region"]], on="war_id", how="left")
    scored = scored.sort_values("dss_score", ascending=False).head(50)

    st.dataframe(
        scored[["war_id", "war_name", "era", "region", "dss_score", "ses_score"]],
        use_container_width=True,
        height=600,
    )

    fig5_path = FIGS_DIR / "fig_05_decisive_battle_timing.png"
    if fig5_path.exists():
        st.subheader("Battle timing distribution")
        st.image(str(fig5_path), use_container_width=True)


def show_ses_rankings(dss, ses, wars):
    st.header("Strategic Exhaustion Score Rankings")
    st.markdown("Wars with highest Strategic Exhaustion Score (SES) — most exhaustion-driven terminations.")

    if len(ses) == 0:
        st.warning("No SES data available.")
        return

    scored = ses.merge(dss[["war_id", "dss_score"]], on="war_id", how="left")
    scored = scored.merge(wars[["war_id", "era", "region", "war_name"]], on="war_id", how="left")
    scored = scored.sort_values("ses_score", ascending=False).head(50)

    st.dataframe(
        scored[["war_id", "war_name", "era", "region", "ses_score", "dss_score"]],
        use_container_width=True,
        height=600,
    )

    fig4_path = FIGS_DIR / "fig_04_attrition_trajectories_selected_wars.png"
    if fig4_path.exists():
        st.subheader("Capability trajectories")
        st.image(str(fig4_path), use_container_width=True)


def show_case_studies(case_studies, dss, ses):
    st.header("Manual Case Studies")
    st.markdown(
        """
        These wars have manual historical classifications by the researcher. They serve as
        ground truth for evaluating the model's performance.
        """
    )

    if len(case_studies) == 0:
        st.warning("No case studies found.")
        return

    fig7_path = FIGS_DIR / "fig_07_case_study_scorecards.png"
    if fig7_path.exists():
        st.image(str(fig7_path), use_container_width=True)

    # Map case studies to model war_ids for comparison
    NAME_TO_WAR_ID = {
        "Franco-Prussian War": "cow_iw_58",
        "Russo-Japanese War": "cow_iw_85",
        "Gulf War 1991": "cow_iw_211",
        "World War I": "cow_iw_106",
        "World War II Pacific": "cow_iw_139",
        "Vietnam War": "cow_iw_163",
    }

    rows = []
    for _, c in case_studies.iterrows():
        wid = str(c.get("war_id", ""))
        if not wid or wid.startswith("manual_"):
            wid = NAME_TO_WAR_ID.get(c["war_name"], "")
        d = dss[dss["war_id"] == wid] if wid else pd.DataFrame()
        s = ses[ses["war_id"] == wid] if wid else pd.DataFrame()
        model_dss = float(d.iloc[0]["dss_score"]) if len(d) > 0 else None
        model_ses = float(s.iloc[0]["ses_score"]) if len(s) > 0 else None
        dss_val = c.get("manual_dss", c.get("dss", 0))
        ses_val = c.get("manual_ses", c.get("ses", 0))
        rows.append({
            "War": c["war_name"],
            "Confidence": c.get("confidence", ""),
            "Manual DSS": dss_val,
            "Manual SES": ses_val,
            "Manual mechanism": c["dominant_mechanism"],
            "Model DSS": model_dss,
            "Model SES": model_ses,
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

    # Show full text of each case study
    st.subheader("Case study memos")
    md_files = sorted(CASE_DIR.glob("case_study_*.md"))
    for md in md_files:
        with st.expander(md.stem.replace("case_study_", "").replace("_", " ").title()):
            st.markdown(md.read_text())


def show_validation():
    st.header("Case Study Validation")
    st.markdown("Comparison of manual historical classifications against model output.")

    val_path = DATA_DIR / "case_study_validation.json"
    if not val_path.exists():
        st.warning("Run `python -m mahan_vs_attrition validate` to generate validation.")
        return

    data = json.loads(val_path.read_text())
    summary = data.get("summary", {})

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Case studies", summary.get("n_case_studies", 0))
    with col2:
        st.metric("Agreement %", f"{summary.get('agreement_pct', 0)}%")
    with col3:
        st.metric("Mean DSS delta", f"{summary.get('mean_dss_delta', 0):+.1f}" if summary.get("mean_dss_delta") is not None else "n/a")
    with col4:
        st.metric("Mean SES delta", f"{summary.get('mean_ses_delta', 0):+.1f}" if summary.get("mean_ses_delta") is not None else "n/a")

    st.subheader("Per-case detail")
    rows = data.get("cases", [])
    df = pd.DataFrame(rows)
    if len(df) > 0:
        st.dataframe(df, use_container_width=True)

    st.markdown("---")
    val_md = REPORTS_DIR / "case_study_validation.md"
    if val_md.exists():
        with st.expander("Markdown report"):
            st.markdown(val_md.read_text())


def show_source_confidence(wars):
    st.header("Source Confidence")
    st.markdown(
        """
        Confidence grades A-E:
        - **A**: Official structured dataset, day-level precision
        - **B**: Academic dataset or peer-reviewed source
        - **C**: Reputable encyclopedia/history source
        - **D**: Single non-academic web source
        - **E**: LLM-assisted unresolved extraction
        """
    )

    if "confidence" not in wars.columns:
        st.warning("No confidence column in wars table.")
        return

    counts = wars["confidence"].value_counts().reset_index()
    counts.columns = ["Grade", "Count"]
    st.dataframe(counts, use_container_width=True)

    st.bar_chart(counts.set_index("Grade"))


if __name__ == "__main__":
    main()
