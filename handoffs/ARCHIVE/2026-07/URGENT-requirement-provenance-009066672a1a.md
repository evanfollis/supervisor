# Requirement-provenance gate rejected a project handoff

**Source**: handoff dispatcher
**Target**: atlas
**Original handoff**: /opt/workspace/runtime/.handoff/atlas-canon-path-env-hatch-2026-07-26.md
**Quarantined intact at**: /opt/workspace/runtime/.handoff/REJECTED/009066672a1a-atlas-canon-path-env-hatch-2026-07-26.md
**Reason**: missing required provenance fields: external_dependencies policy_compatibility

The handoff was not dispatched, marked complete, or left on the project PM's
direct inbox path. Correct its underlying objective under ADR-0047 and create a
new handoff; preserve this quarantined artifact as evidence. Required non-empty
fields are `authority`, `external_dependencies`, and
`policy_compatibility`. The external-dependency field is the scalar enum
`none` or `authorized`; authorized dependencies additionally require
`dependency_authority` and `dependency_details`.
