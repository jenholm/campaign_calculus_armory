from pathlib import Path


def all_tex() -> str:
    return "\n".join(p.read_text() for p in Path("paper/sections").rglob("*.tex"))


def test_no_internal_ids_in_paper_sections():
    text = all_tex()
    assert "cow\\_iw" not in text
    assert "cow_iw" not in text


def test_no_confusion_matrix_caption_for_blind_eval():
    text = all_tex().lower()
    assert "blind validation results: confusion matrix" not in text


def test_no_placeholder_case_inventory_rows():
    text = all_tex()
    assert "24 historical cases & Various" not in text
    assert "30 wars & Antiquity" not in text


def test_blind_evaluation_not_in_main_paper():
    main_text = "\n".join(
        p.read_text()
        for p in Path("paper/sections").rglob("*.tex")
        if "appendix" not in p.name and "supplementary" not in p.name
    )
    forbidden = [
        r"\label{fig:blind_val}",
        "fig_04_blind_validation.png",
        "Blind Evaluation Results",
        "Blind evaluation case inventory",
        "other_mismatch",
        "false_decisive",
    ]
    for item in forbidden:
        assert item not in main_text


def test_no_raw_cow_ids_in_figure_generators():
    paths = [
        Path("src/mahan_vs_attrition/viz/plots.py"),
        Path("scripts/generate_paper_figures.py"),
    ]
    text = "\n".join(p.read_text() for p in paths)
    assert "label=str(war_id)" not in text


def test_no_diamond_model_markers_in_case_scorecard():
    text = Path("src/mahan_vs_attrition/viz/plots.py").read_text()
    assert 'marker="D"' not in text
    assert "Model DSS" not in text
    assert "Model SES" not in text


def test_paper_generator_does_not_copy_stale_figures():
    text = Path("scripts/generate_paper_figures.py").read_text()
    assert "fig_04_attrition_trajectories_selected_wars.png" not in text
    assert '("fig_07_case_study_scorecards.png", "fig_07_case_study_scorecards.png")' not in text


def test_case_scorecard_has_no_model_diamond_overlay():
    texts = []
    for path in [
        Path("scripts/generate_paper_figures.py"),
        Path("src/mahan_vs_attrition/viz/plots.py"),
    ]:
        if path.exists():
            texts.append(path.read_text())

    text = "\n".join(texts)
    assert 'marker="D"' not in text
    assert "Model DSS" not in text
    assert "Model SES" not in text
    assert "Manual vs Model Classifications" not in text


def test_figure_6_known_cow_ids_have_display_names():
    from mahan_vs_attrition.display_names import display_war_name_strict

    for war_id in ["cow_iw_1", "cow_iw_4", "cow_iw_7", "cow_iw_10", "cow_iw_13"]:
        name = display_war_name_strict(war_id)
        assert "cow_iw" not in name.lower()
        assert "COW war" not in name


def test_generated_inventory_tables_use_forced_layout():
    text = Path("scripts/generate_case_inventory_tables.py").read_text()
    assert r"\begin{table}[p]" in text


def test_appendix_does_not_clearpage_between_case_inventory_heading_and_tables():
    text = Path("paper/sections/appendix.tex").read_text()
    start = text.index(r"\section{Historical Case Inventory}")
    input_pos = text.index(r"\input{sections/generated/case_inventory_tables}")
    case_inventory_block = text[start:input_pos]
    assert r"\clearpage" not in case_inventory_block


def test_figure_6_generator_uses_aggregate_start_end_transitions():
    text = Path("scripts/generate_paper_figures.py").read_text()
    assert "Start-to-End Capability Transitions" in text
    assert "Aggregate CINC score across conflict participants" in text
    assert "Start total CINC" in text
    assert "End total CINC" in text
    assert '.groupby("year", as_index=False)' in text


def test_figure_6_no_direct_participant_row_timeseries_plot():
    text = Path("scripts/generate_paper_figures.py").read_text()
    forbidden = '''ax.plot(
            sub["year"],
            sub[value_col],'''
    assert forbidden not in text


def test_no_landscape_environments_in_paper():
    text = all_tex()
    assert r"\begin{landscape}" not in text
    assert r"\end{landscape}" not in text


def test_no_pdflscape_package_in_manuscript():
    text = Path("paper/manuscript.tex").read_text()
    assert r"\usepackage{pdflscape}" not in text


def test_blind_validation_table_no_final_class_column():
    text = Path("paper/tables/blind_validation_table.tex").read_text()
    assert "Final class" not in text
    assert "Final Class" not in text


def test_normalization_table_no_missing_column():
    text = Path("paper/sections/appendix.tex").read_text()
    start = text.index(r"\section{DSS and SES Normalization Formulas}")
    end = text.index(r"\section{Blind Validation}")
    normalization_block = text[start:end]
    assert r"\textbf{Missing}" not in normalization_block
