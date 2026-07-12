# Completion: reflect validation failure telemetry

Timestamp: 2026-07-12T04-26-29Z

Commit: `207d4c1 reflect: emit telemetry on validation failures`

What changed:
- `scripts/lib/reflect.sh` now initializes the failure telemetry helper before validation exits.
- Missing prompt templates emit `reason=prompt_template_not_found`.
- Missing project directories emit `reason=project_dir_not_found`.
- The HEAD mutation safety-net `exit 3` emits `reason=head_changed` before writing its urgent handoff.
- `tests/test-reflect-failure-telemetry.sh` now covers the deterministic validation failure paths in addition to the existing Claude failure and no-output paths.

Verification:
- `bash tests/test-reflect-failure-telemetry.sh`
