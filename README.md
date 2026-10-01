# VEC P3 Freeze

P3 changes the cost of a mistake: the current rules allow **two official submissions per board for the whole final phase**, each scored immediately and not withdrawable.

`vec-p3-freeze` creates an immutable local submission bundle for those scarce slots. It does not choose models or score them; it prevents "wrong file", "file changed after selection", and "which slot was this?" mistakes.

## Usage

```bash
# Freeze slot 1
vec-p3-freeze freeze \
  --bundle final_bundle \
  --board T2:heart:val_extrap \
  --slot 1 \
  --file candidates/model17.h5ad \
  --note "selected by pseudo-split + manual review"

# Freeze slot 2 later
vec-p3-freeze freeze --bundle final_bundle --board T2:heart:val_extrap --slot 2 --file candidates/model23.h5ad

# Verify no byte changed
vec-p3-freeze verify --bundle final_bundle

# Generate one upload checklist
vec-p3-freeze checklist --bundle final_bundle
```

The bundle stores a byte-for-byte copy, SHA256, source path, UTC freeze time and note. Frozen prediction files are made read-only. A third slot is refused by construction.

This is **not** a format validator; use the official/local validator before freezing.
