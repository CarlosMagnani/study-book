## Agent skills

### Issue tracker

GitHub Issues are the issue tracker. See `docs/agents/issue-tracker.md`.

### Triage labels

Use the default canonical labels. See `docs/agents/triage-labels.md`.

### Domain docs

This is a single-context repository. See `docs/agents/domain.md`.

### Project structure

Keep source, tests, documentation, and generated video artifacts separate:

- Application code belongs in `src/study_book/`.
- Tests belong in `tests/` and mirror the source module they cover.
- Project documentation belongs in `docs/`; architectural decisions belong in
  `docs/adr/`.
- Downloaded audio, source metadata, transcripts, and analyses belong in
  `downloads/<video-id>/` and must not be committed.
- Keep the repository root for project configuration, `README.md`, and
  `AGENTS.md`; do not add new application modules there.

The current root-level downloader is transitional. Move it into the source
package when the next implementation step introduces the package layout.

### Learning notes

This project is built as a learning exercise. For every non-trivial
application-code step or change, create or update one Portuguese learning note
in `docs/learn-it/`.

Each note must name the source file, explain the change's context and expected
behavior, and explain every added or changed line in plain Portuguese,
including the relevant Python syntax. Keep one note per implementation step so
the learner can follow the project in order. This rule does not apply to
generated artifacts, dependency-only changes, or documentation-only edits.
