# Re-validation of 2026-11-24 (evening): failures and fixes

Run: `efficient_corporate_travel_agent/pilot/ladder/runs/revalidation_2026-11-24/`, `thornton-tomasetti-flight-policy@v2`,
at b0a8994. 23 scored runs (`linden-spire` got a provider 429 and was not scored): 18/23 valid (78.3%), easy 5/5,
mean field score 0.906, 0/23 over the hosted 65,536 cap. The morning's classifications are in
`pilot/ladder/runs/validation_2026-11-24/VALIDATION.md`; recurring ones are checked again below, not redone.

## Approver amendment (template SYNC_NOTES 4')

A BOOK or REFUSE that rests on a sign-off already on file now accepts that role and `NONE`. In `rules.solve`
(and the byte-identical `verifier/rules.py`) every non-hold key whose approvers are not just `NONE` gains `NONE`.
Holds still accept only the awaited role; `linden-spire` keeps `MANAGING_PRINCIPAL` only (the Office Director
whose sign-off is on file is the invalid giver the case tests). The unused-sign-off rule 4(b) is unchanged.

Scenarios whose key changed (approvers only, no world change): `juniper-anvil`, `umber-skiff` (`SUPERVISOR` or
`NONE`), `basalt-ferry`, `garnet-harbor` (`MANAGING_PRINCIPAL` or `NONE`). `MAX_PASS_ALWAYS_LOWEST` stays **4**
(measured): the four changed cases book business, which the always-cheapest agent never picks.

## Every failure, classified

| scenario | category | submitted vs key | class | evidence | fix |
|---|---|---|---|---|---|
| umber-skiff | multi_rule | approver NONE; key SUPERVISOR (rest right) | approver rule alone | "approver: NONE (the sign-off is on file already; this decision relies on no one's further sign-off)". Same reading as this morning. | 4' (NONE accepted) |
| ember-trellis | flag | BOOK nonstop, ALTERNATE_ROUTE_WITHIN_MARGIN; key FLAG / UNCLEAR_POLICY_TEXT / NOT_NAMED | model slip (recurs, settled) | Again "125% of $412 = $515, so the Delta nonstop at $514 is within that margin" without weighing the $100 reading of lines 239-240 ($102 more). | none |
| hazel-compass | boundary_twin | BOOK morning-premium, PREMIUM_ECONOMY_ALLOWED; key morning-economy, UPGRADE_NOT_ELIGIBLE | model slip (recurs, settled) | "A 6-hour flight - is it 'in excess of 6 hours'? ... 6h00 is not longer", then books premium because the upgrade is $18 and "the reason code list includes PREMIUM_ECONOMY_ALLOWED". Lines 211-213 need a flight in excess of 6 hours or overnight. | none |
| velvet-prairie | flag | BOOK coach, UPGRADE_COST_NOT_NOMINAL; key FLAG evening-premium, UNCLEAR_POLICY_TEXT | model slip (recurs, settled) | "$189 on $640 is ~30%. Not nominal", one reading of "deemed nominal" (line 213) taken as clear. | none |
| yarrow-mosaic | boundary_twin | reason LOWEST_FARE; key LONG_FLIGHT_CONDITION_NOT_MET or UPGRADE_NOT_ELIGIBLE (offer, cabin, approver, clause right) | model slip (borderline) | The reasoning finds the case: "480 minutes = exactly 8 hours ... not in excess" (line 229) and "LONG_FLIGHT_CONDITION_NOT_MET ... suggests a case where the long flight condition is not met", and its final message gives that as the reason, but it submits LOWEST_FARE. | none (see below) |

`yarrow-mosaic` was weighed against the `kestrel-loom` precedent (LOWEST_FARE accepted because line 239 says "book
the lowest logical airfare"). Line 208 ("always purchase the lowest fare available with the following possible
exceptions") would support the same for every refused upgrade, but in this handbook the reason code is the only
field that separates "weighed the requested upgrade and refused it" from "ignored the request": accepting
LOWEST_FARE on the five refused-upgrade cases (`dune-orchard`, `hazel-compass`, `yarrow-mosaic`, `quartz-hollow`,
`indigo-meadow`) would let the always-cheapest agent pass them and raise its count from 4 to 9 of 24. The key
already accepts both codes that name the failed condition, and the model named it itself, so this is not
loosened. The lead may decide otherwise; the change would be one line in each of the three refused-upgrade
branches of `rules.business` and `rules.premium`.

No scenario or grader defect was found. Expected after the fix on the same answers: 19/23 valid.

## Checks

`uv run pytest -q` (209 passed), `uv run ruff check .`, `uv lock --check`, `python3 ../_template/check_shared.py .`
(ok), `tools/stock_verify.py` with the NanoAgent venv (24 scenarios, 0 failures). `world.py` and every scenario
world are unchanged, so `world_diff.py` has nothing to report.
