# Data dictionary

**Inspection date:** 2026-09-23  
**Workspace:** `C:\Users\devansh\test-app\TigerGraphAI`  
**README used:** `dataset/README.md` (byte-identical copy of `C:\Users\devansh\Downloads\README.md`, 38663 bytes). Title: *TigerGraph × Hacker House Goa — Fraud Investigation Dataset (IEEE-CIS edition)*.

This document records **only** what the dataset README states, plus the result of looking for files on disk. It does **not** invent column meanings, join keys, or entity relationships.

Legend:

- **README-stated:** written in the official README.
- **UNKNOWN — MUST VERIFY:** not observable because the data files were not present, or the README does not specify it.

---

## Inspection status of `data/raw/`

| Check | Result |
| --- | --- |
| Path `data/raw/` in this repository | **Does not exist** |
| Path `dataset/` | Exists; contains **only** `README.md` |
| `transactions.csv`, `identity.csv`, `closed_cases_history.csv`, `case_pack.csv` on disk | **Not found** next to the README, in `data/raw/`, or in `dataset/` |
| Row counts, headers, null rates, uniqueness, ID formats | **UNKNOWN — MUST VERIFY** after the four CSVs are placed in `data/raw/` (or another agreed path) without modifying them |

**Do not treat README row counts as file-verified.** They are README-stated only.

Until the CSVs are present, every header name, delimiter quirk, quoting, ID prefix (`3514030` vs `T0412877`), and uniqueness claim below that depends on files is **UNKNOWN — MUST VERIFY**.

---

## 1. Every file

### 1.1 Files the README says belong in the dataset folder

| File | README-stated contents | Present in `data/raw/` |
| --- | --- | --- |
| `README.md` | Task, data description, known patterns, regulatory URLs, fraud policy, answer format, 20 cases | **No `data/raw/`**. A copy exists at `dataset/README.md` |
| `transactions.csv` | 590,742 transactions; all 393 original Vesta columns plus `customer_id`, `ts`, `channel`, `risk_score`; no fraud flag; ~708 MB; UTF-8 CSV with header; amounts in USD | **UNKNOWN — MUST VERIFY** (file missing) |
| `identity.csv` | 144,432 identity records; all 41 original columns; online transactions only | **UNKNOWN — MUST VERIFY** (file missing) |
| `closed_cases_history.csv` | 5,565 finished investigations, July–October; 4,665 confirmed fraud, 900 cleared | **UNKNOWN — MUST VERIFY** (file missing) |
| `case_pack.csv` | The 20 exam cases and their triggers; also tabulated in the README | **UNKNOWN — MUST VERIFY** (file missing) |

README-stated join: `transactions.csv` joins to `identity.csv` on `TransactionID`.

### 1.2 Files not in the dataset folder

Regulatory PDFs are **linked by URL** in the README. They are **not** listed as files in the dataset folder. Whether any PDF is bundled with the CSVs is **UNKNOWN — MUST VERIFY**.

No other filenames are named by the README.

---

## 2. Every important column

**Exact full header lists for the CSVs are UNKNOWN — MUST VERIFY** until headers are read from the files. The README gives **groups** and **named extra columns**, not a 393-name dump of `transactions.csv`.

### 2.1 `transactions.csv` — original Vesta groups (README)

Vesta published column **groups**, not individual definitions. README instruction: use them as signals and be honest in evidence about what a column is.

| Group / columns | Count (README) | README meaning | Individual names |
| --- | --- | --- | --- |
| `TransactionID`, `TransactionDT`, `TransactionAmt` | 3 | ID; seconds from the dataset start; amount in USD | Named |
| `ProductCD` | 1 | Product code: `W`, `C`, `H`, `R`, `S`. `W` has no identity record and is treated as in person | Named |
| `card1` to `card6` | 6 | Card details. `card4` = network (visa, mastercard, american express, discover). `card6` = type (credit, debit). The others = issuer codes | Named as `card1`–`card6`. **Which of `card1`–`card3`,`card5` is which issuer field: README does not specify beyond “issuer codes”.** |
| `addr1`, `addr2` | 2 | Billing region and billing country, as codes. Glossary: `addr1` anonymized billing-region code; `addr2` country code; **87 is the home country** | Named |
| `dist1`, `dist2` | 2 | Distances between two unnamed points, when known | Named. **Point identities: UNKNOWN — MUST VERIFY** (README: unnamed) |
| `P_emaildomain`, `R_emaildomain` | 2 | Purchaser and recipient email domains | Named |
| `C1` to `C14` | 14 | Counts, such as how many addresses or phones are associated with the card. Unnamed individually | Group only |
| `D1` to `D15` | 15 | Time deltas in days, such as days since the previous transaction. Unnamed individually | Group only |
| `M1` to `M9` | 9 | Match flags, such as whether the name on the card matches the address. Unnamed individually | Group only |
| `V1` to `V339` | 339 | Vesta engineered features: ranking, counting, and relationships between entities. Unnamed | Group only |

