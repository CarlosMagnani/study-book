# Domain Docs

How engineering skills should consume this repo's domain documentation.

## Before exploring, read these

- `CONTEXT.md` at the repo root, or `CONTEXT-MAP.md` when it exists.
- Relevant decisions in `docs/adr/`.

If these files do not exist, proceed silently. Create them only when the project records terminology or an architectural decision.

## File structure

This is a single-context repository:

```text
/
├── CONTEXT.md
├── docs/
│   └── adr/
└── src/
```

## Vocabulary and ADRs

Use the terminology defined in `CONTEXT.md`. Surface any conflict with an existing ADR instead of silently overriding it.
