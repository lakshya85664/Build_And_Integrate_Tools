import json
import time
from pathlib import Path

from tools import Tool, ToolRegistry, ToolValidationError
from task3_tool_failure import (
    TransientToolError,
    PermanentToolError,
)
from task4_authority_boundary import AuthorityError


TRACE_PATH = Path(
    "traces/task5_tool_trace.jsonl"
)


class SecretRedactor:
    """Removes sensitive values from trace records."""

    SECRET_KEYS = {
        "api_key",
        "token",
        "password",
        "secret",
    }

    @classmethod
    def redact(cls, value):
        if isinstance(value, dict):
            return {
                key: (
                    "***REDACTED***"
                    if key.lower() in cls.SECRET_KEYS
                    else cls.redact(item)
                )
                for key, item in value.items()
            }

        if isinstance(value, list):
            return [
                cls.redact(item)
                for item in value
            ]

        return value


def write_trace(record: dict) -> None:
    TRACE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    safe_record = SecretRedactor.redact(record)

    with TRACE_PATH.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(safe_record) + "\n"
        )


def get_status(args: dict) -> str:
    return f"status for {args['item']}: ready"


def validate_args(args: dict) -> None:
    if not isinstance(args, dict):
        raise ToolValidationError(
            "arguments must be a dictionary"
        )

    item = args.get("item")

    if not isinstance(item, str):
        raise ToolValidationError(
            "item must be a string"
        )

    if not item.strip():
        raise ToolValidationError(
            "item must be non-empty"
        )


def invoke_traced(
    registry: ToolRegistry,
    tool_name: str,
    args: dict,
    authorized_tools: set[str],
) -> str:

    start = time.perf_counter()

    safe_args = SecretRedactor.redact(args)

    write_trace(
        {
            "event": "tool_requested",
            "tool": tool_name,
            "arguments": safe_args,
        }
    )

    try:
        validate_args(args)

        write_trace(
            {
                "event": "arguments_validated",
                "tool": tool_name,
                "status": "success",
            }
        )

        if tool_name not in authorized_tools:
            raise AuthorityError(
                f"authority denied for tool: {tool_name}"
            )

        write_trace(
            {
                "event": "authority_granted",
                "tool": tool_name,
                "status": "success",
            }
        )

        result = registry.invoke(
            tool_name,
            args,
        )

        duration_ms = round(
            (time.perf_counter() - start) * 1000,
            3,
        )

        write_trace(
            {
                "event": "tool_completed",
                "tool": tool_name,
                "result": result,
                "duration_ms": duration_ms,
                "status": "success",
            }
        )

        return result

    except ToolValidationError as exc:
        write_trace(
            {
                "event": "tool_rejected",
                "tool": tool_name,
                "error": type(exc).__name__,
                "message": str(exc),
                "status": "rejected",
            }
        )
        raise

    except AuthorityError as exc:
        write_trace(
            {
                "event": "authority_denied",
                "tool": tool_name,
                "error": type(exc).__name__,
                "message": str(exc),
                "status": "rejected",
            }
        )
        raise

    except (TransientToolError, PermanentToolError) as exc:
        write_trace(
            {
                "event": "tool_failed",
                "tool": tool_name,
                "error": type(exc).__name__,
                "message": str(exc),
                "status": "failed",
            }
        )
        raise


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()

    registry.register(
        Tool(
            name="get_status",
            run=get_status,
            required=("item",),
        )
    )

    return registry


def main() -> None:
    TRACE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    TRACE_PATH.write_text(
        "",
        encoding="utf-8",
    )

    registry = build_registry()

    print("TOPIC 3 — TASK 5: TOOL TRACE")
    print("=" * 45)

    print("HAPPY PATH")

    result = invoke_traced(
        registry,
        "get_status",
        {
            "item": "agent",
            "api_key": "SECRET_VALUE",
        },
        {"get_status"},
    )

    print(f"result: {result}")

    print()
    print("AUTHORITY FAILURE PATH")

    try:
        invoke_traced(
            registry,
            "get_status",
            {
                "item": "agent",
                "token": "PRIVATE_TOKEN",
            },
            set(),
        )

    except AuthorityError as exc:
        print("tool call rejected")
        print(
            f"error: {type(exc).__name__}"
        )
        print(f"message: {exc}")

    print()
    print("VALIDATION FAILURE PATH")

    try:
        invoke_traced(
            registry,
            "get_status",
            {
                "item": "",
                "password": "PRIVATE_PASSWORD",
            },
            {"get_status"},
        )

    except ToolValidationError as exc:
        print("tool call rejected")
        print(
            f"error: {type(exc).__name__}"
        )
        print(f"message: {exc}")

    print()
    print(f"Trace saved to: {TRACE_PATH}")


if __name__ == "__main__":
    main()