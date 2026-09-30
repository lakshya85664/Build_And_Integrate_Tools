import json


def test_authorized_read_tool_executes():
    from task4_authority_boundary import (
        build_registry,
        invoke_authorized,
    )

    registry = build_registry()

    result = invoke_authorized(
        registry,
        "lookup_order",
        {"order_id": "A100"},
        {"lookup_order"},
    )

    assert result == "packed"


def test_unauthorized_sensitive_tool_is_rejected():
    from task4_authority_boundary import (
        AuthorityError,
        build_registry,
        invoke_authorized,
    )

    registry = build_registry()

    try:
        invoke_authorized(
            registry,
            "delete_order",
            {"order_id": "A100"},
            {"lookup_order"},
        )
    except AuthorityError as exc:
        assert "authority denied" in str(exc)
    else:
        raise AssertionError(
            "Unauthorized delete should be rejected"
        )


def test_authorized_delete_can_execute():
    import task4_authority_boundary as module

    module.ORDERS.clear()
    module.ORDERS.update(
        {
            "A100": "packed",
        }
    )

    registry = module.build_registry()

    result = module.invoke_authorized(
        registry,
        "delete_order",
        {"order_id": "A100"},
        {"delete_order"},
    )

    assert result == "deleted: A100"
    assert "A100" not in module.ORDERS


def test_authority_rejection_does_not_execute_tool():
    import task4_authority_boundary as module

    module.ORDERS.clear()
    module.ORDERS.update(
        {
            "A100": "packed",
        }
    )

    registry = module.build_registry()

    try:
        module.invoke_authorized(
            registry,
            "delete_order",
            {"order_id": "A100"},
            {"lookup_order"},
        )
    except module.AuthorityError:
        pass
    else:
        raise AssertionError(
            "Unauthorized delete should be rejected"
        )

    assert module.ORDERS["A100"] == "packed"


def test_authority_trace_contains_rejection():
    import task4_authority_boundary as module

    module.TRACE_PATH.unlink(
        missing_ok=True
    )

    module.write_trace(
        {
            "case": "failure_path",
            "event": "authority_denied",
            "tool": "delete_order",
            "status": "rejected",
        }
    )

    records = [
        json.loads(line)
        for line in module.TRACE_PATH
        .read_text(encoding="utf-8")
        .splitlines()
    ]

    assert len(records) == 1
    assert records[0]["event"] == "authority_denied"
    assert records[0]["status"] == "rejected"