"""The answer key's rules for the Thornton Tomasetti Travel and Business Expense Policy (October 2019), as
exact integer code. Byte-identical in src/plugin/rules.py and verifier/rules.py; it imports only modules a
verifier may use.

Every rule cites the frozen handbook text (src/plugin/data/policy.txt) by line. Where the text leaves an
answer open, the rule returns FLAG_FOR_APPROVAL with the unclear words, and a scenario may depend on each
unclear phrase at most once (tests/test_scenarios.py). Combinations no scenario needs raise ValueError, so a
new scenario cannot fall silently into untested logic.

The duration hook. This handbook measures "flights in excess of 6 hours" (line 211) and "The scheduled time
of the flight is in excess of 8 hours" (line 229) per flight: a nonstop is over the limit when its
scheduled minutes exceed it. For a connection, "the flight" may mean one segment or the journey: when any
segment is over the limit every reading agrees (over); when the whole elapsed journey is within the limit
every reading agrees (not over); otherwise the reading is unclear.
"""

from contract import Approver, Cabin, Clause, Decision, Passenger, Purpose, ReasonCode, Routing, SignOffSubject

from .world import clock_minutes, days_between

HANDBOOK = "Thornton Tomasetti, Travel and Business Expense Policy, October 2019"

# Each closed-list section and the heading it names in the frozen text (tests check every heading is there).
CLAUSE_HEADINGS = {
    Clause.SCOPE: "Scope of Policy",
    Clause.RESPONSIBILITIES: "Employee Responsibilities:",
    Clause.ARRANGEMENTS: "2. MAKING TRAVEL ARRANGEMENTS",
    Clause.AIR_CLASS: "Airline Class of Service",
    Clause.AIR_ROUTE: "Airline Route",
    Clause.STANDBY: "Standby Charges",
    Clause.FREQUENT_FLYER: "Airline Frequent Flyer Programs",
    Clause.CANCELLATIONS: "Cancellations or Unused Airline Tickets",
    Clause.LODGING: "4. LODGING",
    Clause.RENTAL_CAR: "5. RENTAL CAR",
    Clause.RAIL: "6. RAIL TRAVEL",
    Clause.MEALS: "7. MEALS AND ENTERTAINMENT",
    Clause.CREDIT_CARD: "8. CREDIT CARD EXPENSES",
    Clause.PERSONAL_TRAVEL: "9. PERSONAL/VACATION TRAVEL",
    Clause.WORKING_LATE: "10. WORKING LATE/WEEKENDS: TRANSPORTATION",
    Clause.EXPENSE_REPORTS: "11. EXPENSE REPORTS",
    Clause.NOT_REIMBURSABLE: "Items That Are Typically Not Reimbursable",
}

# The handbook's duration thresholds (the per-handbook duration hook; tests/test_duration.py tests both
# sides of each). operator ">" is strict ("in excess of").
DURATION_RULES = (
    {"name": "premium-economy", "minutes": 360, "operator": ">", "lines": [211, 213],
     "quote": "flights in excess of 6 hours"},
    {"name": "long-flight", "minutes": 480, "operator": ">", "lines": [229, 229],
     "quote": "The scheduled time of the flight is in excess of 8 hours"},
)
LIMITS = {rule["name"]: rule["minutes"] for rule in DURATION_RULES}

# Handbook-specific conventions shown by booking_requirements, beyond the template's (none here).
CONVENTIONS = ()

# Fare windows, in integer arithmetic.
UPGRADE_MARGIN_PERCENT = 110  # line 217: "does not exceed the lowest priced fare by more than 10%"
ROUTE_PERCENT = 125  # line 240: "does not exceed 125% or $100 of the lowest airfare"
ROUTE_CENTS = 10_000
# "nominal" (line 212) is not defined. Clearly nominal: at most $25 and at most 3% of the coach fare.
# Clearly not nominal: at least $250 and at least 30%. Anything between is the unclear phrase.
NOMINAL_CENTS, NOMINAL_PERCENT = 2_500, 3
NOT_NOMINAL_CENTS, NOT_NOMINAL_PERCENT = 25_000, 30
# "at least once in the past 30 days" (lines 232-233): clearly inside when the earlier flight left at most
# 29 days before the travel date; clearly outside when it left at least 31 days before the booking date.
RECENT_INSIDE_DAYS, RECENT_OUTSIDE_DAYS = 29, 31


def over(rule, offer):
    """True, False or None (unclear): whether ``offer`` is over the handbook's ``rule`` duration."""
    limit = LIMITS[rule]
    if any(segment.scheduled_minutes > limit for segment in offer.segments):
        return True
    if offer.elapsed_minutes <= limit:
        return False
    return None


