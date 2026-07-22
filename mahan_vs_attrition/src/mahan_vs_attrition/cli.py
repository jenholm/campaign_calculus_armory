"""CLI for Mahan vs Attrition analysis pipeline."""

import logging
from pathlib import Path

import typer
from rich.console import Console
from rich.logging import RichHandler

from mahan_vs_attrition import __version__

app = typer.Typer(help="Mahan vs Attrition: Decisive Battle or Strategic Exhaustion?")
console = Console()
RAW_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")


def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)],
    )


@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging"),
):
    setup_logging(verbose)


@app.command()
def version():
    """Show version information."""
    console.print(f"Mahan vs Attrition v{__version__}")


@app.command()
def fetch(source: str = typer.Argument("all", help="Source to fetch")):
    """Fetch raw data from a source."""
    from mahan_vs_attrition.ingest import aow, brecke, cow_nmc, cow_war, iwb, sipri, ucdp, vdem

    sources = {
        "cow_nmc": (
            "COW National Material Capabilities",
            lambda: cow_nmc.run(RAW_DIR / "cow_nmc", OUTPUT_DIR),
        ),
        "cow_war": (
            "COW War Data",
            lambda: cow_war.run(RAW_DIR / "cow_war", OUTPUT_DIR),
        ),
        "ucdp": (
            "UCDP Battle-Related Deaths",
            lambda: ucdp.run(RAW_DIR / "ucdp", OUTPUT_DIR),
        ),
        "sipri": (
            "SIPRI Military Expenditure",
            lambda: sipri.run(RAW_DIR / "sipri", OUTPUT_DIR),
        ),
        "brecke": (
            "Brecke Conflict Catalog",
            lambda: brecke.run(RAW_DIR / "brecke", OUTPUT_DIR),
        ),
        "iwb": (
            "Interstate War Battle Dataset",
            lambda: iwb.run(RAW_DIR / "iwb", OUTPUT_DIR),
        ),
        "vdem": (
            "V-Dem Dataset",
            lambda: vdem.run(RAW_DIR / "vdem", OUTPUT_DIR),
        ),
        "aow": (
            "Autocracies of the World",
            lambda: aow.run(RAW_DIR / "iwb", OUTPUT_DIR),
        ),
    }

    if source == "all":
        for name, (label, func) in sources.items():
            console.print(f"[yellow]Fetching {label}...[/yellow]")
            try:
                func()
                console.print(f"[green]  OK {label}[/green]")
            except Exception as e:
                console.print(f"[red]  FAIL {label}: {e}[/red]")
    elif source in sources:
        label, func = sources[source]
        console.print(f"[yellow]Fetching {label}...[/yellow]")
        try:
            func()
            console.print(f"[green]  OK {label}[/green]")
        except Exception as e:
            console.print(f"[red]  FAIL {label}: {e}[/red]")
    else:
        opts = ", ".join(sources.keys())
        console.print(f"[red]Unknown source: {source}. Options: all, {opts}[/red]")


@app.command()
def normalize(source: str = typer.Argument("all", help="Source to normalize")):
    """Normalize raw data into standardized tables."""
    from mahan_vs_attrition.normalize.pipeline import run as normalize_run

    console.print(f"[yellow]Normalizing {source}...[/yellow]")
    try:
        result = normalize_run(
            cow_war_path=OUTPUT_DIR / "cow_war.parquet",
            cow_nmc_path=OUTPUT_DIR / "cow_nmc.parquet",
            ucdp_path=OUTPUT_DIR / "ucdp_battle_deaths.parquet",
            brecke_path=OUTPUT_DIR / "brecke_conflicts.parquet",
            iwb_path=OUTPUT_DIR / "iwb_battles.parquet",
            output_dir=OUTPUT_DIR,
        )
        for k, v in result.items():
            console.print(f"  {k}: {v}")
        console.print("[green]Normalization complete[/green]")
    except Exception as e:
        console.print(f"[red]Normalization failed: {e}[/red]")


