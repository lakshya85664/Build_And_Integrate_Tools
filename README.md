# Topic 3 — Build and Integrate Tools

## Overview
This project implements a controlled tool-integration layer for an AI agent architecture. It provides a reusable tool registry, validates tool arguments before execution, distinguishes transient from permanent failures, enforces an authority boundary for sensitive operations, and records structured execution traces with secret redaction.

## Objectives
- Register and discover tools through a controlled registry.
- Validate tool arguments before execution.
- Reject invalid arguments safely.
- Retry transient failures with a bounded retry count.
- Avoid retrying permanent failures.
- Enforce explicit authority for sensitive operations.
- Record observable tool-execution traces.
- Prevent secrets from appearing in traces.
- Validate all components with automated tests.

## Project Structure
```text
Build_And_Integrate_Tools/
├── tools.py
├── task1_tool_registry.py
├── task2_argument_validation.py
├── task3_tool_failure.py
├── task4_authority_boundary.py
├── task5_tool_trace.py
├── tests/
│   ├── test_task1.py
│   ├── test_task2.py
│   ├── test_task3.py
│   ├── test_task4.py
│   └── test_task5.py
└── traces/
    ├── task1_tool_registry.jsonl
    ├── task2_argument_validation.jsonl
    ├── task3_tool_failure.jsonl
    ├── task4_authority_boundary.jsonl
    └── task5_tool_trace.jsonl
```

## Task 1 — Tool Registry
`tools.py` provides `Tool` and `ToolRegistry`. The registry supports registration, discovery, and invocation. Unknown tools and missing required arguments are rejected.

## Task 2 — Argument Validation
Arguments are validated before tool execution. The weather example requires a non-empty city and a supported unit (`C` or `F`). Invalid arguments are rejected before execution.

## Task 3 — Tool Failure
Transient failures are retried with a bounded retry count and backoff. Permanent failures are not retried. Structured traces distinguish retrying transient failures from permanent failures.

## Task 4 — Authority Boundary
An explicit authorization boundary protects sensitive operations. A read-only lookup can execute when authorized, while an unauthorized delete operation is rejected before the underlying data is modified.

## Task 5 — Tool Trace
The trace records request, validation, authority, completion, rejection, and failure events. API keys, tokens, passwords, and secrets are replaced with `***REDACTED***` before being written to traces.

## Testing
Final regression:
```cmd
python -m pytest -q
```
Result:
```text
22 passed in 0.23s
```

Task results:
- Task 1: 4 passed
- Task 2: 4 passed
- Task 3: 4 passed
- Task 4: 5 passed
- Task 5: 5 passed

## Evidence
Each task produces structured JSONL evidence under `traces/`. Evidence covers successful invocation, rejected tools and arguments, bounded retries, permanent failures without retry, authority decisions, completion events, and secret redaction.

## Reflection
This activity helped me understand that integrating tools into an AI agent is not simply about making functions callable. A reliable tool layer needs controls around discovery, input validation, failures, authorization, and observability.

The tool registry provided a clear abstraction for registering and discovering capabilities. Argument validation added an important boundary because invalid inputs should be rejected before they reach the underlying tool.

The failure-handling task demonstrated why retry behavior must depend on the type of failure. A transient failure may succeed later, while a permanent failure should not be repeatedly retried. The implementation therefore uses a bounded retry count and retries only the transient exception.

The authority-boundary task reinforced that a model-generated request should not automatically be treated as permission to perform a sensitive action. The delete operation was protected by an explicit authorization set, and the test confirmed that an unauthorized request did not modify the stored order.

Finally, the tracing task showed the importance of observability and secret hygiene. The trace records the major stages of execution while replacing API keys, tokens, passwords, and secrets with a redacted value.

The final regression suite passed all 22 tests, providing evidence that the five components work together as intended.