Group counts 3+1+6+2+2+2+14+15+9+339 = **393**, matching “all 393 original Vesta columns.” **Whether the CSV header uses exactly these names (including `V1` vs `V001`) is UNKNOWN — MUST VERIFY.**

### 2.2 `transactions.csv` — columns the README says were added

| Column | README meaning |
| --- | --- |
| `customer_id` | Example `C01234`. Derived from the card issuer field. One customer can have several cards. Card IDs in the **cases** look like `C01234-K1` |
| `ts` | Real timestamp, `YYYY-MM-DD HH:MM:SS`, from July 2 to December 31, 2016 |
| `channel` | `in_person` or `online` |
| `risk_score` | 0 to 1 from the bank’s detection model. An input, not an answer. Above 0.7, most flagged transactions turn out legitimate. Some fraud scores near zero |

README: `TransactionID`, `card1`, `TransactionDT`, and `TransactionAmt` were disguised (new IDs, small time and amount offsets). Everything else is untouched.

**Does `transactions.csv` contain a `card_id` column** (the `C01234-K1` form used in the case pack)? **UNKNOWN — MUST VERIFY** from the file header. The README names `card_id` on `closed_cases_history.csv` and `case_pack.csv`, and shows card IDs in cases; it does **not** list `card_id` among columns added to `transactions.csv`.

### 2.3 `identity.csv` (README)

| Columns | README meaning |
| --- | --- |
| `TransactionID` | Join key to `transactions.csv` |
| `id_01` to `id_11` | Encoded ratings: device rating, IP-domain rating, proxy rating, login counts, time on page. **Which id maps to which rating: not specified individually except as this list of examples.** |
| `id_12` to `id_38` | Categorical identity fields. README-named readable ones: `id_15` (device New / Found), `id_23` (proxy: transparent, anonymous, hidden), `id_30` (OS), `id_31` (browser), `id_33` (screen), `id_34` (match status). **Meanings of the other `id_12`–`id_38` fields: UNKNOWN — MUST VERIFY** (README does not define them) |
| `DeviceType` | mobile or desktop |
| `DeviceInfo` | device or platform description, e.g. `SAMSUNG SM-G935F Build/NRD90M` |

README: 41 original columns. 11 + 27 + 2 = 40 plus `TransactionID` = 41. **Confirm header names and that no extra columns exist: UNKNOWN — MUST VERIFY.**

### 2.4 `closed_cases_history.csv` (README lists these names)

`case_id`, `customer_id`, `card_id`, `opened_at`, `closed_at`, `outcome` (`confirmed_fraud` / `cleared`), `pattern`, `first_fraud_txn_id`, `txn_ids` (pipe-separated), `n_txns`, `exposure_usd`, `connected_card_ids`, `actions_taken`, `report_filed`, `analyst_notes`

**Extra columns, dtypes, delimiter inside `connected_card_ids`, date formats: UNKNOWN — MUST VERIFY.**

### 2.5 `case_pack.csv` (README lists these names)

`case_id`, `opened_at`, `trigger_type` (`risk_score` / `customer_report` / `analyst_request`), `trigger_text`, `flagged_txn_id`, `card_id`, `customer_id`, `risk_score` (filled only for risk-score triggers)

**Extra columns and exact `flagged_txn_id` string format vs `TransactionID`: UNKNOWN — MUST VERIFY.**

---

## 3. Primary identifiers

