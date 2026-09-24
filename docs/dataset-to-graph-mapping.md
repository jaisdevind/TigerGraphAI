# Dataset to graph mapping

**Status:** Mapping proposal from the official dataset README only.  
**Data files in `data/raw/`:** not present at inspection; **do not treat this as file-verified.**  
**Schema design is part of the engineering** (README). The vertex/edge names below follow the README **suggested graph schema** unless marked otherwise.

Do **not** implement loaders from this document until CSV headers are verified. Where a mapping depends on a column that might not exist, the row says **UNKNOWN — MUST VERIFY**.

---

## Mapping principles

1. Source of graph facts: CSV fields and README-stated joins only.  
2. Suggested schema may be changed, but extra vertices/edges that are not in the README (e.g. Merchant) are **not** claimed as dataset entities.  
3. Investigation `Case` vertices are **outputs written back**, not rows in the four CSVs (except starting memory from `ClosedCase`).  
4. GraphRAG documents are text the README says to load into TigerGraph vector search; they are not extra CSV entity types.  
5. LLM must not invent hops that are not edges or query results.

---

## TigerGraph vertices

| Vertex type (suggested) | Dataset origin | Primary id (proposed) | Attributes (from named fields only) | Notes |
| --- | --- | --- | --- | --- |
| `Customer` | Distinct `customer_id` on transactions, closed cases, case pack | `customer_id` (e.g. `C01234`) | none required by README | **File uniqueness UNKNOWN — MUST VERIFY** |
| `Card` | `card_id` on closed cases and case pack; cards owned by customers | `card_id` (e.g. `C01234-K1`) | README-available **if present on a card grain**: `card4`, `card6`, issuer codes `card1`–`card3`,`card5` | **How to get one Card row per `card_id` from `transactions.csv` without a `card_id` column: UNKNOWN — MUST VERIFY.** Do not assume `card1` is `card_id`. |
| `Transaction` | `transactions.csv` | `TransactionID` | README-named: `TransactionDT`, `TransactionAmt`, `ProductCD`, `addr1`, `addr2`, `dist1`, `dist2`, `P_emaildomain`, `R_emaildomain`, `C1`–`C14`, `D1`–`D15`, `M1`–`M9`, `V1`–`V339`, `customer_id`, `ts`, `channel`, `risk_score`, `card1`–`card6` | Store unnamed V/C/D/M as attributes or skip until needed; evidence must not pretend to know their definitions. **Exact header names UNKNOWN — MUST VERIFY** |
| `DeviceProfile` | `identity.csv` online rows | **UNKNOWN — MUST VERIFY.** README suggests DeviceInfo + OS + browser + screen. Example answer uses both a concatenated string and `D000731` | `DeviceType`, `DeviceInfo`, `id_30`, `id_31`, `id_33`, optionally `id_15`, `id_23` | In-person / `ProductCD=W`: no identity → **no `FROM_DEVICE` edge** (README) |
| `EmailDomain` | Distinct `P_emaildomain` values (suggested edge is purchaser) | domain string | none specified | Empty/null domains: **UNKNOWN — MUST VERIFY** |
| `BillingRegion` | Distinct `addr1` | `addr1` code | optional `addr2` is **country**, not this vertex (README) | |
| `ClosedCase` | `closed_cases_history.csv` | `case_id` (e.g. `CC-*`) | `opened_at`, `closed_at`, `outcome`, `pattern`, `first_fraud_txn_id`, `txn_ids`, `n_txns`, `exposure_usd`, `connected_card_ids`, `actions_taken`, `report_filed`, `analyst_notes`, `customer_id`, `card_id` | Jul–Oct memory only |
| `Case` (investigation write-back) | **Not a source file.** README: write investigations into the graph | `graph_case_id` from answer format (example `CASE-2016-1187`) | Fields needed to round-trip the answer `case` object | **Id generation rule UNKNOWN — MUST VERIFY** (not specified). Distinct from `ClosedCase` and from exam `HHG-*` |

**Not mapped as vertices (not dataset entities in README schema):** Merchant, IP, Account (separate from Card/Customer), Person name.

**Identity-only encoded fields `id_01`–`id_14`, `id_16`–`id_22`, `id_24`–`id_29`, `id_32`, `id_35`–`id_38`:** keep as **Transaction or DeviceProfile attributes** if loaded; they are not separate vertex types. Meanings except the README-named readable ids: **UNKNOWN — MUST VERIFY** (unnamed).

---

## TigerGraph edges