@app.command()
def build(table: str = typer.Argument("all", help="Table to build")):
    """Build derived tables (same as normalize for now)."""
    normalize(source=table)


@app.command()
def score(target: str = typer.Argument("all", help="Score target")):
    """Compute metrics and scores."""
    import pandas as pd

    from mahan_vs_attrition.metrics.classify import classify_all
    from mahan_vs_attrition.metrics.dss import score_wars as score_dss
    from mahan_vs_attrition.metrics.ses import score_wars as score_ses

    console.print(f"[yellow]Computing scores: {target}...[/yellow]")

    wars_path = OUTPUT_DIR / "wars.parquet"
    war_years_path = OUTPUT_DIR / "war_years.parquet"
    battles_path = OUTPUT_DIR / "iwb_battles.parquet"

    if target in ("all", "dss"):
        if battles_path.exists() and battles_path.stat().st_size > 1000 and wars_path.exists():
            try:
                cow_war_path = OUTPUT_DIR / "cow_war.parquet"
                cow_war_df = (
                    pd.read_parquet(cow_war_path) if cow_war_path.exists() else None
                )
                score_dss(
                    pd.read_parquet(battles_path),
                    pd.read_parquet(wars_path),
                    OUTPUT_DIR,
                    cow_war_df=cow_war_df,
                )
                console.print("[green]  OK DSS scores[/green]")
            except Exception as e:
                console.print(f"[yellow]  DSS failed: {e}[/yellow]")
        else:
            console.print("[yellow]  Skipping DSS (no battle data)[/yellow]")

    if target in ("all", "ses"):
        if war_years_path.exists():
            wars_df = pd.read_parquet(wars_path) if wars_path.exists() else None
            score_ses(pd.read_parquet(war_years_path), OUTPUT_DIR, wars_df=wars_df)
            console.print("[green]  OK SES scores[/green]")
        else:
            console.print("[yellow]  Skipping SES (no war-years data)[/yellow]")

    if target in ("all", "classify"):
        dss_path = OUTPUT_DIR / "dss_scores.parquet"
        ses_path = OUTPUT_DIR / "ses_scores.parquet"
        if dss_path.exists() or ses_path.exists():
            dss_df = pd.read_parquet(dss_path) if dss_path.exists() else pd.DataFrame()
            ses_df = pd.read_parquet(ses_path) if ses_path.exists() else pd.DataFrame()
            classify_all(dss_df, ses_df, OUTPUT_DIR)
            console.print("[green]  OK Classifications[/green]")
        else:
            console.print("[yellow]  Skipping classification (no scores)[/yellow]")


@app.command()
def analyze(target: str = typer.Argument("all", help="Analysis target")):
    """Run statistical analysis."""
    from mahan_vs_attrition.models.analysis import run_all

    console.print(f"[yellow]Analyzing {target}...[/yellow]")
    try:
        if target == "survival":
            import json
            import pandas as pd
            from mahan_vs_attrition.models.analysis import survival_analysis
            wars = pd.read_parquet(OUTPUT_DIR / "wars.parquet") if (OUTPUT_DIR / "wars.parquet").exists() else pd.DataFrame()
            classifications = pd.read_parquet(OUTPUT_DIR / "termination_classification.parquet") if (OUTPUT_DIR / "termination_classification.parquet").exists() else pd.DataFrame()
            result = survival_analysis(wars, classifications, OUTPUT_DIR)
            for k, v in result.items():
                if isinstance(v, dict) and "n_wars" in v:
                    console.print(f"  {k}: {v['n_wars']} wars, median {v['median_duration_days']}d")
            console.print("[green]Survival analysis complete[/green]")
            return
        results = run_all(
            wars_path=OUTPUT_DIR / "wars.parquet",
            war_years_path=OUTPUT_DIR / "war_years.parquet",
            classifications_path=OUTPUT_DIR / "termination_classification.parquet",
            output_dir=OUTPUT_DIR,
        )
        for section, data in results.items():
            if data:
                label = f"{len(data)} items" if isinstance(data, dict) else "done"
                console.print(f"  {section}: {label}")
        console.print("[green]Analysis complete[/green]")
    except Exception as e:
        console.print(f"[red]Analysis failed: {e}[/red]")