| Entity (README term) | Identifier field(s) | Notes |
| --- | --- | --- |
| Transaction | `TransactionID` | README: disguised. Case pack uses numeric-looking IDs (e.g. `3514030`). Answer-format **example** uses `T0412877`. **Canonical string form in the CSV: UNKNOWN — MUST VERIFY** |
| Customer | `customer_id` | Example `C01234`. README: derived from the card issuer field |
| Card (in cases / closed cases) | `card_id` | Example `C01234-K1`. **How `card_id` is constructed from `card1`–`card6` + `customer_id`: not specified beyond example pattern. UNKNOWN — MUST VERIFY from files** |
| Closed case | `case_id` | Example in answer format: `CC-0141` |
| Exam case | `case_id` | `HHG-001` … `HHG-020` in the README table |
| Device profile | **Not given as a single CSV column.** Suggested schema: DeviceInfo + OS + browser + screen. Answer example also cites `device_id=D000731`. **Whether a `D######` id exists in data: UNKNOWN — MUST VERIFY** |
| Email domain | `P_emaildomain`, `R_emaildomain` as **values**, not a separate ID column | |
| Billing region | `addr1` as code | |
| Investigation case written to graph | `graph_case_id` in the **answer file**, not a source CSV. Example `CASE-2016-1187`. **Allocation rule: UNKNOWN — MUST VERIFY** (not a dataset column) |

**Uniqueness of each key in the CSVs: UNKNOWN — MUST VERIFY** (files not loaded).

---

## 4. Foreign keys / relationships

### 4.1 README-stated

| From | To | How README states it |
| --- | --- | --- |
| `identity.csv`.`TransactionID` | `transactions.csv`.`TransactionID` | Join; identity is online only |
| `ProductCD` = `W` | no identity record; channel treated as in person | Glossary / ProductCD |
| `customer_id` | one customer, several cards | Added-columns section |
| Closed case | transactions via `first_fraud_txn_id`, `txn_ids` | Column list |
| Closed case | card via `card_id`; other cards via `connected_card_ids` | Column list |
| Closed case | customer via `customer_id` | Column list |
| Case pack | flagged transaction `flagged_txn_id`, `card_id`, `customer_id` | Column list |
| Suggested graph edges | `Customer-OWNS-Card`, `Card-MADE-Transaction`, `Transaction-FROM_DEVICE-DeviceProfile` (online), `Transaction-PURCHASER_EMAIL-EmailDomain`, `Transaction-BILLED_IN-BillingRegion` from `addr1`, `Transaction-NEXT-Transaction` ordered by `ts` within a card, `ClosedCase-INVOLVES-Transaction`, `ClosedCase-ON_CARD-Card`, `ClosedCase-CONNECTED_TO-Card` | “Suggested graph schema” — **engineering suggestion, not a file-verified FK** |

### 4.2 Not stated as keys (do not invent)

| Possible relationship | Status |
| --- | --- |
| `transactions` row → `card_id` | **UNKNOWN — MUST VERIFY** whether a `card_id` column exists on transactions, or must be derived |
| `card1` uniqueness = one Card vertex | README does not say `card1` is the card primary key. **UNKNOWN — MUST VERIFY** |
| Merchant / `ProductCD` as merchant | README: product code, not merchant ID. **No merchant entity is named in the suggested schema.** |
| `R_emaildomain` as a graph edge | Suggested schema only names `PURCHASER_EMAIL`. Recipient domain is a column; **edge not specified. UNKNOWN — MUST VERIFY** whether to model it |
| `addr2` as a vertex | Suggested schema uses `BillingRegion` from `addr1` only |
| Closed case `txn_ids` always subset of `transactions.csv` | Implied by “IDs must exist in this dataset” for **answers**; **file integrity UNKNOWN — MUST VERIFY** |
| Case-pack `flagged_txn_id` = `TransactionID` | Intended by README (“flagged transaction”); **string equality UNKNOWN — MUST VERIFY** |

---

## 5. Transaction identifiers

| Item | Status |
| --- | --- |
| Field name | README-stated: `TransactionID` |
| Closed-case episode list | `txn_ids` (pipe-separated), `first_fraud_txn_id` |
| Exam flag | `flagged_txn_id` |
| Disguise | README: new IDs so public IEEE-CIS/Kaggle lookup is invalid |
| Prefix `T` vs bare integer | README table uses values like `3514030`; example answer uses `T0412877`. **UNKNOWN — MUST VERIFY from CSV** |
| Uniqueness | **UNKNOWN — MUST VERIFY** |
| `TransactionDT` vs `ts` | `TransactionDT` = seconds from dataset start; `ts` = calendar timestamp. **Exact epoch of `TransactionDT`: UNKNOWN — MUST VERIFY** |

---

## 6. Customer identifiers

| Item | Status |
| --- | --- |
| Field | `customer_id` (example `C01234`) |
| Derivation | README: derived from “the card issuer field.” **Which of `card1`–`card6` is that field: UNKNOWN — MUST VERIFY** |
| Cardinality | README: one customer can have several cards |
| Present on | README lists it on transactions (added), closed cases, case pack. **Presence on identity.csv: UNKNOWN — MUST VERIFY** (not listed) |

