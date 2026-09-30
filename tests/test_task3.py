def test_transient_failure_is_retried():
    from task3_tool_failure import (
        FlakyTool,
        build_registry,
        invoke_with_retry,
    )

    registry = build_registry()

    result = invoke_with_retry(
        registry,
        "flaky_tool",
        {"value": "report"},
        max_retries=2,
    )

    assert result == "processed: report"


def test_transient_retry_is_bounded():
    from task3_tool_failure import (
        FlakyTool,
        invoke_with_retry,
    )
    from tools import Tool, ToolRegistry

    flaky = FlakyTool(
        failures_before_success=10
    )

    registry = ToolRegistry()

    registry.register(
        Tool(
            name="always_flaky",
            run=flaky,
            required=("value",),
        )
    )

    try:
        invoke_with_retry(
            registry,
            "always_flaky",
            {"value": "report"},
            max_retries=2,
        )
    except Exception as exc:
        assert type(exc).__name__ == (
            "TransientToolError"
        )
    else:
        raise AssertionError(
            "Retry limit should be enforced"
        )

    assert flaky.calls == 3


def test_permanent_failure_is_not_retried():
    from task3_tool_failure import (
        build_registry,
        invoke_with_retry,
    )

    registry = build_registry()

    try:
        invoke_with_retry(
            registry,
            "permanent_tool",
            {"value": "report"},
            max_retries=2,
        )
    except Exception as exc:
        assert type(exc).__name__ == (
            "PermanentToolError"
        )
    else:
        raise AssertionError(
            "Permanent failure should propagate"
        )


def test_retry_count_is_configurable():
    from task3_tool_failure import (
        FlakyTool,
        invoke_with_retry,
    )
    from tools import Tool, ToolRegistry

    flaky = FlakyTool(
        failures_before_success=2
    )

    registry = ToolRegistry()

    registry.register(
        Tool(
            name="retry_tool",
            run=flaky,
            required=("value",),
        )
    )

    result = invoke_with_retry(
        registry,
        "retry_tool",
        {"value": "ok"},
        max_retries=2,
    )

    assert result == "processed: ok"
    assert flaky.calls == 3