@app.command()
def report():
    """Generate the final report."""
    import pandas as pd

    from mahan_vs_attrition.viz.plots import generate_all_figures

    console.print("[yellow]Generating report...[/yellow]")

    try:

        def _read(name):
            path = OUTPUT_DIR / name
            return pd.read_parquet(path) if path.exists() else pd.DataFrame()

        wars = _read("wars.parquet")
        classifications = _read("termination_classification.parquet")
        dss = _read("dss_scores.parquet")
        ses = _read("ses_scores.parquet")
        war_years = _read("war_years.parquet")
        battles = _read("battles.parquet") if (OUTPUT_DIR / "battles.parquet").exists() else _read("iwb_battles.parquet")

        scored = pd.DataFrame()
        if len(dss) > 0 and len(ses) > 0:
            scored = dss.merge(ses, on="war_id", how="outer", suffixes=("_dss", "_ses"))

        # Load case studies if available
        case_studies = pd.DataFrame()
        cs_path = Path("data/manual/manual_case_scores.csv")
        if cs_path.exists():
            case_studies = pd.read_csv(cs_path)

        model_results_path = OUTPUT_DIR / "loss_prediction_model.json"
        model_results = {}
        if model_results_path.exists():
            import json

            model_results = json.loads(model_results_path.read_text())

        paths = generate_all_figures(
            wars, classifications, scored, war_years, model_results,
            battles_df=battles, case_studies_df=case_studies,
        )
        for p in paths:
            console.print(f"  [green]OK[/green] {p}")

        # Generate text report
        report_lines = []
        report_lines.append("# Mahan vs Attrition: Research Report")
        report_lines.append(f"*Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}*\n")
        report_lines.append(f"**Total wars in dataset:** {len(wars)}")
        if "era" in wars.columns:
            era_counts = wars["era"].value_counts().to_dict()
            report_lines.append(f"**Eras covered:** {', '.join(f'{k} ({v})' for k, v in era_counts.items())}")
        if len(classifications) > 0:
            cc = classifications["termination_type_model"].value_counts().to_dict()
            report_lines.append(f"**Termination types:** {cc}")
        if len(dss) > 0:
            report_lines.append(f"**DSS scored:** {len(dss)} wars")
        if len(ses) > 0:
            report_lines.append(f"**SES scored:** {len(ses)} wars")
        report_lines.append(f"**Battle records:** {len(battles) if len(battles) > 0 else 0}")
        if model_results:
            report_lines.append(f"**Loss prediction model:** trained on {model_results.get('random_forest', {}).get('n_wars', 'N/A')} wars")
        report_lines.append(f"\n## Figures generated")
        for p in paths:
            report_lines.append(f"- {p.name}")

        # Case studies
        case_dir = Path("data/manual")
        case_files = list(case_dir.glob("case_study_*.md"))
        if case_files:
            report_lines.append(f"\n## Manual case studies ({len(case_files)})")
            for cf in sorted(case_files):
                report_lines.append(f"- {cf.stem.replace('case_study_', '')}")

        report_text = "\n".join(report_lines)
        report_path = Path("reports/mahan_vs_attrition_report.md")
        report_path.write_text(report_text)
        console.print(f"  [green]OK[/green] {report_path}")
        console.print("[green]Report generated[/green]")
    except Exception as e:
        console.print(f"[red]Report generation failed: {e}[/red]")


