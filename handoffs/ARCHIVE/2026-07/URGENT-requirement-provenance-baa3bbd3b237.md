# Requirement-provenance gate rejected a project handoff

**Source**: handoff dispatcher
**Target**: general-codex
**Original handoff**: /opt/workspace/runtime/.handoff/general-codex-preflight-v0.1.1-deployment-metadata-complete-2026-07-26T21-27-50Z.md
**Quarantined intact at**: /opt/workspace/runtime/.handoff/REJECTED/baa3bbd3b237-general-codex-preflight-v0.1.1-deployment-metadata-complete-2026-07-26T21-27-50Z.md
**Reason**: missing required provenance fields: external_dependencies

The handoff was not dispatched, marked complete, or left on the project PM's
direct inbox path. Correct its underlying objective under ADR-0047 and create a
new handoff; preserve this quarantined artifact as evidence. Required non-empty
fields are `authority`, `external_dependencies`, and
`policy_compatibility`. The external-dependency field is the scalar enum
`none` or `authorized`; authorized dependencies additionally require
`dependency_authority` and `dependency_details`.