| Edge (suggested) | From → To | Dataset basis | Status |
| --- | --- | --- | --- |
| `OWNS` | `Customer` → `Card` | README: customer has several cards; both ids on closed cases and case pack | **Need a verified card–customer pairing on every transaction. UNKNOWN — MUST VERIFY** if transactions lack `card_id` |
| `MADE` | `Card` → `Transaction` | Suggested; card performs txn | **Requires Card id on each txn. UNKNOWN — MUST VERIFY** |
| `FROM_DEVICE` | `Transaction` → `DeviceProfile` | `identity.csv` join on `TransactionID`; online only | README-stated join. **DeviceProfile key UNKNOWN — MUST VERIFY** |
| `PURCHASER_EMAIL` | `Transaction` → `EmailDomain` | `P_emaildomain` | README suggested |
| *(unnamed in suggested schema)* | Transaction → email via `R_emaildomain` | Column exists (“recipient email domain”); policy R6 mentions same recipient email | **No suggested edge name. UNKNOWN — MUST VERIFY** whether to add e.g. `RECIPIENT_EMAIL` |
| `BILLED_IN` | `Transaction` → `BillingRegion` | `addr1` | README suggested |
| `NEXT` | `Transaction` → `Transaction` | Order by `ts` **within a card** | README suggested. **Card grain UNKNOWN — MUST VERIFY.** Tie-breaking when `ts` equal: **UNKNOWN — MUST VERIFY** |
| `INVOLVES` | `ClosedCase` → `Transaction` | `txn_ids` (pipe-separated) and `first_fraud_txn_id` | Parse list; **format UNKNOWN — MUST VERIFY** |
| `ON_CARD` | `ClosedCase` → `Card` | `card_id` | README suggested |
| `CONNECTED_TO` | `ClosedCase` → `Card` | `connected_card_ids` | **Delimiter/format UNKNOWN — MUST VERIFY** (not stated as pipe; `txn_ids` is) |
| *(write-back, not in suggested list)* | `Case` → Transaction / Card / Customer / DeviceProfile / ClosedCase | Answer `affected_txn_ids`, `connected_card_ids`, `similar_prior_cases`, etc. | Required by “write the case into the graph.” **Edge type names not specified. UNKNOWN — MUST VERIFY** engineering choice vs reusing `INVOLVES` / `ON_CARD` |

**Do not add** shared-device or shared-region edges as **base load** unless derived by a named GSQL query at investigation time. README says those shares are **worth looking at**; it does not define a pre-materialized `SHARES_DEVICE` edge.

---

## Case objects

Two different “case” concepts in the README. Map both; do not collapse them.

### A. Historical `ClosedCase` (input)

| Case-object field | CSV column |
| --- | --- |
| id | `case_id` |
| customer | `customer_id` |
| card | `card_id` |
| times | `opened_at`, `closed_at` |
| outcome | `outcome` |
| pattern | `pattern` |
| episode txns | `txn_ids`, `first_fraud_txn_id`, `n_txns` |
| exposure | `exposure_usd` |
| connected cards | `connected_card_ids` |
| actions / SAR flag | `actions_taken`, `report_filed` |
| narrative memory | `analyst_notes` |

Cite these IDs in answer `similar_prior_cases`.

### B. Investigation `case` (output + graph write-back)

Produced per exam `HHG-*` (and optionally extra alerts). Must match answer-format `case` and policy 3a (`CREATE_CASE`).

| Answer / runtime field | Dataset input used | Graph |
| --- | --- | --- |
| `case_id` | `case_pack.case_id` | attribute on `Case` (exam id, not necessarily vertex PK) |
| `status`, `verdict`, `fraud_probability` | **Not in CSVs.** Agent + policy | attributes |
| `pattern`, `pattern_description` | Graph evidence vs README pattern section; history `pattern` as memory only | attributes |
| `affected_txn_ids`, `first_suspicious_txn_id` | Investigation over `Transaction` neighborhood; seed `flagged_txn_id` | edges to `Transaction` |
| `connected_card_ids` | Shared device/region/email queries; history analog `connected_card_ids` | edges to `Card` |
| `connected_device_profiles` | `DeviceProfile` vertices / concatenated strings | edges or string list |
| `exposure_usd` | Sum of abs(`TransactionAmt`) of affected ids (policy §4) | attribute |
| `evidence` | See Evidence objects | stored with refs |
| `similar_prior_cases` | Retrieved `ClosedCase` ids | edges to `ClosedCase` |
| `summary` | Agent text | attribute |
| `written_to_graph`, `graph_case_id` | Write-back result | vertex id |

