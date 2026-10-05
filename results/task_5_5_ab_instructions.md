# A/B sheet: instructions for raters

File: `task_5_5_ab_sheet.csv` (30 flows; the columns after the two narratives are blank on purpose). `task_5_5_ab_key.csv` says which of A / B is the older narrative and which is the new one and
keeps the flow's predicted class; do not open it before rating.

Each row is one flow (raw values: duration, protocol, service, state, packets, bytes, rate) with two narratives for the same prediction, A and B, in a random order. The two differ only in how the reasons
are written (one lists every cited feature with a magnitude word; the other drops features that look ordinary and says where the value sits among all flows and among flows of the predicted class) and in whether a
calibrated confidence appears. Fill:

| column | values |
|---|---|
| `clearer_A_B_same` | which narrative is easier to understand |
| `more_actionable_A_B_same` | which gives you more to act on, or a better reason to trust or doubt the verdict |
| `comments` | free text |
| `rater` | your name or initials |

Rate each flow on its own and independently of other raters. These ratings are not collected or reported by the analysis; the sheet is a template for the team. The six groups are Normal, Overlap-Group-1,
Fuzzers, flagged Unknown, false-positive Normal (a Normal flow the model called an attack) and one group of the other attack classes (Exploits, Generic, Reconnaissance), 5 flows each.
