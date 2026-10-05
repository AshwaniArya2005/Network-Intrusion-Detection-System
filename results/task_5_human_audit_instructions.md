# Human audit sheet: instructions for raters

File: `task_5_human_audit_sheet.csv` (30 narratives; the columns after the flow values are blank on purpose). `task_5_human_audit_key.csv` maps `sheet_id` to the flow and its predicted-class stratum and is kept
apart so the sheet shows no label; do not open it before rating.

For each row read the narrative and the raw flow values (duration, protocol, service, state, packets, bytes, rate) and fill:

| column | values |
|---|---|
| `rating_understandable_1_to_5` | 1 = could not tell what the system is saying ... 5 = completely clear to a SOC analyst |
| `rating_actionable_1_to_5` | 1 = I would not know what to do ... 5 = the suggested action is what I would do next |
| `rating_agrees_with_my_judgement_yes_no_unsure` | would you, from the flow values alone, reach the same verdict (the attack type or "normal" the narrative names; for "unrecognized pattern" or "Overlap-Group" whether escalating is reasonable)? |
| `comments` | free text, for example "says 'typical' but lists it as a reason" |
| `rater` | your name or initials |

Rate each narrative on its own and independently of other raters. These ratings are not collected or reported by the analysis; the sheet is a template for the team.
