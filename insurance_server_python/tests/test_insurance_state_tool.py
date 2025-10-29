from insurance_server_python.main import (
    INSURANCE_STATE_WIDGET_IDENTIFIER,
    WIDGETS_BY_ID,
    _insurance_state_tool_handler,
)


def test_insurance_state_tool_requests_widget_without_text_when_state_missing() -> None:
    result = _insurance_state_tool_handler({})

    assert "response_text" not in result
    assert result["structured_content"] == {}

    meta = result["meta"]
    widget = WIDGETS_BY_ID[INSURANCE_STATE_WIDGET_IDENTIFIER]

    assert meta["openai/outputTemplate"] == widget.template_uri
    assert meta["openai/resultCanProduceWidget"] is True
    assert "openai.com/widget" in meta


def test_insurance_state_tool_confirms_when_state_available() -> None:
    result = _insurance_state_tool_handler({"state": "CA"})

    assert result["structured_content"] == {"state": "California"}
    assert result["response_text"] == "Captured California as the customer's state."

    meta = result["meta"]
    assert meta["openai/resultCanProduceWidget"] is False
    assert "openai.com/widget" not in meta
