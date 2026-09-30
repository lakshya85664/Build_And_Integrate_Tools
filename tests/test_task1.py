import json


def test_registry_registers_and_invokes_tool():
    from task1_tool_registry import build_registry

    registry = build_registry()

    assert "lookup_order" in registry.names()
    assert registry.invoke(
        "lookup_order",
        {"order_id": "A100"},
    ) == "packed"


def test_registry_rejects_unknown_tool():
    from task1_tool_registry import build_registry
    from tools import ToolValidationError

    registry = build_registry()

    try:
        registry.invoke(
            "unknown_tool",
            {"order_id": "A100"},
        )
    except ToolValidationError as exc:
        assert "tool not found" in str(exc)
    else:
        raise AssertionError(
            "Unknown tool should be rejected"
        )


def test_registry_rejects_missing_required_argument():
    from task1_tool_registry import build_registry
    from tools import ToolValidationError

    registry = build_registry()

    try:
        registry.invoke(
            "lookup_order",
            {},
        )
    except ToolValidationError as exc:
        assert "missing arguments" in str(exc)
    else:
        raise AssertionError(
            "Missing required argument should be rejected"
        )


def test_registry_trace_is_created():
    import task1_tool_registry

    task1_tool_registry.TRACE_PATH.unlink(
        missing_ok=True
    )

    registry = task1_tool_registry.build_registry()

    result = registry.invoke(
        "lookup_order",
        {"order_id": "A100"},
    )

    task1_tool_registry.write_trace(
        {
            "case": "test",
            "tool": "lookup_order",
            "result": result,
            "status": "success",
        }
    )

    records = [
        json.loads(line)
        for line in task1_tool_registry.TRACE_PATH
        .read_text(encoding="utf-8")
        .splitlines()
    ]

    assert len(records) == 1
    assert records[0]["status"] == "success"