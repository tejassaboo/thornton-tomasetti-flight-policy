# Thornton Tomasetti Flight Policy

**No affiliation with Thornton Tomasetti.** The handbook is the firm's public *Travel and Business Expense
Policy* (October 2019), bundled verbatim for research. Do not publish this plugin before the course staff
confirm that a verbatim corporate handbook may be redistributed.

A `nanoagent.plugin/v0001` plugin. An agent handles one traveller's flight request under the firm's real
travel handbook: it reads the trip record, searches a simulated flight world and submits **BOOK**,
**REFUSE** or **FLAG_FOR_APPROVAL** with the offer, cabin, reason, approver and handbook section. A
deterministic Python verifier, with no LLM, rebuilds the offers and the handbook's answer itself and checks
every field.

## The handbook and the harness flag

The frozen text (`src/plugin/data/policy.txt`, 4,141 words, sha256 `adc0e820...29e2`) is never
paraphrased, and the task text restates no rule. Under stock NanoAgent the agent does not see it: the
plugin then runs as the `off` baseline. The `harness.policy` switch of the NanoAgent fork
(github.com/tejassaboo/nanoagent, branch `policy-switch`) adds it to the system prompt:
`harness.policy: full` adds all of it, and the selection methods add parts of it. These plugins are meant
to run with `query: instructions+input`, so a selector sees the traveller's request.

## Task

- **Input:** `TaskInput`: `scenario` (one of 24 case ids) and `request`, the traveller's own words.
- **Steps:** `get_trip`, then `search_flights` on the trip's route and date, then `submit` (3 of the 6 hosted steps).
- **Output:** `BookingOutput`: `decision`, `offer_id` (empty when refusing), `cabin` (`NONE` when
  refusing), `reason_code`, `approver` and `clause`, each from a closed list. The reason list is shared by
  every handbook plugin and holds codes for rules this handbook lacks, plus decoy codes from other handbooks'
  rules. The approver is the role whose sign-off the decision relies on, on file or awaited (`SUPERVISOR` in
  `juniper-anvil` and `umber-skiff`); `NONE` when it relies on none, and where a sign-off on file goes unused
  (`quartz-hollow`, `yarrow-mosaic`) that role is accepted beside `NONE`; `NOT_NAMED` is the approver when a
  sign-off is needed but the handbook names nobody.
- **Success:** every field is one the answer key accepts. Score = fields right / 6.

| Scenario | Category | Expected decision (offer) | Reason | Approver | Clause cited (frozen lines) |
|---|---|---|---|---|---|
| `amber-quay` | easy | BOOK (mid-economy, ECONOMY) | LOWEST_FARE | NONE | AIR_CLASS or AIR_ROUTE (208-209, 239-240) |
| `fjord-pebble` | easy | BOOK (eve-business, BUSINESS) | CLIENT_REIMBURSABLE | NONE | AIR_CLASS (215, 216) |
| `juniper-anvil` | easy | BOOK (am-business, BUSINESS) | MEDICAL_NEED | SUPERVISOR | AIR_CLASS (215, 218-219) |
| `opal-thicket` | easy | BOOK (red-economy, ECONOMY) | LOWEST_FARE | NONE | AIR_CLASS or AIR_ROUTE (208-209, 239-240) |
| `willow-beacon` | easy | BOOK (noon-economy, ECONOMY) | LOWEST_FARE | NONE | AIR_CLASS or AIR_ROUTE (208-209, 239-240) |
| `basalt-ferry` | boundary_twin | BOOK (noon-business, BUSINESS) | LONG_FLIGHT_APPROVED | MANAGING_PRINCIPAL | AIR_CLASS (215, 226-233) |
| `dune-orchard` | boundary_twin | BOOK (first-economy, ECONOMY) | UPGRADE_NOT_ELIGIBLE | NONE | AIR_CLASS (215, 217, 208-209) |
| `hazel-compass` | boundary_twin | BOOK (morning-economy, ECONOMY) | UPGRADE_NOT_ELIGIBLE | NONE | AIR_CLASS (211-213, 208-209) |
| `nutmeg-bridge` | boundary_twin | BOOK (first-business, BUSINESS) | UPGRADE_WITHIN_FARE_MARGIN | NONE | AIR_CLASS (215, 217) |
| `russet-glade` | boundary_twin | BOOK (morning-premium, PREMIUM_ECONOMY) | PREMIUM_ECONOMY_ALLOWED | NONE | AIR_CLASS (211-213) |
| `yarrow-mosaic` | boundary_twin | BOOK (noon-economy, ECONOMY) | LONG_FLIGHT_CONDITION_NOT_MET or UPGRADE_NOT_ELIGIBLE | MANAGING_PRINCIPAL or NONE | AIR_CLASS (215, 226-233, 208-209) |
| `garnet-harbor` | multi_rule | BOOK (day-business, BUSINESS) | LONG_FLIGHT_APPROVED | MANAGING_PRINCIPAL | AIR_CLASS (215, 226-233) |
| `marble-canopy` | multi_rule | BOOK (early-business, BUSINESS) | COST_SAVINGS | NONE | AIR_CLASS (215, 220-222) |
| `quartz-hollow` | multi_rule | BOOK (day-economy, ECONOMY) | LONG_FLIGHT_CONDITION_NOT_MET or UPGRADE_NOT_ELIGIBLE | MANAGING_PRINCIPAL or NONE | AIR_CLASS (215, 226-233, 208-209) |
| `umber-skiff` | multi_rule | BOOK (first-business, BUSINESS) | NO_ECONOMY_SEATS_URGENT | SUPERVISOR | AIR_CLASS (215, 223-224) |
| `indigo-meadow` | hidden_clause | BOOK (evening-economy, ECONOMY) | UPGRADE_COST_NOT_NOMINAL or UPGRADE_NOT_ELIGIBLE | NONE | AIR_CLASS (211-213, 208-209) |
| `timber-cairn` | hidden_clause | BOOK (am-business, BUSINESS) | TRAVELER_PAYS_UPGRADE | NONE | AIR_CLASS (215, 225) |
| `kestrel-loom` | distractor | BOOK (dallas-economy, ECONOMY) | ALTERNATE_ROUTE_TOO_EXPENSIVE or LOWEST_FARE | NONE | AIR_ROUTE (239-240) |
| `saffron-wharf` | distractor | BOOK (direct-economy, ECONOMY) | ALTERNATE_ROUTE_WITHIN_MARGIN | NONE | AIR_ROUTE (239-240) |
| `cedar-lantern` | refusal | REFUSE (none, NONE) | PERSONAL_TRAVEL_NOT_COVERED | NONE | NOT_REIMBURSABLE or PERSONAL_TRAVEL (556, 571) |
| `pewter-delta` | refusal | REFUSE (none, NONE) | COMPANION_NOT_COVERED | NONE | PERSONAL_TRAVEL or NOT_REIMBURSABLE (459-461, 556, 570) |
| `ember-trellis` | flag | FLAG_FOR_APPROVAL (direct-economy, ECONOMY) | UNCLEAR_POLICY_TEXT | NOT_NAMED | AIR_ROUTE (239-240) |
| `linden-spire` | flag | FLAG_FOR_APPROVAL (noon-business, BUSINESS) | APPROVAL_REQUIRED | MANAGING_PRINCIPAL | AIR_CLASS (215, 226-233) |
| `velvet-prairie` | flag | FLAG_FOR_APPROVAL (evening-premium, PREMIUM_ECONOMY) | UNCLEAR_POLICY_TEXT | NOT_NAMED | AIR_CLASS (211-213) |

