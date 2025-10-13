import json
from src.models.lab_model import LabManager


def sample_data():
    return {
        "config": {
            "courses": [
                {"course_id": "CMSC 140", "credits": 4, "lab": ["Linux"], "faculty": ["Hardy"]},
                {"course_id": "CMSC 161", "credits": 4, "lab": [], "faculty": ["Zoppetti"]},
            ],
            "labs": ["Linux", "Mac"]
        }
    }


def test_lab_manager_basic_ops():
    mgr = LabManager()
    mgr.data = sample_data()

    # get existing
    c = mgr.get_course_by_id("CMSC 140")
    assert c is not None
    assert c["course_id"] == "CMSC 140"

    # add lab to course without labs
    assert mgr.add_lab("CMSC 161", "Mac") is True
    assert "Mac" in mgr.get_course_by_id("CMSC 161")["lab"]

    # adding duplicate returns False
    assert mgr.add_lab("CMSC 161", "Mac") is False

    # modify lab
    assert mgr.modify_lab("CMSC 140", "Linux", "Windows") is True
    assert "Windows" in mgr.get_course_by_id("CMSC 140")["lab"]

    # modify non-existent lab
    assert mgr.modify_lab("CMSC 140", "Python", "Java") is False

    # delete lab
    assert mgr.delete_lab("CMSC 140", "Windows") is True
    assert "Windows" not in mgr.get_course_by_id("CMSC 140")["lab"]

    # delete from course with no labs
    assert mgr.delete_lab("CMSC 161", "Linux") is False


def test_lab_manager_file_io(tmp_path):
    mgr = LabManager()
    data = sample_data()
    f = tmp_path / "cfg.json"
    f.write_text(json.dumps(data))

    mgr.load_data(str(f))
    assert mgr.data is not None
    assert mgr.config_file == str(f)

    # save_data should write back to file (no exception)
    mgr.data["config"]["courses"][0]["lab"].append("TestLab")
    mgr.save_data()

    # reload
    m2 = LabManager()
    m2.load_data(str(f))
    assert any("TestLab" in c.get("lab", []) for c in m2.data.get("config", {}).get("courses", []))
