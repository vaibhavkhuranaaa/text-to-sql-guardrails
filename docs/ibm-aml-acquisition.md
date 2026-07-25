# IBM AML benchmark acquisition procedure

## Pinned release

- Provider record: IBM `AML-Data` repository, which directs consumers to the
  newer Kaggle release and states that the data is licensed under
  CDLA-Sharing-1.0.
- Dataset: `ealtman2019/ibm-transactions-for-anti-money-laundering-aml`.
- Immutable provider version: **8** (provider metadata dated 2025-07-08).
- Private benchmark target: `HI-Small_Trans.csv` and its paired
  `HI-Small_Patterns.txt` from version 8 only.
- Provider metadata observed: 2026-07-25. No dataset artifact was downloaded
  or inspected while pinning this procedure.

The provider's versioned download mechanism must be used with version 8. A
current-dataset URL without an explicit version is not an approved substitute.

## Approved M3 acquisition checklist

1. Obtain a separate owner authorization to begin M3; this M0 approval does
   not authorize a download.
2. Download only the two pinned files to an ignored local directory outside the
   container build context. Do not copy them into Git, the public fixture, or
   any cloud storage.
3. Calculate SHA-256 for each acquired file and record only the artifact name,
   version, digest, byte count, license, and acquisition timestamp in row-free
   local provenance metadata.
4. Verify the recorded license before transforming data. Stop if the provider
   version, file name, or license differs from this record.
5. Keep raw files, account-like values, laundering labels, pattern details,
   source rows, prompts, result rows, credentials, and environment values out
   of model context, public previews, logs, evidence, Git, and the container
   build context.
6. Build only the approved private derivative. Public evidence may contain a
   benchmark digest, row count, schema/transform version, and aggregate
   outcomes—not source values.
7. Delete raw and derived local benchmark artifacts after 30 days. Retain only
   row-free provenance and aggregate evidence.

## Sources

- [IBM AML-Data release notes](https://github.com/IBM/AML-Data/blob/main/README.md)
- [IBM Research benchmark publication](https://research.ibm.com/publications/realistic-synthetic-financial-transactions-for-anti-money-laundering-models)
- [Kaggle dataset metadata](https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml)
