from app.services.graph_calendar import normalize_response_status


def test_normalize_response_status() -> None:
    assert normalize_response_status("accepted", False) == "accepted"
    assert normalize_response_status("tentativelyAccepted", False) == "tentative"
    assert normalize_response_status("notResponded", False) == "notResponded"
    assert normalize_response_status(None, True) == "organizer"
    assert normalize_response_status("none", False) == "unknown"
