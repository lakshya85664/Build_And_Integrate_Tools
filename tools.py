from dataclasses import dataclass
from typing import Callable


class ToolValidationError(ValueError):
    """Raised when tool invocation arguments are invalid."""


@dataclass
class Tool:
    name: str
    run: Callable[[dict], str]
    required: tuple[str, ...] = ()

    def invoke(self, args: dict) -> str:
        if not isinstance(args, dict):
            raise ToolValidationError(
                "tool arguments must be a dictionary"
            )

        missing = [
            key
            for key in self.required
            if key not in args
        ]

        if missing:
            raise ToolValidationError(
                f"missing arguments: {missing}"
            )

        return self.run(args)


class ToolRegistry:
    """Registry used to discover and invoke registered tools."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if not isinstance(tool, Tool):
            raise ToolValidationError(
                "only Tool instances can be registered"
            )

        if not tool.name.strip():
            raise ToolValidationError(
                "tool name must be non-empty"
            )

        if tool.name in self._tools:
            raise ToolValidationError(
                f"tool already registered: {tool.name}"
            )

        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        if not isinstance(name, str) or not name.strip():
            raise ToolValidationError(
                "tool name must be a non-empty string"
            )

        if name not in self._tools:
            raise ToolValidationError(
                f"tool not found: {name}"
            )

        return self._tools[name]

    def invoke(self, name: str, args: dict) -> str:
        tool = self.get(name)
        return tool.invoke(args)

    def names(self) -> list[str]:
        return sorted(self._tools)