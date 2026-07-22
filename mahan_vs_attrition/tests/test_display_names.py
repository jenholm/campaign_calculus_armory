from mahan_vs_attrition.display_names import display_war_name


def test_problem_cow_ids_are_human_readable():
    assert display_war_name("cow_iw_106") == "World War I (1914-1918)"
    assert "Paraguayan" in display_war_name("cow_iw_49")
    assert "Sino-Japanese" in display_war_name("cow_iw_130")


def test_no_raw_cow_id_for_known_ids():
    for war_id in ["cow_iw_49", "cow_iw_106", "cow_iw_130"]:
        assert "cow_iw" not in display_war_name(war_id)
