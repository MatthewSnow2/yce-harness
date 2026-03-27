# Table of Contents

- [Module: sample_code](#module-samplecode)
- [Module: sample_code.module_a](#module-samplecodemodulea)
- [Module: sample_code.module_b](#module-samplecodemoduleb)

## Module: sample_code

Sample code package for testing csuite.

## Module: sample_code.module_a

Module A - Contains sample classes and functions.

### Classes

- **BaseClass** — A base class for demonstration.
  - Methods:
    - `__init__(self, name: str)`
    - `greet(self) -> str` — Return a greeting.
- **SampleClass** (extends: BaseClass) — A sample class that extends BaseClass.
  - Methods:
    - `__init__(self, name: str, value: int = 0)`
    - `compute(self, x: int) -> int` — Compute a value.

### Functions

- **func_a(x: int) -> str** — Returns a string representation of x.
- **helper_func(data: list) -> dict** — Transforms a list into a dictionary.

## Module: sample_code.module_b

Module B - Contains more sample classes.

### Classes

- **AnotherClass** — Another class for testing.
  - Methods:
    - `__init__(self)`
    - `add_item(self, item: str) -> None` — Add an item to the list.
    - `get_items(self) -> list` — Return all items.
- **ChildClass** (extends: SampleClass) — A child class that extends SampleClass.
  - Methods:
    - `compute(self, x: int) -> int` — Override compute with multiplication.

### Functions

- **func_b(text: str) -> str** — Process text by stripping and lowering.
