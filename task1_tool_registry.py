import json
from pathlib import Path

from tools import Tool, ToolRegistry, ToolValidationError


TRACE_PATH = Path("traces/task1_tool_registry.jsonl")


def write_trace(record: dict) -> None:
    TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with TRACE_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")


def lookup_order(args: dict) -> str:
    orders = {
        "A100": "packed",
        "A101": "shipped",
        "A102": "delivered",
    }

    order_id = args["order_id"]

    return orders.get(
        order_id,
        "not found",
    )


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()

    registry.register(
        Tool(
            name="lookup_order",
            run=lookup_order,
            required=("order_id",),
        )
    )

    return registry


def main() -> None:
    TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)
    TRACE_PATH.write_text("", encoding="utf-8")

    registry = build_registry()

    print("TOPIC 3 — TASK 1: TOOL REGISTRY")
    print("=" * 45)

    # Happy path
    result = registry.invoke(
        "lookup_order",
        {"order_id": "A100"},
    )

    print("HAPPY PATH")
    print(f"registered tools: {registry.names()}")
    print(f"lookup result: {result}")

    write_trace(
        {
            "case": "happy_path",
            "event": "tool_invoked",
            "tool": "lookup_order",
            "arguments": {"order_id": "A100"},
            "result": result,
            "status": "success",
        }
    )

    # Failure path
    try:
        registry.invoke(
            "missing_tool",
            {"order_id": "A100"},
        )
    except ToolValidationError as exc:
        print()
        print("FAILURE PATH")
        print("tool invocation rejected")
        print(f"error: {type(exc).__name__}")
        print(f"message: {exc}")

        write_trace(
            {
                "case": "failure_path",
                "event": "tool_rejected",
                "tool": "missing_tool",
                "error": type(exc).__name__,
                "message": str(exc),
                "status": "rejected",
            }
        )

    print()
    print(f"Trace saved to: {TRACE_PATH}")


if __name__ == "__main__":
    main()