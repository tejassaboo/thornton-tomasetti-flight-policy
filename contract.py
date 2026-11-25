"""Each tool's and task's typed input and output (see nanoagent.plugin.v0001.contract): declarations only.

The first part is the original-handbook template's shared contract and is the same in every plugin made from
it. The HANDBOOK-SPECIFIC part in the middle is filled per handbook: the scenario ids, the closed lists of
approvers and sections, and the trip record; the shared inputs and outputs after it refer to those names.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output

# ---------------------------------------------------------------------------------------------------------
# SHARED (template): keep identical across plugins, except the agent task's id in Task.BOOK_FLIGHT.
# ---------------------------------------------------------------------------------------------------------


class Tool(Enum):
    BOOKING_REQUIREMENTS = "booking_requirements"
    GET_TRIP = "get_trip"
    SEARCH_FLIGHTS = "search_flights"
    SOLVE_BOOKING = "solve_booking"


class Task(Enum):
    BOOKING_REQUIREMENTS = "booking-requirements"
    SEARCH_FLIGHTS = "search-flights"
    BOOK_FLIGHT = "book-thornton-tomasetti-flight"


class Decision(Enum):
    BOOK = "BOOK"
    REFUSE = "REFUSE"
    FLAG_FOR_APPROVAL = "FLAG_FOR_APPROVAL"


class Cabin(Enum):
    ECONOMY = "ECONOMY"
    PREMIUM_ECONOMY = "PREMIUM_ECONOMY"
    BUSINESS = "BUSINESS"
    FIRST = "FIRST"
    NONE = "NONE"


class ReasonCode(Enum):
    """Why the decision was made. The list is shared by every handbook plugin, so it also holds reasons
    that a given handbook never uses."""

    LOWEST_FARE = "LOWEST_FARE"
    UPGRADE_NOT_ELIGIBLE = "UPGRADE_NOT_ELIGIBLE"
    CLIENT_REIMBURSABLE = "CLIENT_REIMBURSABLE"
    UPGRADE_WITHIN_FARE_MARGIN = "UPGRADE_WITHIN_FARE_MARGIN"
    MEDICAL_NEED = "MEDICAL_NEED"
    COST_SAVINGS = "COST_SAVINGS"
    NO_ECONOMY_SEATS_URGENT = "NO_ECONOMY_SEATS_URGENT"
    TRAVELER_PAYS_UPGRADE = "TRAVELER_PAYS_UPGRADE"
    LONG_FLIGHT_APPROVED = "LONG_FLIGHT_APPROVED"
    LONG_FLIGHT_CONDITION_NOT_MET = "LONG_FLIGHT_CONDITION_NOT_MET"
    PREMIUM_ECONOMY_ALLOWED = "PREMIUM_ECONOMY_ALLOWED"
    UPGRADE_COST_NOT_NOMINAL = "UPGRADE_COST_NOT_NOMINAL"
    ALTERNATE_ROUTE_WITHIN_MARGIN = "ALTERNATE_ROUTE_WITHIN_MARGIN"
    ALTERNATE_ROUTE_TOO_EXPENSIVE = "ALTERNATE_ROUTE_TOO_EXPENSIVE"
    LOYALTY_PROGRAM_PREFERENCE = "LOYALTY_PROGRAM_PREFERENCE"
    COMPANION_NOT_COVERED = "COMPANION_NOT_COVERED"
    PERSONAL_TRAVEL_NOT_COVERED = "PERSONAL_TRAVEL_NOT_COVERED"
    OUTSIDE_POLICY_SCOPE = "OUTSIDE_POLICY_SCOPE"
    NO_COMPLIANT_OFFER = "NO_COMPLIANT_OFFER"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    UNCLEAR_POLICY_TEXT = "UNCLEAR_POLICY_TEXT"
    ADVANCE_PURCHASE_TOO_LATE = "ADVANCE_PURCHASE_TOO_LATE"
    DISTANCE_BELOW_MINIMUM = "DISTANCE_BELOW_MINIMUM"
    DRIVING_EXPECTED = "DRIVING_EXPECTED"
    RAIL_PREFERRED = "RAIL_PREFERRED"
    REFUNDABLE_FARE_NOT_ALLOWED = "REFUNDABLE_FARE_NOT_ALLOWED"
    PREFERRED_CARRIER_REQUIRED = "PREFERRED_CARRIER_REQUIRED"
    CONNECTION_TOO_LONG = "CONNECTION_TOO_LONG"
    OVERNIGHT_STOP_REQUIRED = "OVERNIGHT_STOP_REQUIRED"
    NATIONAL_CARRIER_REQUIRED = "NATIONAL_CARRIER_REQUIRED"
    SENIOR_ROLE_ENTITLEMENT = "SENIOR_ROLE_ENTITLEMENT"
    INTERNATIONAL_LONG_FLIGHT = "INTERNATIONAL_LONG_FLIGHT"
    TRAVELLER_LIMIT_PER_FLIGHT = "TRAVELLER_LIMIT_PER_FLIGHT"
    # HANDBOOK-SPECIFIC reason codes go below this line (none for this handbook); keep every shared one above.


class TripType(Enum):
    ONE_WAY = "ONE_WAY"
    ROUND_TRIP = "ROUND_TRIP"


class Topic(Enum):
    ALL = "ALL"
    FIELDS = "FIELDS"
    AIRPORTS = "AIRPORTS"


CODE = "An IATA airport code, e.g. JFK"


@dataclass
class Airport(Output):
    code: Annotated[str, CODE]
    name: Annotated[str, "The airport's name"]
    city: Annotated[str, "The city it serves"]
    country: Annotated[str, "Its country, as an ISO code"]


@dataclass
class Segment(Output):
    flight_number: Annotated[str, "The airline's flight number, e.g. BA 117"]
    origin: Annotated[str, CODE]
    destination: Annotated[str, CODE]
    depart_local: Annotated[str, "When it leaves: YYYY-MM-DD HH:MM, local time at that airport"]
    arrive_local: Annotated[str, "When it lands: YYYY-MM-DD HH:MM, local time at that airport"]
    depart_utc: Annotated[str, "When it leaves: YYYY-MM-DD HH:MM, UTC"]
    arrive_utc: Annotated[str, "When it lands: YYYY-MM-DD HH:MM, UTC"]
    scheduled_minutes: Annotated[int, "Its scheduled time from departure to arrival, in minutes"]


@dataclass
class Offer(Output):
    offer_id: Annotated[str, "The offer's id, to submit when booking or holding it"]
    carrier: Annotated[str, "The airline"]
    trip_type: Annotated[TripType, "ONE_WAY, or ROUND_TRIP when the fare covers the flights out and back"]
    cabin: Annotated[Cabin, "The cabin sold on every flight of the offer"]
    fare_cents: Annotated[int, "The whole fare for one passenger, in cents of the search's currency"]
    seats_available: Annotated[bool, "False when this cabin is sold out on these flights: it is listed but cannot be bought"]
    refundable: Annotated[bool, "Whether the fare can be refunded or changed without a fee"]
    stops: Annotated[int, "Connections on the way out; zero for a nonstop"]
    segments: Annotated[list[Segment], "The flights out, in order"]
    layover_minutes: Annotated[list[int], "Minutes on the ground between consecutive flights out"]
    stopover_nights: Annotated[list[bool], "Per connection out: true when it is a ticketed stopover with a hotel night booked"]
    flying_minutes: Annotated[int, "The flights' scheduled minutes out added together, ground time left out"]
    elapsed_minutes: Annotated[int, "Minutes from the first departure out to the last arrival, ground time included"]
    return_segments: Annotated[list[Segment], "For a round trip, the flights back, in order; empty otherwise"]
    return_layover_minutes: Annotated[list[int], "Minutes on the ground between consecutive flights back"]
    return_stopover_nights: Annotated[list[bool], "Per connection back: true for a ticketed stopover with a hotel night"]
    return_flying_minutes: Annotated[int, "The flights' scheduled minutes back added together; zero one way"]
    return_elapsed_minutes: Annotated[int, "Minutes from the first departure back to the last arrival; zero one way"]


# ---------------------------------------------------------------------------------------------------------
# HANDBOOK-SPECIFIC: Thornton Tomasetti, Travel and Business Expense Policy (October 2019).
# ---------------------------------------------------------------------------------------------------------


class Scenario(Enum):
    AMBER_QUAY = "amber-quay"
    BASALT_FERRY = "basalt-ferry"
    CEDAR_LANTERN = "cedar-lantern"
    DUNE_ORCHARD = "dune-orchard"
    EMBER_TRELLIS = "ember-trellis"
    FJORD_PEBBLE = "fjord-pebble"
    GARNET_HARBOR = "garnet-harbor"
    HAZEL_COMPASS = "hazel-compass"
    INDIGO_MEADOW = "indigo-meadow"
    JUNIPER_ANVIL = "juniper-anvil"
    KESTREL_LOOM = "kestrel-loom"
    LINDEN_SPIRE = "linden-spire"
    MARBLE_CANOPY = "marble-canopy"
    NUTMEG_BRIDGE = "nutmeg-bridge"
    OPAL_THICKET = "opal-thicket"
    PEWTER_DELTA = "pewter-delta"
    QUARTZ_HOLLOW = "quartz-hollow"
    RUSSET_GLADE = "russet-glade"
    SAFFRON_WHARF = "saffron-wharf"
    TIMBER_CAIRN = "timber-cairn"
    UMBER_SKIFF = "umber-skiff"
    VELVET_PRAIRIE = "velvet-prairie"
    WILLOW_BEACON = "willow-beacon"
    YARROW_MOSAIC = "yarrow-mosaic"


class Approver(Enum):
    """Roles that may sign off. NONE: nobody's sign-off is involved. NOT_NAMED: one is needed, but the
    handbook names no role."""

    NONE = "NONE"
    NOT_NAMED = "NOT_NAMED"
    SUPERVISOR = "SUPERVISOR"
    MANAGING_PRINCIPAL = "MANAGING_PRINCIPAL"
    VICE_PRESIDENT = "VICE_PRESIDENT"
    OFFICE_DIRECTOR = "OFFICE_DIRECTOR"
    PRACTICE_LEADER = "PRACTICE_LEADER"
    DEPARTMENT_HEAD = "DEPARTMENT_HEAD"
    PRINCIPAL = "PRINCIPAL"
    CONTROLLER = "CONTROLLER"
    CHIEF_FINANCIAL_OFFICER = "CHIEF_FINANCIAL_OFFICER"
    TRAVEL_MANAGER = "TRAVEL_MANAGER"
    CHIEF_EXECUTIVE = "CHIEF_EXECUTIVE"


class Clause(Enum):
    """The handbook's sections, by heading."""

    SCOPE = "SCOPE"
    RESPONSIBILITIES = "RESPONSIBILITIES"
    ARRANGEMENTS = "ARRANGEMENTS"
    AIR_CLASS = "AIR_CLASS"
    AIR_ROUTE = "AIR_ROUTE"
    STANDBY = "STANDBY"
    FREQUENT_FLYER = "FREQUENT_FLYER"
    CANCELLATIONS = "CANCELLATIONS"
    LODGING = "LODGING"
    RENTAL_CAR = "RENTAL_CAR"
    RAIL = "RAIL"
    MEALS = "MEALS"
    CREDIT_CARD = "CREDIT_CARD"
    PERSONAL_TRAVEL = "PERSONAL_TRAVEL"
    WORKING_LATE = "WORKING_LATE"
    EXPENSE_REPORTS = "EXPENSE_REPORTS"
    NOT_REIMBURSABLE = "NOT_REIMBURSABLE"


