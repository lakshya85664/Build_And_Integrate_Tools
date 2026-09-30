import json
from pathlib import Path

from tools import Tool, ToolRegistry, ToolValidationError


TRACE_PATH = Path(
    "traces/task2_argument_validation.jsonl"
)


def write_trace(record: dict) -> None:
    TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with TRACE_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")


def get_weather(args: dict) -> str:
    city = args["city"]
    unit = args["unit"]

    return f"Weather for {city}: 25 degrees {unit}"


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()

    registry.register(
        Tool(
            name="get_weather",
            run=get_weather,
            required=("city", "unit"),
        )
    )

    return registry


def validate_weather_arguments(args: dict) -> None:
    if not isinstance(args, dict):
        raise ToolValidationError(
            "arguments must be a dictionary"
        )

    city = args.get("city")
    unit = args.get("unit")

    if not isinstance(city, str) or not city.strip():
        raise ToolValidationError(
            "city must be a non-empty string"
        )

    if not isinstance(unit, str):
        raise ToolValidationError(
            "unit must be a string"
        )

    if unit not in {"C", "F"}:
        raise ToolValidationError(
            "unit must be 'C' or 'F'"
        )


def invoke_validated(
    registry: ToolRegistry,
    args: dict,
) -> str:
    validate_weather_arguments(args)

    return registry.invoke(
        "get_weather",
        args,
    )


def main() -> None:
    TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)
    TRACE_PATH.write_text("", encoding="utf-8")

    registry = build_registry()

    print("TOPIC 3 — TASK 2: ARGUMENT VALIDATION")
    print("=" * 50)

    # Happy path
    valid_args = {
        "city": "Surat",
        "unit": "C",
    }

    result = invoke_validated(
        registry,
        valid_args,
    )

    print("HAPPY PATH")
    print(f"arguments: {valid_args}")
    print(f"result: {result}")

    write_trace(
        {
            "case": "happy_path",
            "event": "arguments_validated",
            "arguments": valid_args,
            "result": result,
            "status": "success",
        }
    )

    # Failure path
    invalid_args = {
        "city": "Surat",
        "unit": "K",
    }

    try:
        invoke_validated(
            registry,
            invalid_args,
        )
    except ToolValidationError as exc:
        print()
        print("FAILURE PATH")
        print(f"arguments: {invalid_args}")
        print("tool invocation rejected before execution")
        print(f"error: {type(exc).__name__}")
        print(f"message: {exc}")

        write_trace(
            {
                "case": "failure_path",
                "event": "arguments_rejected",
                "arguments": invalid_args,
                "error": type(exc).__name__,
                "message": str(exc),
                "status": "rejected",
            }
        )

    print()
    print(f"Trace saved to: {TRACE_PATH}")


if __name__ == "__main__":
    main()