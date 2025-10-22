from typing import Dict, List
from conflicts import (
    ConflictManager,
    load_conflicts_from_config,
    detect_conflicting_assignments,
    suggest_conflict_resolution,
)


def demo_config() -> Dict:
    # Minimal realistic config like your project structure
    return {
        "config": {
            "courses": [
                {"course_id": "CMSC 140", "conflicts": ["CMSC 161", "CMSC 162"]},
                {"course_id": "CMSC 161", "conflicts": ["CMSC 140"]},
                {"course_id": "CMSC 162", "conflicts": ["CMSC 140"]},
                {"course_id": "CMSC 152", "conflicts": []},
            ]
        }
    }


def test_build_and_queries():
    cfg = demo_config()
    cm = load_conflicts_from_config(
        cfg["config"]
    )  # builds ConflictManager from "courses"

    # Basic map checks (bidirectional edges)
    assert cm.has_conflict("CMSC 140", "CMSC 161") is True
    assert cm.has_conflict("CMSC 161", "CMSC 140") is True
    assert cm.has_conflict("CMSC 152", "CMSC 140") is False

    # Get set of conflicts for a course
    c140 = cm.get_conflicts("CMSC 140")
    print("Conflicts for CMSC 140:", c140)
    assert c140 == {"CMSC 161", "CMSC 162"}

    # Add a new conflict and verify
    cm.add_conflict("CMSC 152", "CMSC 161")
    assert cm.has_conflict("CMSC 152", "CMSC 161") is True
    # Remove it and verify
    cm.remove_conflict("CMSC 152", "CMSC 161")
    assert cm.has_conflict("CMSC 152", "CMSC 161") is False


def test_schedule_validation_and_groups():
    cfg = demo_config()
    cm = load_conflicts_from_config(cfg["config"])

    # A schedule is a list of dicts with at least course_id
    schedule: List[Dict] = [
        {"course_id": "CMSC 140"},
        {"course_id": "CMSC 161"},
        {"course_id": "CMSC 152"},
    ]

    conflicts = cm.validate_schedule_conflicts(schedule)
    print("Conflicting pairs in schedule:", conflicts)
    # Only (140,161) should conflict
    assert ("CMSC 140", "CMSC 161") in conflicts or (
        "CMSC 161",
        "CMSC 140",
    ) in conflicts
    assert all(
        pair in {("CMSC 140", "CMSC 161"), ("CMSC 161", "CMSC 140")}
        for pair in conflicts
    )

    # Conflict groups (connected components)
    groups = cm.get_conflict_groups()
    print("Conflict groups:", groups)
    # One group linking 140,161,162 and another with 152 alone (with no conflicts → its own 1-node group)
    flat_groups = [frozenset(g) for g in groups]
    assert frozenset({"CMSC 140", "CMSC 161", "CMSC 162"}) in flat_groups
    assert frozenset({"CMSC 152"}) in flat_groups

    # Together scheduling checks
    assert (
        cm.can_schedule_together(["CMSC 152", "CMSC 161"]) is True
    )  # in base config they don't conflict
    assert cm.can_schedule_together(["CMSC 140", "CMSC 161"]) is False


def test_independent_set_and_suggestions():
    cfg = demo_config()
    cm = load_conflicts_from_config(cfg["config"])

    # Greedy MIS: expect it to include 152 and one of {161,162}
    mis = cm.get_maximum_independent_set()
    print("Greedy independent set:", mis)
    assert "CMSC 152" in mis
    # Should not include both 161 and 162 with 140, because 140 conflicts with both
    assert not ({"CMSC 140", "CMSC 161"} <= mis and {"CMSC 140", "CMSC 162"} <= mis)

    # Detect conflicts in a schedule
    schedule = [{"course_id": "CMSC 140"}, {"course_id": "CMSC 162"}]
    analysis = detect_conflicting_assignments(schedule, cm)
    print("Conflict analysis:", analysis)
    assert analysis["has_conflicts"] is True
    assert set(analysis["courses_with_conflicts"]) == {"CMSC 140", "CMSC 162"}

    # Suggestions text
    sugg = suggest_conflict_resolution(analysis["conflicting_pairs"], schedule, cm)
    print("Suggestions:", sugg)
    assert isinstance(sugg, list) and len(sugg) >= 1


def main():
    test_build_and_queries()
    test_schedule_validation_and_groups()
    test_independent_set_and_suggestions()
    print("\nAll ConflictManager tests passed ✅")


if __name__ == "__main__":
    main()