class Passenger(Enum):
    EMPLOYEE = "EMPLOYEE"
    CONSULTANT = "CONSULTANT"
    JOB_CANDIDATE = "JOB_CANDIDATE"
    SPOUSE_OR_FAMILY = "SPOUSE_OR_FAMILY"


class Purpose(Enum):
    CLIENT_MEETING = "CLIENT_MEETING"
    PROJECT_SITE_WORK = "PROJECT_SITE_WORK"
    INTERNAL_MEETING = "INTERNAL_MEETING"
    TRAINING = "TRAINING"
    CONFERENCE = "CONFERENCE"
    INTERVIEW = "INTERVIEW"
    PERSONAL = "PERSONAL"


class Routing(Enum):
    ANY = "ANY"
    NONSTOP = "NONSTOP"


class SignOffSubject(Enum):
    CABIN_UPGRADE = "CABIN_UPGRADE"
    TRIP = "TRIP"


@dataclass
class SignOff(Output):
    role: Annotated[Approver, "The role of the person who signed off"]
    name: Annotated[str, "Their name"]
    subject: Annotated[SignOffSubject, "What they signed off: a better cabin, or the trip itself"]
    extra_fare_judged_reasonable: Annotated[
        bool, "Whether they wrote that the extra fare for the better cabin is reasonable"
    ]


