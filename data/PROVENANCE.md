# Fixture provenance

- Source: [MoMTSim V2 synthetic mobile-money transaction dataset](https://data.mendeley.com/datasets/zhj366m53p/2), DOI `10.17632/zhj366m53p.2`
- Version / published date: version 2 / 2024-10-29
- License: CC BY 4.0
- Retrieval checked: 2026-07-22
- Source description: synthetic mobile-money transactions generated with MoMTSim.
- Derived-fixture method: this repository does **not** redistribute or normalize source rows. `payments.json` is a six-field, hand-authored synthetic fixture designed only to exercise the documented star schema and deterministic tests.
- Approved release boundary: `data/source_manifest.json` records the owner-verified SHA-256 for both V2 source files. The local reviewed copies produced the aggregate-only `data/approved/profile.json`; resulting snapshots, metadata, and benchmark evidence are local artifacts excluded from Git.
- Curated-source boundary: V2 source headers were profiled on 2026-07-22. `initiator` and `recipient` are treated as account identifiers and excluded from the approved snapshot. `step` is retained only as `simulation_step`; it is not represented as a calendar date or timestamp.
- Fixture SHA-256: `089709b3a93363aa04e7398404336eddde104bf6d5bc06e9d3b4c801fe1a34d3`

Attribution is not an assertion that the source represents real bank/cardholder data. The repository makes no such claim.
