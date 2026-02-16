from insurance_server_python.widget_registry import (
    INSURANCE_STATE_WIDGET_IDENTIFIER,
    WIDGETS_BY_ID,
)
from insurance_server_python.tool_handlers import _insurance_state_tool_handler


def _invoke_handler(arguments):
    widget = WIDGETS_BY_ID[INSURANCE_STATE_WIDGET_IDENTIFIER]
    from insurance_server_python.widget_registry import _tool_meta
    widget_meta = _tool_meta(widget)
    widget_resource = {"uri": widget.template_uri}
    return _insurance_state_tool_handler(
        arguments,
        INSURANCE_STATE_WIDGET_IDENTIFIER,
        widget_meta,
        widget_resource
    )


def test_insurance_state_tool_requests_widget_without_text_when_state_missing() -> None:
    result = _invoke_handler({})

    assert "response_text" not in result
    assert result["structured_content"] == {}

    meta = result["meta"]
    widget = WIDGETS_BY_ID[INSURANCE_STATE_WIDGET_IDENTIFIER]

    assert meta["openai/outputTemplate"] == widget.template_uri
    assert meta["openai/resultCanProduceWidget"] is True
    assert "openai.com/widget" in meta


def test_insurance_state_tool_confirms_when_state_available() -> None:
    result = _invoke_handler(
        {"state": "CA", "insuranceType": "Auto", "zipCode": "94107"}
    )

    assert "response_text" not in result
    assert result["structured_content"] == {}

    meta = result["meta"]
    widget = WIDGETS_BY_ID[INSURANCE_STATE_WIDGET_IDENTIFIER]

    assert meta["openai/outputTemplate"] == widget.template_uri
    assert meta["openai/resultCanProduceWidget"] is True
    assert "openai.com/widget" in meta


def test_insurance_state_tool_returns_partial_details_when_incomplete() -> None:
    result = _invoke_handler({"state": "Texas"})

    assert "response_text" not in result
    assert result["structured_content"] == {}

    meta = result["meta"]
    widget = WIDGETS_BY_ID[INSURANCE_STATE_WIDGET_IDENTIFIER]

    assert meta["openai/outputTemplate"] == widget.template_uri
    assert meta["openai/resultCanProduceWidget"] is True
    assert "openai.com/widget" in meta