def overnight(offer):
    """True, False or None (unclear) for "overnight flights" (line 212), which the handbook does not define.
    A flight is clearly overnight when it leaves at 20:00 local time or later and lands on a later local
    date by 11:00; clearly not when it leaves at 05:00 or later and lands later the same local date by 21:00."""
    verdicts = []
    for segment in offer.segments:
        leave_day, leave = segment.depart_local[:10], clock_minutes(segment.depart_local[11:])
        land_day, land = segment.arrive_local[:10], clock_minutes(segment.arrive_local[11:])
        dates = days_between(leave_day, land_day)
        if dates >= 1 and leave >= 20 * 60 and land <= 11 * 60:
            verdicts.append(True)
        elif dates == 0 and 5 * 60 <= leave < land <= 21 * 60:
            verdicts.append(False)
        else:
            verdicts.append(None)
    if True in verdicts:
        return True
    if all(verdict is False for verdict in verdicts):
        return False
    return None


def flew_long_lately(trip):
    """True, False or None (unclear): whether the traveller "has traveled on flights of this length at
    least once in the past 30 days" (lines 232-233), "this length" being over the long-flight limit."""
    unclear = False
    for flight in trip.recent_flights:
        if flight.scheduled_minutes <= LIMITS["long-flight"]:
            continue
        before_travel = days_between(flight.date, trip.travel_date)
        before_booking = days_between(flight.date, trip.booking_date)
        if before_booking < 0:
            raise ValueError("an earlier flight on file leaves after the booking date")
        if before_travel <= RECENT_INSIDE_DAYS:
            return True
        if before_booking >= RECENT_OUTSIDE_DAYS:
            continue
        unclear = True
    return None if unclear else False


def sign_off(trip, role):
    for record in trip.sign_offs:
        if record.role == role and record.subject == SignOffSubject.CABIN_UPGRADE:
            return record
    return None


def by_value(items):
    return sorted(set(items), key=lambda item: item.value)


def answer(decision, offers, reasons, approvers, clauses, why, phrase=""):
    return {
        "decision": decision,
        "offer_ids": sorted(offer.offer_id for offer in offers),
        "cabins": by_value(offer.cabin for offer in offers) or [Cabin.NONE],
        "reason_codes": by_value(reasons),
        "approvers": by_value(approvers),
        "clauses": by_value(clauses),
        "unclear_phrase": phrase,
        "explanation": why,
    }


def refuse(reason, clauses, why):
    return answer(Decision.REFUSE, [], [reason], [Approver.NONE], clauses, why)


def cheapest(offers):
    if not offers:
        return []
    low = min(offer.fare_cents for offer in offers)
    return [offer for offer in offers if offer.fare_cents == low]


def flights_of(offer):
    return tuple((segment.flight_number, segment.depart_utc) for segment in offer.segments)


def solve(trip, offers, hidden):
    """The answer key for one trip and the offers on its route and date: the decision, and every accepted
    offer id, cabin, reason, approver and section. ``hidden`` (the scenario's answer_key_inputs) is unused
    by this handbook."""
    if hidden:
        raise ValueError("this handbook's scenarios carry no answer_key_inputs")
    if trip.passenger == Passenger.SPOUSE_OR_FAMILY:
        return refuse(ReasonCode.COMPANION_NOT_COVERED, [Clause.PERSONAL_TRAVEL, Clause.NOT_REIMBURSABLE],
                      "Lines 459-461: a companion travels at the employee's expense; line 570 lists expenses "
                      "for travel companions/family members as not reimbursed.")
    if trip.purpose_kind == Purpose.PERSONAL:
        return refuse(ReasonCode.PERSONAL_TRAVEL_NOT_COVERED, [Clause.NOT_REIMBURSABLE, Clause.PERSONAL_TRAVEL],
                      "Line 571: expenses related to vacation or personal days while on a business trip are "
                      "not reimbursed.")
    bookable = [offer for offer in offers if offer.seats_available]
    lowest = cheapest(bookable)
    if not lowest:
        raise ValueError("no offer on the route and date can be bought")
    if trip.requested_routing == Routing.NONSTOP:
        return route(trip, bookable, lowest)
    if trip.requested_cabin == Cabin.ECONOMY:
        if any(offer.cabin != Cabin.ECONOMY for offer in lowest):
            raise ValueError("an economy request whose cheapest offer is not economy is not modelled")
        return answer(Decision.BOOK, lowest, [ReasonCode.LOWEST_FARE], [Approver.NONE],
                      [Clause.AIR_CLASS, Clause.AIR_ROUTE],
                      "Lines 208-209 and 239: book the lowest fare available.")
    if trip.requested_cabin == Cabin.PREMIUM_ECONOMY:
        return premium(bookable, lowest)
    if trip.requested_cabin == Cabin.BUSINESS:
        return business(trip, offers, bookable, lowest)
    raise ValueError(f"a {trip.requested_cabin.value} request is not modelled")


