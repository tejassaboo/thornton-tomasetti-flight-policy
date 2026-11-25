# Validation notes: thornton-tomasetti-flight-policy (paid wave 1 validation w1v3, 2026-11-25)

Run: `efficient_corporate_travel_agent/pilot/ladder/runs/validation_w1v3_2026-11-25/thornton-tomasetti-flight-policy@w1v3/`,
arm `full`, DeepSeek V4 Flash, temperature 0, max_steps 6, max_tokens 8192, one run per scenario, at plugin head
4b81038 (after the approver rule 4' and the declined-request sentence). Line numbers are lines of
`src/plugin/data/policy.txt`.

## Results

20/24 valid (83.3%), **easy 5/5**. By category: boundary 5/6, distractor 2/2, easy 5/5, flag 0/3, hidden 2/2,
multi 4/4, refusal 2/2. Re-scoring the stored submissions under this commit's verifier (no paid call) gives
**20/24, easy 5/5**: no failure was a grader defect, and velvet-prairie's record changed, so its stored answer
cannot be re-scored and it needs a paid re-run.

## Every failure, classified

| scenario | category | submitted vs key | class | evidence |
|---|---|---|---|---|
| dune-orchard | boundary_twin | BOOK American business 6F3E-XZLU ($1,628.01), UPGRADE_WITHIN_FARE_MARGIN; key economy VCKT-EG73, UPGRADE_NOT_ELIGIBLE | model slip (arithmetic) | It found the right test (line 217) and the right base ($1,480, the lowest fare) and computed the limit itself: "1480 * 1.10 = 1628. So it's exactly 10%, which does not exceed 10%" for a fare of $1,628.01. One cent over is the designed boundary; the twin nutmeg-bridge ($1,628.00) is the BOOK side. The text is clear ("does not exceed ... by more than 10%"). |
| ember-trellis | flag | BOOK Delta nonstop H3VV-ECE4, ALTERNATE_ROUTE_WITHIN_MARGIN; key FLAG the nonstop, UNCLEAR_POLICY_TEXT | model slip (recurs) | It computed both tests ("$514 is within 125% ... $102, which exceeds $100") and wrote "This is ambiguous ... I interpret as ... either threshold", then booked. Lines 239-240 do not say whether one test or both must pass; it saw the open question and settled it. Third run with the same answer; the twins saffron-wharf and kestrel-loom passed. |
| linden-spire | flag | BOOK BA economy BUHJ-P3LG, UPGRADE_NOT_ELIGIBLE; key FLAG business for MANAGING_PRINCIPAL, APPROVAL_REQUIRED | model slip | First scored run (the 2026-11-24 run got a 429). It found that the Office Director is not the Managing Principal the long-flight condition needs (lines 226-233), weighed "maybe we should flag for approval to get the correct approver (Managing Principal/VP)", and booked economy instead. Every other condition holds (client meeting, rest on arrival, extra fare judged reasonable), so the business ticket waits for a sign-off the handbook lets the Managing Principal give; the task's FLAG wording is exactly this case. The twins basalt-ferry (valid sign-off) and yarrow-mosaic (480 minutes) passed. |
| velvet-prairie | flag | BOOK Virgin economy 5DF7-U5F7, UPGRADE_COST_NOT_NOMINAL; key FLAG evening-premium, UNCLEAR_POLICY_TEXT | **scenario defect (weak flag)** | "The upgrade is $189, which is about 29.5% of the coach fare. That doesn't seem nominal." Third run in a row with this answer (11-24 morning and evening notes called it a slip). The verifier's own window puts "clearly not nominal" at $250 and 30%; $189 at 29.5% sits on that edge, and in ordinary usage "nominal" (line 212) means token, which 30% is not. A careful reader books coach here, so the hold does not test an open phrase. The flag should sit in the middle of the window. |

## Fixes (this commit)

`src/plugin/rules.py` and the byte-identical `verifier/rules.py`, scenario JSON (the JSON files are the source of
truth here; `test_scenarios.py` checks that every hand-written key equals what the rules compute), README rows.
No id, decision or category changed.

1. **velvet-prairie (record):** the evening premium-economy fare is now $704 (was $829): $64 on the $640 coach
   fare, 10%, between clearly nominal ($25 and 3%) and clearly not ($250 and 30%). The key is unchanged (hold the
   premium seat, UNCLEAR_POLICY_TEXT, NOT_NAMED); the ambiguity readings, design note and `twin_fact` (also on
   indigo-meadow, metadata only) say so. **Needs a paid re-run.**
2. **Long-flight business (basalt-ferry, garnet-harbor; cross-plugin consistency from wave 2):**
   `INTERNATIONAL_LONG_FLIGHT` accepted beside `LONG_FLIGHT_APPROVED` when the flight is international (origin and
   destination countries differ). Both cases are international (London-New York 481 minutes, New York-Dubai 760),
   so either code describes the ground. A domestic long flight would still accept only `LONG_FLIGHT_APPROVED`: lines
   226-233 are a flight-length rule, not an international one. Both cases passed in this run.

Not changed:

- **kestrel-loom (route codes):** keeps `ALTERNATE_ROUTE_TOO_EXPENSIVE` and `LOWEST_FARE`. In lines 239-240 the
  "alternate connection or direct route" is the route dearer than the lowest logical airfare, here the declined
  nonstop, which fails both tests ($520 against $412: 126% and $108 more). `ALTERNATE_ROUTE_WITHIN_MARGIN` would
  state the opposite of the case, and it is the twin saffron-wharf's code for booking a nonstop that passes.
  Unlike FedEx and Hill-Rom, whose texts make the connection the alternate under a savings test, it does not
  describe this ground. kestrel-loom passed in this run.
- saffron-wharf (nonstop asked for and booked within the margin) and marble-canopy (business on cost savings,
  lines 220-222) decline nothing on a route ground and need nothing.
- Not loosened: dune-orchard, ember-trellis, linden-spire.

## Q2

The always-cheapest agent books the cheapest seat with `LOWEST_FARE`. Neither fix adds an economy offer or
`LOWEST_FARE`, so its count is unchanged: **4/24 (17%)** (amber-quay, kestrel-loom, opal-thicket, willow-beacon;
`MAX_PASS_ALWAYS_LOWEST = 4`).

## Re-run

Required: **velvet-prairie** (record changed). Optional: linden-spire (first scored run), dune-orchard.

## Checks

`uv run pytest -q` (209 passed), `uv run ruff check .`, `uv lock --check`, `check_shared.py`,
`tools/stock_verify.py` (0 failures), stock `nanoagent plugin inspect .` (exit 0).
