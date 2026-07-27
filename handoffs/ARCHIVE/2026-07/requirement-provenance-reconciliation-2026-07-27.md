# Requirement-provenance reconciliation — 2026-07-27

Five ADR-0047 rejection alerts are archived here after valid successor
handoffs and external outcome evidence reconciled their underlying objectives.
The rejected handoffs remain intact under
`/opt/workspace/runtime/.handoff/REJECTED/`; archiving an alert does not rewrite
or delete that evidence.

## Archived alerts

| Alert | SHA-256 |
|---|---|
| `URGENT-requirement-provenance-009066672a1a.md` | `4b9c1db8c1d340751c1cf6ac55019b60b208a5dfac16e4162e3d8675b42cceaa` |
| `URGENT-requirement-provenance-3d2ba80280bd.md` | `bcbdf50525c2677ae411a11e1fa984c911ce58af869e6fd9e0064e7104fcfd7d` |
| `URGENT-requirement-provenance-a9a99dfea799.md` | `01a147ac2e3cdc4604972b7030bc05ede43617f74c0e33123d85d78885791a56` |
| `URGENT-requirement-provenance-baa3bbd3b237.md` | `e4cb46e6bd0a937288224f3d5273e1bba8219e6eb739750e0939e399df06e36e` |
| `URGENT-requirement-provenance-e406b1186cab.md` | `de222827ecc74b3868b7bb452b460b4a7e988aade7a011665bc6157bed97d2d3` |

## Successor evidence

- Atlas repository migration:
  `/opt/workspace/runtime/.handoff/ARCHIVE/2026-07-26/general-codex-atlas-july-2026-profiled-repository-migration-complete-2026-07-26T21-29-32Z.md`
- Synaplex canon-path reconciliation:
  `/opt/workspace/runtime/.handoff/ARCHIVE/2026-07-26/synaplex-canon-path-env-hatch-reconciliation-2026-07-26T20-50-08Z.md`
- Synaplex typed public lineage and Cadence closure:
  `/opt/workspace/runtime/.handoff/general-synaplex-cadence-lineage-dependency-closure-2026-07-27T00-17-00Z.md`
- Preflight live-metadata reconciliation:
  `/opt/workspace/runtime/.handoff/ARCHIVE/2026-07-26/general-codex-preflight-live-metadata-correction-reconciliation-2026-07-26T21-47-32Z.md`
- Preflight dependency, security, deployment, and containment closure:
  `/opt/workspace/runtime/.handoff/general-codex-dependency-closure-security-containment-addendum-complete-2026-07-27T00-28-39Z.md`

All successor handoffs declare non-empty authority, external-dependency, and
policy-compatibility fields. Each affected repository passed its clean-check
gate, and the hosted products or public routes were verified independently
where the objective changed runtime or public state.