**Intake fields from `case_pack.csv` (not all copied into the answer `case` object, but they start the investigation):** `opened_at`, `trigger_type`, `trigger_text`, `flagged_txn_id`, `card_id`, `customer_id`, pack `risk_score`.

**Customer replies:** not in the dataset. They become `evidence_requests[].assumed_response` and may change `next_best_actions.final`. They are not vertices.

---

## Evidence objects

Answer format: list of `{ claim, source, ref, entity_ids }`.

| `source` | Maps from | `ref` (README) | `entity_ids` |
| --- | --- | --- | --- |
| `graph` | Installed GSQL / algorithm results on vertices and edges above | Query name + params (example style `query:card_window(...)` is **illustrative only**, not a required query catalog) | Transaction / card / closed-case / device ids that exist in the dataset |
| `document` | GraphRAG hits (policy, patterns, regs, closed-case notes) | Document section id | ids mentioned in the chunk if any |
| `customer` | Simulated validation / step-up | `evidence_request:N` | often `[]` |
| `external` | **No external dataset files.** Only if policy/docs retrieved or team-added data (README allows extending) | **UNKNOWN — MUST VERIFY** what judges accept besides provided data | dataset ids only in the scored answer |

**Unnamed V/C/D/M/`id_*` features:** allowed as signals if present on `Transaction` / identity attributes; `claim` must say the column is unnamed. Do not map them to invented relationship types.

**Risk score:** input attribute on `Transaction` / trigger; **not** a verdict and not a substitute for graph evidence.

---

## GraphRAG documents

README: load closed-case narratives, the README pattern section, the policy, and useful regulatory documents into TigerGraph vector search.

| Document set | Source | Suggested doc id / metadata | Retrievable for |
| --- | --- | --- | --- |
| Closed-case notes | `closed_cases_history.csv` `analyst_notes` (+ structured fields in text or as metadata) | `case_id` | `similar_prior_cases`, typology, false-alarm reasons |
| Known fraud patterns | README “The five known fraud patterns” | e.g. `pattern:card_testing` … | pattern classification language |
| Fraud policy | README `# Fraud Policy` including R1–R10, actions, routes, 3a/3b, stop rules | `policy:R1` … `policy:R10`, `policy:actions` | NBA `reason` citations |
| Answer / glossary constraints | README answer format + “Things to know” | optional chunks | calibration, half-legitimate, simulate evidence |
| Regulatory | FinCEN / FATF / FFIEC / OFAC **URLs** in README | URL or filename if downloaded | `sar.narrative` style; **files not in `data/raw/`** |
| Written-back investigations | `Case` vertex / notes after close | `graph_case_id` | later case memory (exam + optional extra cases) |

**Hybrid retrieval:** structural GSQL (neighbors, windows, shares) **plus** vector search over these texts. GraphRAG must return citations (`document` evidence `ref`).

**Embedding fields / index names in TigerGraph:** **UNKNOWN — MUST VERIFY** (not in the dataset README; product configuration).

---

## Exam pack → graph walk (no extra relationships)

For each `HHG-*`:

1. Read `flagged_txn_id`, `card_id`, `customer_id`, `trigger_type`, `trigger_text`.  
2. Locate `Transaction` by `TransactionID` **once ID format is verified**.  
3. Traverse **only** suggested edges: card history (`MADE`, `NEXT`), device (`FROM_DEVICE`), purchaser email, billing region, customer other cards (`OWNS`), closed cases (`ON_CARD`, `INVOLVES`, `CONNECTED_TO`).  
4. Shared-device / shared-region / shared-recipient **findings** come from **queries over those edges**, not from invented link types.  
5. Retrieve GraphRAG docs; attach as `document` evidence.  
6. Apply policy deterministically; write `Case` + answer JSON.

---

## Explicit non-mappings

| Item | Why not mapped |
| --- | --- |
| Public IEEE-CIS fraud labels | Disallowed; labels removed from this edition |
| `fraud_probability` column | Does not exist; agent output |
| Customer/analyst reply CSV | Specified as not provided |
| Merchant vertex | Not in suggested schema; no merchant id named |
| Query names `card_window` / `device_neighbors` | Example JSON only, not dataset schema |

---

## Blocked until `data/raw/` exists

Re-verify before implementing GSQL:

- Header names and `card_id` on transactions  
- `TransactionID` string form vs case-pack `flagged_txn_id`  
- DeviceProfile primary key  
- `connected_card_ids` delimiter  
- Referential integrity of history `txn_ids` to `TransactionID`