@dataclass
class PastFlight(Output):
    date: Annotated[str, "The day it left, YYYY-MM-DD"]
    origin: Annotated[str, CODE]
    destination: Annotated[str, CODE]
    scheduled_minutes: Annotated[int, "Its scheduled minutes from departure to arrival"]


@dataclass
class Trip(Output):
    traveller_name: Annotated[str, "Who flies"]
    traveller_title: Annotated[str, "Their job title, or their relation to the employee"]
    passenger: Annotated[Passenger, "What the person flying is to the company"]
    origin: Annotated[Airport, "Where the flight leaves from"]
    destination: Annotated[Airport, "Where it goes"]
    travel_date: Annotated[str, "The day to leave, YYYY-MM-DD: the local date at the origin airport"]
    booking_date: Annotated[str, "Today in this world, the day the ticket is bought, YYYY-MM-DD"]
    purpose: Annotated[str, "Why the trip is made, in plain words"]
    purpose_kind: Annotated[Purpose, "The kind of trip"]
    client_reimburses_trip: Annotated[bool, "Whether a client pays the company back for this trip"]
    project_cost: Annotated[bool, "Whether the trip is charged to a project"]
    requested_cabin: Annotated[Cabin, "The cabin the traveller asks for"]
    requested_routing: Annotated[Routing, "NONSTOP when the traveller asks for a nonstop flight; ANY otherwise"]
    traveller_pays_upgrade: Annotated[bool, "Whether the traveller pays, out of pocket, anything above the cheapest ticket"]
    special_needs_on_file: Annotated[bool, "Whether a medical or accessibility need of the traveller is on file"]
    urgent_cannot_postpone: Annotated[bool, "Whether the trip is an emergency that cannot be moved to another day"]
    rest_needed_on_arrival: Annotated[bool, "Whether the traveller must sleep on board to work as soon as they land"]
    extra_costs_if_cheapest_cents: Annotated[
        int, "Extra hotel, meal or overtime cost, in cents, that the cheapest ticket would add; zero when none"
    ]
    sign_offs: Annotated[list[SignOff], "Sign-offs already on file for this trip"]
    recent_flights: Annotated[list[PastFlight], "The traveller's earlier flights on file, most recent first"]


