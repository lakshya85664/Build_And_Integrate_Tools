import json


def test_valid_arguments_are_accepted():
    from task2_argument_validation import (
        build_registry,
        invoke_validated,
    )

    registry = build_registry()

    result = invoke_validated(
        registry,
        {
            "city": "Surat",
            "unit": "C",
        },
    )

    assert result == (
        "Weather for Surat: 25 degrees C"
    )


def test_invalid_unit_is_rejected():
    from task2_argument_validation import (
        build_registry,
        invoke_validated,
    )
    from tools import ToolValidationError

    registry = build_registry()

    try:
        invoke_validated(
            registry,
            {
                "city": "Surat",
                "unit": "K",
            },
        )
    except ToolValidationError as exc:
        assert "unit must be 'C' or 'F'" in str(exc)
    else:
        raise AssertionError(
            "Invalid unit should be rejected"
        )


def test_empty_city_is_rejected():
    from task2_argument_validation import (
        build_registry,
        invoke_validated,
    )
    from tools import ToolValidationError

    registry = build_registry()

    try:
        invoke_validated(
            registry,
            {
                "city": "",
                "unit": "C",
            },
        )
    except ToolValidationError as exc:
        assert "city must be a non-empty string" in str(exc)
    else:
        raise AssertionError(
            "Empty city should be rejected"
        )


def test_trace_contains_success_and_rejection():
    import task2_argument_validation

    task2_argument_validation.TRACE_PATH.unlink(
        missing_ok=True
    )

    registry = task2_argument_validation.build_registry()

    result = task2_argument_validation.invoke_validated(
        registry,
        {
            "city": "Surat",
            "unit": "C",
        },
    )

    task2_argument_validation.write_trace(
        {
            "case": "happy_path",
            "result": result,
            "status": "success",
        }
    )

    try:
        task2_argument_validation.invoke_validated(
            registry,
            {
                "city": "Surat",
                "unit": "K",
            },
        )
    except task2_argument_validation.ToolValidationError as exc:
        task2_argument_validation.write_trace(
            {
                "case": "failure_path",
                "error": type(exc).__name__,
                "message": str(exc),
                "status": "rejected",
            }
        )

    records = [
        json.loads(line)
        for line in task2_argument_validation.TRACE_PATH
        .read_text(encoding="utf-8")
        .splitlines()
    ]

    assert len(records) == 2
    assert records[0]["status"] == "success"
    assert records[1]["status"] == "rejected"