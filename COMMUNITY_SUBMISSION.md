# Community Contribution submission text

## Title
VEC P3 Freeze — immutable two-slot final-submission bundle

## Description
P3 Freeze is a small safety tool built around the final-phase rule that each board has only two official submissions for the whole phase. It copies a selected prediction into an explicit board/slot-1-or-2 bundle, records SHA256/source/timestamp/notes, makes the frozen copy read-only, refuses a third slot, and can later verify every byte and generate a single upload checklist. It does not replace scoring or validation; it addresses the operational failure mode of uploading the wrong candidate or changing a selected artifact after model selection when final attempts are scarce.