# ---------------------------------------------------------------------------------------------------------
# SHARED (template), continued: the tools' and tasks' inputs and outputs.
# ---------------------------------------------------------------------------------------------------------


@dataclass
class TaskInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id"]
    request: Annotated[str, "The traveller's request, in their own words"]


@dataclass
class TripInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id, as the task input gives it"]


@dataclass
class TripOutput(Output):
    scenario: Annotated[Scenario, "The case id"]
    request: Annotated[str, "The traveller's request, in their own words"]
    trip: Annotated[Trip, "The trip record behind the request"]


@dataclass
class SearchInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id"]
    origin: Annotated[str, "The airport to leave from: An IATA airport code, e.g. JFK"]
    destination: Annotated[str, "The airport to fly to: An IATA airport code, e.g. JFK"]
    date: Annotated[str, "The day to leave, YYYY-MM-DD: the local date at the origin airport, on or after the booking date"]
    return_date: Annotated[str, "For round-trip fares, the day to fly back, YYYY-MM-DD, local at the destination; empty for one way"]


@dataclass
class SearchOutput(Output):
    note: Annotated[str, "Where the offers come from"]
    currency: Annotated[str, "The currency of every fare, as an ISO code"]
    offers: Annotated[list[Offer], "Every offer leaving on that local date, in departure order"]


