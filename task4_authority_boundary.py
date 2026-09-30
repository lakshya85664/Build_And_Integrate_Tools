import json
from pathlib import Path

from tools import Tool, ToolRegistry, ToolValidationError


TRACE_PATH = Path(
    "traces/task4_authority_boundary.jsonl"
)


class AuthorityError(PermissionError):
    """Raised when a tool lacks sufficient authority."""


def write_trace(record: dict) -> None:
    TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with TRACE_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")


ORDERS = {
    "A100": "packed",
    "A101": "shipped",
}


def lookup_order(args: dict) -> str:
    order_id = args["order_id"]

    return ORDERS.get(
        order_id,
        "not found",
    )


def delete_order(args: dict) -> str:
    order_id = args["order_id"]

    if order_id not in ORDERS:
        return "not found"

    del ORDERS[order_id]

    return f"deleted: {order_id}"


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()

    registry.register(
        Tool(
            name="lookup_order",
            run=lookup_order,
            required=("order_id",),
        )
    )

    registry.register(
        Tool(
            name="delete_order",
            run=delete_order,
            required=("order_id",),
        )
    )

    return registry


def authorize(
    tool_name: str,
    authorized_tools: set[str],
) -> None:
    if tool_name not in authorized_tools:
        raise AuthorityError(
            f"authority denied for tool: {tool_name}"
        )


def invoke_authorized(
    registry: ToolRegistry,
    tool_name: str,
    args: dict,
    authorized_tools: set[str],
) -> str:
    authorize(
        tool_name,
        authorized_tools,
    )

    return registry.invoke(
        tool_name,
        args,
    )


def main() -> None:
    TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)
    TRACE_PATH.write_text("", encoding="utf-8")

    registry = build_registry()

    print("TOPIC 3 — TASK 4: AUTHORITY BOUNDARY")
    print("=" * 50)

    # --------------------------------------------------
    # HAPPY PATH
    # --------------------------------------------------

    authorized_tools = {
        "lookup_order",
    }

    result = invoke_authorized(
        registry,
        "lookup_order",
        {"order_id": "A100"},
        authorized_tools,
    )

    print("HAPPY PATH")
    print(
        "authorized tools:",
        sorted(authorized_tools),
    )
    print(f"lookup result: {result}")

    write_trace(
        {
            "case": "happy_path",
            "event": "authorized_tool_call",
            "tool": "lookup_order",
            "arguments": {
                "order_id": "A100",
            },
            "result": result,
            "status": "success",
        }
    )

    # --------------------------------------------------
    # FAILURE PATH
    # --------------------------------------------------

    try:
        invoke_authorized(
            registry,
            "delete_order",
            {"order_id": "A100"},
            authorized_tools,
        )

    except AuthorityError as exc:
        print()
        print("FAILURE PATH")
        print("sensitive tool invocation rejected")
        print(f"error: {type(exc).__name__}")
        print(f"message: {exc}")

        write_trace(
            {
                "case": "failure_path",
                "event": "authority_denied",
                "tool": "delete_order",
                "arguments": {
                    "order_id": "A100",
                },
                "error": type(exc).__name__,
                "message": str(exc),
                "status": "rejected",
            }
        )

    print()
    print(
        "remaining orders:",
        ORDERS,
    )
    print()
    print(
        f"Trace saved to: {TRACE_PATH}"
    )


if __name__ == "__main__":
    main()