@app.command()
def report_html():
    """Build a comprehensive HTML report."""
    from mahan_vs_attrition.viz.report import build_html_report

    console.print("[yellow]Building HTML report...[/yellow]")
    try:
        path = build_html_report(OUTPUT_DIR, Path("reports/mahan_vs_attrition_report.html"))
        console.print(f"  [green]OK[/green] {path}")
        console.print(f"  Size: {path.stat().st_size / 1024:.1f} KB")
        console.print("[green]HTML report complete[/green]")
    except Exception as e:
        console.print(f"[red]HTML report failed: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())


@app.command()
def wikipedia(
    max_wars: int = typer.Option(0, "--max", "-m", help="Max wars to enrich (0=all)"),
):
    """Enrich wars/battles from Wikipedia infobox data."""
    from mahan_vs_attrition.ingest.wikipedia_enrich import run_enrichment

    progress_dir = Path("data/interim/wikipedia_progress")
    console.print("[yellow]Running Wikipedia enrichment...[/yellow]")
    console.print("[yellow]Rate-limited: ~1.8-3.5s between requests[/yellow]")
    try:
        result = run_enrichment(OUTPUT_DIR, progress_dir, max_wars=max_wars)
        for k, v in result.items():
            console.print(f"  {k}: {v}")
        console.print("[green]Wikipedia enrichment complete[/green]")
    except Exception as e:
        console.print(f"[red]Wikipedia enrichment failed: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())


@app.command()
def validate():
    """Validate manual case studies against model output."""
    from mahan_vs_attrition.case_studies.validation import (
        validate_case_studies, case_study_validation_report_text
    )

    console.print("[yellow]Validating case studies...[/yellow]")
    try:
        result = validate_case_studies(
            case_studies_path=Path("data/manual/manual_case_scores.csv"),
            dss_path=OUTPUT_DIR / "dss_scores.parquet",
            ses_path=OUTPUT_DIR / "ses_scores.parquet",
            output_path=OUTPUT_DIR / "case_study_validation.json",
        )
        summary = result["summary"]
        console.print(f"  Case studies: {summary['n_case_studies']}")
        console.print(f"  Agreement: {summary['n_classification_agreement']}/{summary['n_evaluated_against_model']} ({summary['agreement_pct']}%)")
        if summary["mean_dss_delta"] is not None:
            console.print(f"  Mean DSS delta: {summary['mean_dss_delta']:+.1f}")
        if summary["mean_ses_delta"] is not None:
            console.print(f"  Mean SES delta: {summary['mean_ses_delta']:+.1f}")
        # Write markdown report
        report = case_study_validation_report_text(result)
        report_path = Path("reports/case_study_validation.md")
        report_path.write_text(report)
        console.print(f"  [green]OK[/green] {report_path}")
        console.print("[green]Case study validation complete[/green]")
    except Exception as e:
        console.print(f"[red]Validation failed: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())


@app.command()
def hypothesis():
    """Run hypothesis testing (Mahan vs Attrition)."""
    import pandas as pd

    from mahan_vs_attrition.models.hypothesis_testing import (
        ablation_study,
        logistic_regression_hypothesis,
        survival_analysis_hypothesis,
        validate_simulation_against_history,
    )

    wars_path = OUTPUT_DIR / "wars.parquet"
    war_years_path = OUTPUT_DIR / "war_years.parquet"
    classifications_path = OUTPUT_DIR / "termination_classification.parquet"

    def _read(path: Path):
        return pd.read_parquet(path) if path.exists() else pd.DataFrame()

    wars = _read(wars_path)
    war_years = _read(war_years_path)
    classifications = _read(classifications_path)

    if len(war_years) > 0 and len(classifications) > 0:
        console.print("[yellow]Running logistic regression hypothesis test...[/yellow]")
        try:
            lr_result = logistic_regression_hypothesis(
                war_years, classifications, OUTPUT_DIR, wars_df=wars,
            )
            if "error" not in lr_result:
                console.print(f"  Accuracy: {lr_result.get('mean_accuracy', 'N/A')} ± {lr_result.get('std_accuracy', 'N/A')}")
                if "h1_correlation" in lr_result:
                    r = lr_result["h1_correlation"]
                    console.print(f"  H1 (Mahan): r={r['r']}, p={r['p_value']}")
                if "h2_correlation" in lr_result:
                    r = lr_result["h2_correlation"]
                    console.print(f"  H2 (Attrition): r={r['r']}, p={r['p_value']}")
            else:
                console.print(f"  [yellow]Skipped: {lr_result['error']}[/yellow]")
        except Exception as e:
            console.print(f"  [red]Failed: {e}[/red]")

        console.print("[yellow]Running ablation study...[/yellow]")
        try:
            ablation_result = ablation_study(
                war_years, classifications, OUTPUT_DIR, wars_df=wars,
            )
            if "error" not in ablation_result:
                console.print(f"  Full accuracy: {ablation_result.get('full', {}).get('accuracy', 'N/A')}")
                console.print(f"  DSS loss: {ablation_result.get('dss_loss', 'N/A')}")
                console.print(f"  SES loss: {ablation_result.get('ses_loss', 'N/A')}")
                interp = ablation_result.get("interpretation", {})
                if interp.get("dss_more_predictive"):
                    console.print("  [green]→ DSS features more predictive (Mahan supported)[/green]")
                elif interp.get("ses_more_predictive"):
                    console.print("  [green]→ SES features more predictive (Attrition supported)[/green]")
                elif interp.get("both_contribute"):
                    console.print("  [green]→ Both DSS and SES contribute (Mixed model supported)[/green]")
            else:
                console.print(f"  [yellow]Skipped: {ablation_result['error']}[/yellow]")
        except Exception as e:
            console.print(f"  [red]Failed: {e}[/red]")

    if len(wars) > 0 and len(classifications) > 0:
        console.print("[yellow]Running survival hypothesis test...[/yellow]")
        try:
            surv_result = survival_analysis_hypothesis(
                wars, classifications, OUTPUT_DIR,
            )
            if "error" not in surv_result:
                for k, v in surv_result.items():
                    if isinstance(v, dict) and "n_wars" in v:
                        console.print(f"  {k}: {v['n_wars']} wars, median {v['median_duration_months']}mo")
            else:
                console.print(f"  [yellow]Skipped: {surv_result['error']}[/yellow]")
        except Exception as e:
            console.print(f"  [red]Failed: {e}[/red]")

    console.print("[yellow]Validating simulation against history...[/yellow]")
    try:
        sim_result = validate_simulation_against_history(output_dir=OUTPUT_DIR)
        summary = sim_result.get("summary", {})
        console.print(f"  Passed: {summary.get('passed', 0)}/{summary.get('total_validated', 0)}")
        for name in [k for k in sim_result if k != "summary"]:
            v = sim_result[name]
            status = "[green]PASS[/green]" if v.get("passes") else "[red]FAIL[/red]"
            console.print(f"  {status} {name} ({v.get('expected_pattern', '?')})")
    except Exception as e:
        console.print(f"  [red]Failed: {e}[/red]")

    console.print("[green]Hypothesis testing complete[/green]")


@app.command()
def missingness():
    """Generate missingness report for all processed tables."""
    from mahan_vs_attrition.normalize.pipeline import generate_missingness_report

    console.print("[yellow]Generating missingness report...[/yellow]")
    try:
        report = generate_missingness_report(OUTPUT_DIR)
        for table, info in report.items():
            if isinstance(info, int):
                continue
            status = "[green]OK[/green]" if info["status"] == "present" else "[red]MISSING[/red]"
            console.print(f"  {status} {table}: {info['rows']} rows, {info.get('columns', 0)} cols")
            if info.get("missing_pct"):
                for col, pct in list(info["missing_pct"].items())[:5]:
                    console.print(f"      {col}: {pct}% missing")
        console.print(f"[green]Missingness report: {report['total_tables_checked']} tables checked[/green]")
    except Exception as e:
        console.print(f"[red]Failed: {e}[/red]")


@app.command()
def dashboard():
    """Launch the interactive dashboard."""
    console.print("[yellow]Launching dashboard (placeholder)...[/yellow]")
    console.print("Run: streamlit run src/mahan_vs_attrition/viz/app.py")


if __name__ == "__main__":
    app()