@dataclass
class BookingOutput(Output):
    decision: Annotated[
        Decision,
        "BOOK: buy offer_id now. REFUSE: buy nothing, because the company will not pay for this ticket. "
        "FLAG_FOR_APPROVAL: hold offer_id and buy nothing yet, because someone must approve it first or "
        "the handbook's words leave the answer open",
    ]
    offer_id: Annotated[str, "The offer bought or held, exactly as search_flights listed it; empty when refusing"]
    cabin: Annotated[Cabin, "That offer's cabin; NONE when refusing"]
    reason_code: Annotated[ReasonCode, "Why, from the closed list"]
    approver: Annotated[
        Approver,
        "The role whose sign-off this decision relies on or still waits for; NONE when it needs nobody's; "
        "NOT_NAMED when a sign-off is needed but the handbook names no role",
    ]
    clause: Annotated[Clause, "The handbook section the decision rests on"]


@dataclass
class SolveOutput(Output):
    trip: Annotated[Trip, "The trip record"]
    offers: Annotated[list[Offer], "Every offer on the trip's route and date"]
    decision: Annotated[Decision, "The correct decision"]
    offer_ids: Annotated[list[str], "Every offer id that is a correct choice; empty when refusing"]
    cabins: Annotated[list[Cabin], "Every correct cabin"]
    reason_codes: Annotated[list[ReasonCode], "Every accepted reason"]
    approvers: Annotated[list[Approver], "Every accepted approver"]
    clauses: Annotated[list[Clause], "Every accepted section"]
    unclear_phrase: Annotated[str, "For a hold over unclear words, those words; empty otherwise"]
    explanation: Annotated[str, "How the answer key reached the answer"]


@dataclass
class FieldHelp(Output):
    name: Annotated[str, "The trip record field's name"]
    kind: Annotated[str, "Its type"]
    description: Annotated[str, "What it means"]


@dataclass
class RequirementsInput(Output):
    topic: Annotated[Topic, "ALL for everything, FIELDS for the trip record's fields, AIRPORTS for the airport list"]


@dataclass
class RequirementsOutput(Output):
    fields: Annotated[list[FieldHelp], "The trip record's fields; empty for AIRPORTS"]
    conventions: Annotated[list[str], "How times, dates, fares and seats work in this world; empty for AIRPORTS"]
    airports: Annotated[list[Airport], "The airports the simulated world knows; empty for FIELDS"]


TOOLS = {
    Tool.BOOKING_REQUIREMENTS: (RequirementsInput, RequirementsOutput),
    Tool.GET_TRIP: (TripInput, TripOutput),
    Tool.SEARCH_FLIGHTS: (SearchInput, SearchOutput),
    Tool.SOLVE_BOOKING: (TaskInput, SolveOutput),
}
TASKS = {
    Task.BOOKING_REQUIREMENTS: (RequirementsInput, RequirementsOutput),
    Task.SEARCH_FLIGHTS: (SearchInput, SearchOutput),
    Task.BOOK_FLIGHT: (TaskInput, BookingOutput),
}