---

## 7. Device information

| Item | README-stated | File-verified |
| --- | --- | --- |
| Online vs in person | `channel`; `W` / no identity = in person | **UNKNOWN — MUST VERIFY** |
| `DeviceType` | mobile or desktop | **UNKNOWN — MUST VERIFY** |
| `DeviceInfo` | platform string example given | **UNKNOWN — MUST VERIFY** |
| OS, browser, screen | `id_30`, `id_31`, `id_33` | **UNKNOWN — MUST VERIFY** values |
| Device New / Found | `id_15` | **UNKNOWN — MUST VERIFY** |
| Device profile vertex | Suggested: DeviceInfo + OS + browser + screen | **How to concatenate, missing-field handling, ID: UNKNOWN — MUST VERIFY** |
| Shared devices across cards | “Things to know”: a device profile shared across many cards in a short window is worth a look | Observation guidance, not a column |

---

## 8. Identity information

Identity records exist **only for online** transactions (README).

| Field group | README |
| --- | --- |
| `id_01`–`id_11` | Encoded ratings (device, IP-domain, proxy, login counts, time on page) — not mapped 1:1 by name |
| `id_12`–`id_38` | Categorical; only `id_15`, `id_23`, `id_30`, `id_31`, `id_33`, `id_34` are called readable |
| `id_23` | proxy: transparent, anonymous, hidden |
| `id_34` | match status — **match of what: not further specified** |
| Coverage | 144,432 identity rows vs 590,742 transactions (README). **Per-file coverage UNKNOWN — MUST VERIFY** |

---

## 9. Connection information

README uses “connection” in two ways:

1. **Identity / connection details** Vesta captured for online txns: device type/model, OS, browser, screen, proxy flag, encoded ratings (glossary: identity record).
2. **Graph connections** between people via shared device profile or billing region (“Things to know”).

Columns that are README-relevant to connection/sharing:

| Column / field | Role in README |
| --- | --- |
| Identity device fields | Shared origin (policy R6): same device profile |
| `addr1` / billing region | Shared origin; out-of-region pattern |
| `R_emaildomain` | Policy R6: same recipient email |
| Closed case `connected_card_ids` | Other cards in the historical episode |
| Answer field `connected_device_profiles` | Device profile strings linking cards |

**IP address, session ID, or cookie columns: not named. UNKNOWN — MUST VERIFY from headers** (may be hidden inside unnamed `id_*` / `V*` features).

**`proxy` as a dedicated column vs `id_23` / encoded ratings: README mentions a proxy flag in the glossary and `id_23` as readable proxy values. Whether a separate proxy column exists: UNKNOWN — MUST VERIFY.**

---

## 10. Risk-score information

| Item | README-stated |
| --- | --- |
| Column | `risk_score` on every transaction (added) |
| Range | 0 to 1 |
| Source | Bank detection model |
| Role | Reason to look; **never a verdict** |
| Quality | Often wrong both ways. Above 0.7, most flagged transactions legitimate. Some fraud near zero |
| Case pack | `risk_score` filled **only** for `trigger_type` = `risk_score` |
| Agent output | `case.fraud_probability` is a **separate** number; may differ far from the model score; scored for calibration |
| **Formula for `fraud_probability`** | **Not in the dataset. UNKNOWN — MUST VERIFY** is wrong label — it is **not provided**; it is an agent output, not a column |

---

## 11. Historical case information

Source: `closed_cases_history.csv` (July–October). Starting memory for GraphRAG / `similar_prior_cases`.

| Field | README |
| --- | --- |
| `outcome` | `confirmed_fraud` / `cleared` |
| Counts | 4,665 confirmed, 900 cleared (README-stated) |
| `pattern` | Five known patterns, plus `undocumented` for some confirmed fraud; cleared → `pattern` = `none` with notes why false alarm |
| `txn_ids` | Pipe-separated |
| `analyst_notes` | Text; README: read undocumented notes carefully |
| `actions_taken`, `report_filed` | Named; **value enumerations UNKNOWN — MUST VERIFY** from file |
| Date window vs exam | History Jul–Oct; case pack Nov–Dec |

**Do not use these outcomes as labels for November–December exam transactions.** README: exam has no fraud flag; using public IEEE-CIS files to recover outcomes is disqualification.

---

## 12. Fraud-pattern information