def route(trip, bookable, lowest):
    """Lines 239-240: the lowest logical airfare, unless an alternate connection or direct route "does not
    exceed 125% or $100 of the lowest airfare". Whether one test or both must pass is unclear, so a fare
    that passes exactly one is a flag."""
    if trip.requested_cabin != Cabin.ECONOMY:
        raise ValueError("a nonstop request in a cabin above economy is not modelled")
    low = lowest[0].fare_cents
    if any(offer.stops == 0 for offer in lowest):
        return answer(Decision.BOOK, [offer for offer in lowest if offer.stops == 0], [ReasonCode.LOWEST_FARE],
                      [Approver.NONE], [Clause.AIR_ROUTE, Clause.AIR_CLASS],
                      "The lowest fare is already a nonstop.")
    nonstops = cheapest([offer for offer in bookable if offer.stops == 0 and offer.cabin == Cabin.ECONOMY])
    if not nonstops:
        raise ValueError("a nonstop request with no nonstop economy offer is not modelled")
    fare = nonstops[0].fare_cents
    percent_ok = fare * 100 <= ROUTE_PERCENT * low
    dollars_ok = fare - low <= ROUTE_CENTS
    numbers = f"nonstop {fare} cents against lowest {low}: {fare * 100 / low:.1f}% and {fare - low} cents more"
    if percent_ok and dollars_ok:
        return answer(Decision.BOOK, nonstops, [ReasonCode.ALTERNATE_ROUTE_WITHIN_MARGIN], [Approver.NONE],
                      [Clause.AIR_ROUTE], f"Lines 239-240, both tests pass ({numbers}).")
    if not percent_ok and not dollars_ok:
        return answer(Decision.BOOK, lowest, [ReasonCode.ALTERNATE_ROUTE_TOO_EXPENSIVE], [Approver.NONE],
                      [Clause.AIR_ROUTE], f"Lines 239-240, both tests fail ({numbers}).")
    return answer(Decision.FLAG_FOR_APPROVAL, nonstops, [ReasonCode.UNCLEAR_POLICY_TEXT], [Approver.NOT_NAMED],
                  [Clause.AIR_ROUTE], f"Lines 239-240, exactly one test passes ({numbers}).",
                  phrase="does not exceed 125% or $100 of the lowest airfare")


def premium(bookable, lowest):
    """Lines 211-213: "Ecomomy Plus, Economy Premium or similar class may be purchased for flights in excess
    of 6 hours or overnight flights where the cost of the up grade is deemed nominal in terms of dollar
    amount or as a percentage of a Coach ticket.\""""
    wanted = cheapest([offer for offer in bookable if offer.cabin == Cabin.PREMIUM_ECONOMY])
    if len(wanted) != 1:
        raise ValueError("a premium economy request needs exactly one cheapest premium economy offer")
    offer = wanted[0]
    coach = cheapest([other for other in bookable
                      if other.cabin == Cabin.ECONOMY and flights_of(other) == flights_of(offer)])
    if not coach or coach[0].fare_cents != lowest[0].fare_cents:
        raise ValueError("premium economy must sit on the flights of the lowest coach fare")
    long, night = over("premium-economy", offer), overnight(offer)
    if long is not True and night is not True:
        if long is False and night is False:
            return answer(Decision.BOOK, lowest, [ReasonCode.UPGRADE_NOT_ELIGIBLE], [Approver.NONE],
                          [Clause.AIR_CLASS], "Lines 211-213: the flight is neither over the limit nor overnight.")
        return answer(Decision.FLAG_FOR_APPROVAL, wanted, [ReasonCode.UNCLEAR_POLICY_TEXT], [Approver.NOT_NAMED],
                      [Clause.AIR_CLASS], "Lines 211-213: whether this itinerary is over the limit or overnight "
                      "is unclear.", phrase="flights in excess of 6 hours or overnight flights")
    extra, base = offer.fare_cents - coach[0].fare_cents, coach[0].fare_cents
    numbers = f"upgrade {extra} cents on a {base}-cent coach fare ({extra * 100 / base:.1f}%)"
    if extra <= NOMINAL_CENTS and extra * 100 <= NOMINAL_PERCENT * base:
        return answer(Decision.BOOK, wanted, [ReasonCode.PREMIUM_ECONOMY_ALLOWED], [Approver.NONE],
                      [Clause.AIR_CLASS], f"Lines 211-213: eligible flight, clearly nominal {numbers}.")
    if extra >= NOT_NOMINAL_CENTS and extra * 100 >= NOT_NOMINAL_PERCENT * base:
        return answer(Decision.BOOK, lowest, [ReasonCode.UPGRADE_COST_NOT_NOMINAL], [Approver.NONE],
                      [Clause.AIR_CLASS], f"Lines 211-213: eligible flight, clearly not nominal {numbers}.")
    return answer(Decision.FLAG_FOR_APPROVAL, wanted, [ReasonCode.UNCLEAR_POLICY_TEXT], [Approver.NOT_NAMED],
                  [Clause.AIR_CLASS], f"Lines 211-213: eligible flight, \"nominal\" is not defined ({numbers}).",
                  phrase="deemed nominal")


