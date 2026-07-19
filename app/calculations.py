from decimal import Decimal
from .models import Session, ParticipantTotal


def compute_totals(session: Session) -> list[ParticipantTotal]:
    """Compute per-participant totals, splitting items and proportional tax/tip."""

    # Calculate each participant's claimed subtotal
    participant_claimed = {pid: Decimal(0) for pid in session.participants.keys()}

    for item in session.items:
        if item.claimed_by:
            # claimed_by is now a dict: {participant_id: quantity_claimed}
            for pid, qty_claimed in item.claimed_by.items():
                share = item.unit_price * Decimal(qty_claimed)
                participant_claimed[pid] += share

    # Calculate proportional tax and tip
    total_claimed = sum(participant_claimed.values())

    results = []
    for pid, participant in session.participants.items():
        claimed_subtotal = participant_claimed[pid]

        # Proportional split of tax and tip based on claimed subtotal
        if total_claimed > 0:
            ratio = claimed_subtotal / total_claimed
            tax_share = (session.tax or Decimal(0)) * ratio
            tip_share = (session.tip or Decimal(0)) * ratio
        else:
            tax_share = Decimal(0)
            tip_share = Decimal(0)

        total_owed = claimed_subtotal + tax_share + tip_share

        results.append(ParticipantTotal(
            participant_id=pid,
            name=participant.name,
            claimed_subtotal=claimed_subtotal,
            tax_share=tax_share,
            tip_share=tip_share,
            total_owed=total_owed,
        ))

    return results