**Known patterns (analyst-recognized). Not the only patterns in the data.**

| `pattern` enum (answer format) | README description | Policy hook |
| --- | --- | --- |
| `card_testing` | Three or more tiny online authorizations, often under $5, then a larger purchase. Confirmed by the sequence | R5 |
| `card_not_present_fraud` | Number used online without the card. Amounts/products that don’t fit history; often 2–4 within 48 hours. One unusual online purchase is ambiguous: verify | R1–R4 |
| `card_not_present_new_device` | Same as CNP, identity marks device `New`, sometimes behind a proxy. Stronger than pattern 2, not proof | (described; no extra exclusive rule number) |
| `out_of_region_use` | Card-present purchases in a billing region with no history, while normal activity continues at home. Several days in one new region is a trip, not a clone | R2, R3 |
| `account_takeover` | Mixed-channel activity inconsistent with the cardholder; device and match-flag anomalies; stolen credentials vs stolen number | (described) |
| `undocumented` | Abuse that fits none of the five; describe in `pattern_description`. History file also uses this | R9 |
| `none` | No fraud pattern (cleared / legitimate) | — |

**Numeric thresholds in pattern text** ($5, 48 hours, three authorizations, etc.) are README pattern descriptions. **Whether they are exact detectors vs examples: treat as README text; do not add extra unpublished patterns.**

---

## 13. Policy information

**Location:** README section `# Fraud Policy` Version 1.0. **Not a separate data file.**

Action identifiers (must be used exactly):  
`ALLOW_TRANSACTION`, `DECLINE_TRANSACTION`, `MONITOR_CARD`, `MONITOR_CONNECTED_CARDS`, `WARN_CUSTOMER`, `VERIFY_WITH_CUSTOMER`, `STEP_UP_AUTH`, `BLOCK_CARD`, `BLOCK_ALL_CARDS`, `GENERATE_REPORT`, `CREATE_CASE`, `FILE_REPORT`, `ESCALATE_TO_ANALYST`, `CLOSE_NO_FRAUD`.

Approval routes: `auto` | `L1` | `L2` as specified in the README routing table.

Rules: **R1–R10** plus 3a (case vs SAR), 3b (NBA can change), §4 exposure, §5 evidence gathering, §6 stopping, §7 explaining.

Evidence request types (simulated; responses not in the dataset): `customer_validation` | `step_up_auth` | `analyst_info`.

**Customer/analyst reply tables: not provided. UNKNOWN — MUST VERIFY does not apply to missing files — they are specified as absent; simulate and record assumptions.**

---

## 14. Regulatory information

**Location:** README “Regulatory references” — public URLs (FinCEN, FATF, FFIEC, OFAC). Instruction: load useful ones into TigerGraph vector search with closed cases and the policy.

**PDFs are not in `data/raw/` (path missing) and not listed as dataset files.** Whether a team-local copy exists elsewhere: **UNKNOWN — MUST VERIFY**.

SAR narrative standard: README points at FinCEN SAR Narrative Guidance for `sar.narrative` (who, what, when, where, how, why).

FILE_REPORT conditions: policy 3a (exposure > $1000 **or** shared device/region/other-customer fraud **or** R9), plus confirmed or strongly suspected fraud; always L2; always behind a case.

---

## 15. Benchmark case information

Twenty cases, also in `case_pack.csv`. README table (IDs must match the CSV when present):

