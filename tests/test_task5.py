import json


def test_traced_success_contains_execution_events():
    import task5_tool_trace as module

    module.TRACE_PATH.unlink(
        missing_ok=True
    )

    registry = module.build_registry()

    result = module.invoke_traced(
        registry,
        "get_status",
        {"item": "agent"},
        {"get_status"},
    )

    assert result == "status for agent: ready"

    records = [
        json.loads(line)
        for line in module.TRACE_PATH
        .read_text(encoding="utf-8")
        .splitlines()
    ]

    events = [
        record["event"]
        for record in records
    ]

    assert events == [
        "tool_requested",
        "arguments_validated",
        "authority_granted",
        "tool_completed",
    ]


def test_authority_failure_is_traced():
    import task5_tool_trace as module

    module.TRACE_PATH.unlink(
        missing_ok=True
    )

    registry = module.build_registry()

    try:
        module.invoke_traced(
            registry,
            "get_status",
            {"item": "agent"},
            set(),
        )
    except module.AuthorityError:
        pass
    else:
        raise AssertionError(
            "Authority failure should be raised"
        )

    records = [
        json.loads(line)
        for line in module.TRACE_PATH
        .read_text(encoding="utf-8")
        .splitlines()
    ]

    assert records[-1]["event"] == (
        "authority_denied"
    )
    assert records[-1]["status"] == "rejected"


def test_validation_failure_is_traced():
    import task5_tool_trace as module

    module.TRACE_PATH.unlink(
        missing_ok=True
    )

    registry = module.build_registry()

    try:
        module.invoke_traced(
            registry,
            "get_status",
            {"item": ""},
            {"get_status"},
        )
    except module.ToolValidationError:
        pass
    else:
        raise AssertionError(
            "Validation failure should be raised"
        )

    records = [
        json.loads(line)
        for line in module.TRACE_PATH
        .read_text(encoding="utf-8")
        .splitlines()
    ]

    assert records[-1]["event"] == (
        "tool_rejected"
    )
    assert records[-1]["status"] == "rejected"


def test_trace_redacts_secrets():
    import task5_tool_trace as module

    module.TRACE_PATH.unlink(
        missing_ok=True
    )

    registry = module.build_registry()

    module.invoke_traced(
        registry,
        "get_status",
        {
            "item": "agent",
            "api_key": "SUPER_SECRET",
            "token": "PRIVATE_TOKEN",
            "password": "PRIVATE_PASSWORD",
        },
        {"get_status"},
    )

    content = module.TRACE_PATH.read_text(
        encoding="utf-8"
    )

    assert "SUPER_SECRET" not in content
    assert "PRIVATE_TOKEN" not in content
    assert "PRIVATE_PASSWORD" not in content
    assert "***REDACTED***" in content


def test_trace_contains_no_secret_keys_as_plain_values():
    import task5_tool_trace as module

    module.TRACE_PATH.unlink(
        missing_ok=True
    )

    registry = module.build_registry()

    module.invoke_traced(
        registry,
        "get_status",
        {
            "item": "agent",
            "secret": "HIDDEN",
        },
        {"get_status"},
    )

    records = [
        json.loads(line)
        for line in module.TRACE_PATH
        .read_text(encoding="utf-8")
        .splitlines()
    ]

    first = records[0]

    assert first["arguments"]["secret"] == (
        "***REDACTED***"
    )