Mix (EDGE_CASES.md 5.2): 5 easy, 6 boundary twins, 4 multi-rule, 2 hidden clause or synonym, 2 distractor, 2
refusal, 3 flags (12.5%, the 15% cap is 3). Unclear words are each one flag with clear twins on both sides:
"125% or $100" (`ember-trellis`, twins `saffron-wharf` and `kestrel-loom`) and "nominal"
(`velvet-prairie`, twins `russet-glade` and `indigo-meadow`). `linden-spire` is an approval-required
hold, which is never the same as "no compliant offer".

## Tools

| Tool | Does | Code |
|---|---|---|
| `booking_requirements` | The trip record's fields, the world's conventions (local times, dates, fares, sold-out seats) and its airports | `src/plugin/guide.py` |
| `get_trip` | A case's request and trip record: traveller, route, dates, purpose, requested cabin and routing, sign-offs, earlier flights | `src/plugin/tools.py` |
| `search_flights` | Every offer on a route and local date (one way, or round trip with `return_date`): the pinned scenario offers plus seeded background offers on those searches only; a search the case does not pin lists nothing and says so | `src/plugin/world.py` |
| `solve_booking` | The answer key (`rules.solve`), the agent task's `reference`, never shown to the agent | `src/plugin/rules.py` |

| Task | Does | Runner |
|---|---|---|
| `book-thornton-tomasetti-flight` | Handles one booking request | `agent`, with `get_trip` and `search_flights`; reference `solve_booking` |
| `booking-requirements` | Shows `booking_requirements` | `tool` |
| `search-flights` | Shows `search_flights` | `tool` |

## Layout

- `contract.py`: the template's shared contract plus this handbook's scenario ids, approvers, sections and trip record.
- `src/plugin/`: `world.py` (the simulated world: real airports and airline hubs, distance-based times
  and fares, hash-seeded background offers and opaque offer ids), `scenarios.py`, `guide.py`,
  `answer.py`, `tools.py`, `rules.py` (this handbook's rules, citing frozen lines), `__main__.py`.
- `src/plugin/data/`: `policy.txt` (frozen), `handbook.json`, `scenarios/*.json`.
- `verifier/`: byte-identical copies of `world.py`, `scenarios.py`, `guide.py`, `answer.py` and
  `rules.py`, plus `booking.py` (`verify_task`) and `tools.py` (`verify_input`, `verify_output`).
- `tests/`: the template's acceptance suite; `tests/plugin_spec.py` holds this handbook's settings.

## Develop and run

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv lock --check
# from a NanoAgent checkout:
nanoagent plugin inspect <this folder>
```

Offline: `hosts: []`, an empty `.env`, `write: []`, no clock (each case fixes its `booking_date`).