| Case | Opened (README) | Trigger | Flagged txn | Card | Customer | Score |
| --- | --- | --- | --- | --- | --- | --- |
| HHG-001 | 2016-12-05 01:55:28 | risk_score | 3514030 | C12382-K1 | C12382 | 0.61 |
| HHG-002 | 2016-11-22 23:27:07 | risk_score | 3478782 | C11891-K1 | C11891 | 0.79 |
| HHG-003 | 2016-12-10 15:01:21 | customer_report | 3530164 | C08623-K2 | C08623 | — |
| HHG-004 | 2016-12-29 07:53:54 | customer_report | 3583227 | C08106-K1 | C08106 | — |
| HHG-005 | 2016-12-08 03:38:37 | risk_score | 3523199 | C02923-K1 | C02923 | 0.54 |
| HHG-006 | 2016-11-22 02:30:00 | customer_report | 3476682 | C07297-K1 | C07297 | — |
| HHG-007 | 2016-12-05 03:46:14 | risk_score | 3514948 | C09933-K2 | C09933 | 0.87 |
| HHG-008 | 2016-12-20 03:08:56 | customer_report | 3558054 | C13171-K2 | C13171 | — |
| HHG-009 | 2016-12-28 17:10:53 | customer_report | 3581141 | C08299-K1 | C08299 | — |
| HHG-010 | 2016-12-02 18:18:27 | risk_score | 3506725 | C10434-K1 | C10434 | 0.90 |
| HHG-011 | 2016-12-29 06:27:44 | customer_report | 3583368 | C11923-K2 | C11923 | — |
| HHG-012 | 2016-12-18 05:00:31 | risk_score | 3553342 | C05876-K2 | C05876 | 0.55 |
| HHG-013 | 2016-12-09 05:39:29 | risk_score | 3526826 | C07671-K2 | C07671 | 0.76 |
| HHG-014 | 2016-11-22 20:11:00 | analyst_request | 3478561 | C13487-K1 | C13487 | — |
| HHG-015 | 2016-11-17 19:03:36 | risk_score | 3464869 | C03042-K1 | C03042 | 0.77 |
| HHG-016 | 2016-12-12 01:39:08 | customer_report | 3534820 | C09988-K1 | C09988 | — |
| HHG-017 | 2016-11-12 00:46:24 | risk_score | 3450629 | C04570-K1 | C04570 | 0.57 |
| HHG-018 | 2016-11-27 14:41:26 | customer_report | 3491361 | C02354-K2 | C02354 | — |
| HHG-019 | 2016-12-01 22:28:53 | risk_score | 3503878 | C07987-K2 | C07987 | 0.90 |
| HHG-020 | 2016-12-03 12:04:26 | risk_score | 3509359 | C12265-K2 | C12265 | 0.52 |

README: flagged txn is where the alert fired; it may not be the start of fraud and may not be fraud. **About half the cases are legitimate.** Hidden answer key. Optional extra exams-period investigations go in a **separate folder** (Innovation, not accuracy).

**CSV vs table equality: UNKNOWN — MUST VERIFY** when `case_pack.csv` is available.

---

## 16. Required output format

Submit **20 JSON files**, `cases/<case_id>.json` (e.g. `cases/HHG-001.json`). Missing fields score zero for that part.

### Top level

| Field | Type | Meaning |
| --- | --- | --- |
| `case_id` | string | From `case_pack.csv` |
| `case` | object | Internal investigation record |
| `evidence_requests` | list | `{type, asked_after_step, assumed_response}` or `[]` |
| `next_best_actions` | object | `initial`, `final`, `what_changed` |
| `sar` | object | Regulatory filing block |
| `stop_reason` | string | Why the investigation ended |
| `tool_calls` | int | Graph and retrieval calls |
| `tokens` | int | LLM tokens |
| `latency_s` | number | Wall-clock seconds |

### `case`

`status`: `open` | `closed_fraud` | `closed_legitimate` | `escalated`  
`verdict`: `fraud` | `legitimate` | `uncertain`  
`fraud_probability`: 0–1  
`pattern`: enum in §12  
`pattern_description`: required text if `undocumented`, else `""`  
`affected_txn_ids`, `first_suspicious_txn_id`, `connected_card_ids`, `connected_device_profiles`, `exposure_usd`  
`evidence[]`: `{claim, source (graph\|document\|customer\|external), ref, entity_ids}`  
`similar_prior_cases`: closed-case IDs from history  
`summary`, `written_to_graph`, `graph_case_id`

Legitimate: empty `affected_txn_ids`, `exposure_usd` 0, `sar.file` false. All IDs must exist in this dataset.

### `sar`

`file` must agree with whether `FILE_REPORT` is in **final** actions. If `file` is false: empty narrative, empty subjects, `total_amount_usd` 0, empty `activity_dates`.

### `next_best_actions`

Each action: `{action, route, reason}` with policy identifiers. If no evidence requests, `final` equals `initial`. `what_changed` is `"nothing"` or 1–2 sentences.

---

## Gaps that block file-level verification

1. `data/raw/` is missing; four CSVs not inspected.  
2. Full `transactions.csv` / `identity.csv` headers.  
3. Whether `card_id` exists on transactions.  
4. TransactionID string format.  
5. Device profile primary key / `D000731`-style IDs.  
6. Enumerations for `actions_taken`, `report_filed`.  
7. Null rates, duplicates, referential integrity.  
8. Whether regulatory PDFs are bundled.

Place the unmodified CSVs (and README) in `data/raw/` and re-run header/key verification before implementing loaders.
