# AGENTS.md — Block Kit Models

## Adding a New Block Kit Type

Block Kit models live in `slack_sdk/models/blocks/` across three files:

| File | Contents |
| --- | --- |
| `blocks.py` | Layout blocks (`SectionBlock`, `ActionsBlock`, `HeaderBlock`, etc.) |
| `block_elements.py` | Interactive elements (`ButtonElement`, `StaticSelectElement`, `DatePickerElement`, etc.) |
| `basic_components.py` | Composition objects (`TextObject`, `Option`, `ConfirmObject`, etc.) |

All types are exported from `slack_sdk/models/blocks/__init__.py`.

### Base class hierarchy

```
JsonObject
├── Block                      → layout blocks
├── BlockElement               → non-interactive elements
│   └── InteractiveElement     → elements with action_id
│       └── InputInteractiveElement → elements usable inside InputBlock
├── TextObject                 → PlainTextObject, MarkdownTextObject
├── Option / OptionGroup
└── ConfirmObject, etc.
```

Choose the base class that matches the type you're adding.

### Steps

1. **Define the class** in the appropriate file. Follow this pattern:

   ```python
   class MyNewBlock(Block):
       type = "my_new_block"

       @property
       def attributes(self) -> Set[str]:
           return super().attributes.union({"text", "optional_field"})

       def __init__(self, *, text: Union[str, dict, TextObject], optional_field: Optional[str] = None, block_id: Optional[str] = None, **others: dict):
           super().__init__(type=self.type, block_id=block_id)
           show_unknown_key_warning(self, others)
           self.text = TextObject.parse(text, default_type=PlainTextObject.type)
           self.optional_field = optional_field

       @JsonValidator("text must be provided")
       def _validate_text(self):
           return self.text is not None
   ```

   Key conventions:
   - Set `type` class attribute to the Slack API type string
   - Override `attributes` to return the set of JSON field names for serialization
   - Call `super().__init__()` with `type=self.type`
   - Call `show_unknown_key_warning(self, others)` to log unexpected kwargs
   - Use `TextObject.parse()`, `ConfirmObject.parse()`, and `BlockElement.parse()` for nested composition objects
   - Use `@EnumValidator` for fields restricted to a set of values

2. **Register for deserialization:**
   - **Elements:** Automatic — `BlockElement.parse()` discovers subclasses at runtime via `__subclasses__()`. No manual step needed.
   - **Blocks:** Manual — add an `elif` clause in `Block.parse()` (in `blocks.py`) mapping the type string to the new class.

3. **Export the class** — add it to the imports and `__all__` list in `slack_sdk/models/blocks/__init__.py`.

4. **Add tests** in `tests/slack_sdk/models/test_blocks.py`. Cover:
   - Round-trip: `input_dict == MyNewBlock(**input_dict).to_dict()`
   - Validation: required fields raise `SlackObjectFormationError` when missing
   - Constraints: max lengths, enum values, format patterns

5. **Validate:** `./scripts/run_validation.sh`
