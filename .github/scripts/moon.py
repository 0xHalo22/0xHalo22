"""
moon phase + illumination + days-to-next-quarter.

uses a simple synodic-month formula seeded on a known new moon. accurate to
within a few hours, which is more than enough for a daily readout. no external
data, no APIs, just date math.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

# a known new moon — 2000-01-06 18:14 UTC. used as the reference epoch
# from which we count synodic months.
REF_NEW_MOON = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)
# average length of a synodic month (new moon to new moon) in days.
# the actual length varies by ~6 hours either way; this is the mean.
SYNODIC_DAYS = 29.530588853

# labels for the spans between principal moments. we deliberately do NOT use
# "first quarter" / "last quarter" / "new moon" / "full moon" as labels —
# those are *moments*, not spans, and naming the span after the moment leads
# to redundant readouts like "last quarter (label) ... last quarter tomorrow
# (next principal)". instead the label tells you what span you're in, and
# the next-principal line tells you when the exact moment arrives.


@dataclass
class MoonState:
    phase: float            # 0.0 to 1.0 around the synodic cycle
    illumination: float     # 0.0 to 1.0
    label: str              # e.g. "waning gibbous"
    glyph: str              # 🌖
    next_quarter: str       # e.g. "last quarter"
    days_to_next: float     # days until that next quarter


def phase_at(now: datetime) -> float:
    """fraction through the synodic month, 0.0 (new) to 1.0 (also new)."""
    days_since_ref = (now - REF_NEW_MOON).total_seconds() / 86400
    return (days_since_ref % SYNODIC_DAYS) / SYNODIC_DAYS


def illumination_at(phase: float) -> float:
    """fraction of the moon's disc lit up, 0.0 to 1.0."""
    # the lit fraction follows (1 - cos(2π·phase)) / 2 — peaks at phase=0.5 (full).
    return (1 - math.cos(2 * math.pi * phase)) / 2


def label_for(phase: float) -> tuple[str, str]:
    """returns (span_label, glyph) for the current phase fraction."""
    # tight bands around new (0.0/1.0) and full (0.5) get the named-moment treatment.
    # otherwise we use the four crescent/gibbous span names.
    if phase < 0.02 or phase > 0.98:
        return "near new moon", "🌑"
    if phase < 0.25:
        return "waxing crescent", "🌒"
    if phase < 0.48:
        return "waxing gibbous", "🌔"
    if phase < 0.52:
        return "near full moon", "🌕"
    if phase < 0.75:
        return "waning gibbous", "🌖"
    return "waning crescent", "🌘"


# the four "principal" phases — new, first quarter, full, last quarter —
# each at fractions 0, 0.25, 0.5, 0.75. these are what people care about
# as "next" milestones.
PRINCIPAL = [
    (0.00, "new moon"),
    (0.25, "first quarter"),
    (0.50, "full moon"),
    (0.75, "last quarter"),
    (1.00, "new moon"),  # wraps
]


def next_principal(phase: float) -> tuple[str, float]:
    """given the current phase fraction, return (next_principal_name, days_until)."""
    for fraction, name in PRINCIPAL:
        if fraction > phase + 1e-9:  # strict > so we don't say 'in 0 days' on the boundary
            days = (fraction - phase) * SYNODIC_DAYS
            return name, days
    # shouldn't be reached (1.00 is the sentinel) but be safe
    return "new moon", 0.0


def next_dramatic(now: datetime, phase: float) -> tuple[str, datetime]:
    """next full or new moon (whichever comes first), with absolute date.

    quarters are useful but full and new moons are the milestones people
    actually plan around. we always look ahead to the next one — the line
    sits below the imminent-quarter line as a longer-horizon anchor."""
    if phase < 0.5:
        name = "full moon"
        days_until = (0.5 - phase) * SYNODIC_DAYS
    else:
        name = "new moon"
        days_until = (1.0 - phase) * SYNODIC_DAYS
    return name, now + timedelta(days=days_until)


def state_now() -> MoonState:
    now = datetime.now(timezone.utc)
    p = phase_at(now)
    illum = illumination_at(p)
    label, glyph = label_for(p)
    next_name, days_until = next_principal(p)
    return MoonState(
        phase=p,
        illumination=illum,
        label=label,
        glyph=glyph,
        next_quarter=next_name,
        days_to_next=days_until,
    )


def render(state: MoonState | None = None) -> str:
    """four-line ASCII block describing the moon right now plus the next
    dramatic milestone (full or new moon, whichever comes first) as an
    absolute date — gives the column a planning-horizon anchor."""
    if state is None:
        state = state_now()
    pct = round(state.illumination * 100)
    days = state.days_to_next
    if days < 1:
        when = "today"
    elif days < 1.5:
        when = "tomorrow"
    else:
        when = f"in {round(days)} days"
    next_name, next_date = next_dramatic(datetime.now(timezone.utc), state.phase)
    next_str = next_date.strftime("%b %-d")
    return (
        f"   {state.glyph}  {state.label}\n"
        f"   {pct}% illuminated\n"
        f"   {state.next_quarter} {when}\n"
        f"   next {next_name}: {next_str}"
    )


if __name__ == "__main__":
    print(render())
