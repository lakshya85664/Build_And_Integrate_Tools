import json
import time
from pathlib import Path

from tools import Tool, ToolRegistry, ToolValidationError


TRACE_PATH = Path(
    "traces/task3_tool_failure.jsonl"
)


class TransientToolError(RuntimeError):
    """Failure that may succeed if retried."""


class PermanentToolError(RuntimeError):
    """Failure that should not be retried."""


def write_trace(record: dict) -> None:
    TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with TRACE_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")


class FlakyTool:
    """Tool that fails transiently a controlled number of times."""

    def __init__(self, failures_before_success: int) -> None:
        self.failures_before_success = failures_before_success
        self.calls = 0

    def __call__(self, args: dict) -> str:
        self.calls += 1

        if self.calls <= self.failures_before_success:
            raise TransientToolError(
                "temporary service failure"
            )

        return f"processed: {args['value']}"


def permanent_tool(args: dict) -> str:
    raise PermanentToolError(
        "permanent tool failure"
    )


def invoke_with_retry(
    registry: ToolRegistry,
    tool_name: str,
    args: dict,
    max_retries: int = 2,
    backoff_seconds: float = 0.01,
) -> str:
    if max_retries < 0:
        raise ToolValidationError(
            "max_retries must be non-negative"
        )

    attempt = 0

    while True:
        try:
            attempt += 1

            result = registry.invoke(
                tool_name,
                args,
            )

            write_trace(
                {
                    "event": "tool_success",
                    "tool": tool_name,
                    "attempt": attempt,
                    "status": "success",
                }
            )

            return result

        except TransientToolError as exc:
            if attempt > max_retries:
                write_trace(
                    {
                        "event": "retry_exhausted",
                        "tool": tool_name,
                        "attempt": attempt,
                        "error": type(exc).__name__,
                        "message": str(exc),
                        "status": "failed",
                    }
                )
                raise

            write_trace(
                {
                    "event": "transient_failure",
                    "tool": tool_name,
                    "attempt": attempt,
                    "error": type(exc).__name__,
                    "message": str(exc),
                    "retry": True,
                    "status": "retrying",
                }
            )

            time.sleep(backoff_seconds)

        except PermanentToolError as exc:
            write_trace(
                {
                    "event": "permanent_failure",
                    "tool": tool_name,
                    "attempt": attempt,
                    "error": type(exc).__name__,
                    "message": str(exc),
                    "retry": False,
                    "status": "failed",
                }
            )
            raise


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()

    registry.register(
        Tool(
            name="flaky_tool",
            run=FlakyTool(
                failures_before_success=1
            ),
            required=("value",),
        )
    )

    registry.register(
        Tool(
            name="permanent_tool",
            run=permanent_tool,
            required=("value",),
        )
    )

    return registry


def main() -> None:
    TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)
    TRACE_PATH.write_text("", encoding="utf-8")

    registry = build_registry()

    print("TOPIC 3 — TASK 3: TOOL FAILURE")
    print("=" * 45)

    # Happy path with transient failure + retry
    print("HAPPY PATH")
    result = invoke_with_retry(
        registry,
        "flaky_tool",
        {"value": "report"},
        max_retries=2,
    )
    print(f"result: {result}")

    # Permanent failure path
    print()
    print("FAILURE PATH")

    try:
        invoke_with_retry(
            registry,
            "permanent_tool",
            {"value": "report"},
            max_retries=2,
        )
    except PermanentToolError as exc:
        print("permanent failure handled")
        print(f"error: {type(exc).__name__}")
        print(f"message: {exc}")

    print()
    print(f"Trace saved to: {TRACE_PATH}")


if __name__ == "__main__":
    main()