def business(trip, offers, bookable, lowest):
    """Lines 215-233: "Business or similar class may be purchased under any of the following conditions"."""
    wanted = cheapest([offer for offer in bookable if offer.cabin == Cabin.BUSINESS])
    if not wanted:
        raise ValueError("a business request with no business offer is not modelled")
    fare, low = wanted[0].fare_cents, lowest[0].fare_cents
    listed_low = min(offer.fare_cents for offer in offers)  # "the lowest priced fare", sold out or not
    supervisor = sign_off(trip, Approver.SUPERVISOR)
    granted, pending, notes = [], [], []
    if trip.client_reimburses_trip:  # line 216
        granted.append((ReasonCode.CLIENT_REIMBURSABLE, Approver.NONE))
    if fare * 100 <= UPGRADE_MARGIN_PERCENT * listed_low:  # line 217
        granted.append((ReasonCode.UPGRADE_WITHIN_FARE_MARGIN, Approver.NONE))
    if trip.special_needs_on_file:  # lines 218-219, pre-approved by the supervisor
        if supervisor is not None:
            granted.append((ReasonCode.MEDICAL_NEED, Approver.SUPERVISOR))
        else:
            pending.append(Approver.SUPERVISOR)
    if trip.extra_costs_if_cheapest_cents > fare - low:  # lines 220-222
        granted.append((ReasonCode.COST_SAVINGS, Approver.NONE))
    economy_listed = [offer for offer in offers if offer.cabin == Cabin.ECONOMY]
    if economy_listed and not any(offer.seats_available for offer in economy_listed) and trip.urgent_cannot_postpone:
        if supervisor is not None:  # lines 223-224, pre-approved by the supervisor
            granted.append((ReasonCode.NO_ECONOMY_SEATS_URGENT, Approver.SUPERVISOR))
        else:
            pending.append(Approver.SUPERVISOR)
    if trip.traveller_pays_upgrade:  # line 225
        granted.append((ReasonCode.TRAVELER_PAYS_UPGRADE, Approver.NONE))
    # Lines 226-233: approved by the Managing Principal (or the Vice President in charge if a project cost),
    # where the upgrade's cost is not deemed excessive and the flight is over the limit and (a client meeting
    # needing rest, or a flight of this length at least once in the past 30 days).
    role = Approver.VICE_PRESIDENT if trip.project_cost else Approver.MANAGING_PRINCIPAL
    approval = sign_off(trip, role)
    lately = flew_long_lately(trip)
    need = (trip.purpose_kind == Purpose.CLIENT_MEETING and trip.rest_needed_on_arrival) or lately is True
    long_state = "failed"
    if need or lately is None:
        long = over("long-flight", wanted[0])
        if long is True and need:
            if approval is None:
                long_state = "pending"
            elif approval.extra_fare_judged_reasonable:
                long_state = "granted"
        elif long is None or (long is True and lately is None):
            long_state = "unclear"
    if long_state == "granted":
        granted.append((ReasonCode.LONG_FLIGHT_APPROVED, role))
    elif long_state == "pending":
        pending.append(role)
    if granted:
        notes = ", ".join(sorted(reason.value for reason, _ in granted))
        return answer(Decision.BOOK, wanted, [reason for reason, _ in granted], [who for _, who in granted],
                      [Clause.AIR_CLASS], f"Lines 215-233: business allowed ({notes}).")
    if long_state == "unclear":
        return answer(Decision.FLAG_FOR_APPROVAL, wanted, [ReasonCode.UNCLEAR_POLICY_TEXT], [Approver.NOT_NAMED],
                      [Clause.AIR_CLASS], "Lines 229-233: whether the long-flight condition holds is unclear.",
                      phrase="The scheduled time of the flight is in excess of 8 hours")
    if pending:
        return answer(Decision.FLAG_FOR_APPROVAL, wanted, [ReasonCode.APPROVAL_REQUIRED], pending,
                      [Clause.AIR_CLASS], "Lines 215-233: business needs a sign-off that is not on file.")
    reasons = [ReasonCode.UPGRADE_NOT_ELIGIBLE]
    if approval is not None:
        reasons.append(ReasonCode.LONG_FLIGHT_CONDITION_NOT_MET)
    return answer(Decision.BOOK, lowest, reasons, [Approver.NONE], [Clause.AIR_CLASS],
                  "Lines 207-233: no condition for business holds, so the lowest fare.")
