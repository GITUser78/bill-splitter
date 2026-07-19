from decimal import Decimal
from datetime import datetime
from app.models import Session, Participant, BillItem
from app.calculations import compute_totals


def test_worked_example():
    """Burger $10 + Fries $5 + Coke $3 with A and B sharing.

    A claims Burger ($10) + Coke ($3) = $13 claimed
    B claims Fries ($5)

    Subtotal: $18
    Tax: $1.80 (10%)
    Tip: $3.60 (20%)
    Total: $23.40

    A's share: 13/18 ratio
      Claimed: $13.00
      Tax: $1.80 * 13/18 = $1.30
      Tip: $3.60 * 13/18 = $2.60
      Total: $16.90

    B's share: 5/18 ratio
      Claimed: $5.00
      Tax: $1.80 * 5/18 = $0.50
      Tip: $3.60 * 5/18 = $1.00
      Total: $6.50

    Sum: $16.90 + $6.50 = $23.40 ✓
    """
    # Create participants
    a = Participant(name="A")
    b = Participant(name="B")

    # Create items
    burger = BillItem(name="Burger", unit_price=Decimal("10"), quantity=1)
    fries = BillItem(name="Fries", unit_price=Decimal("5"), quantity=1)
    coke = BillItem(name="Coke", unit_price=Decimal("3"), quantity=1)

    # A claims burger and coke; B claims fries
    burger.claimed_by.add(a.id)
    coke.claimed_by.add(a.id)
    fries.claimed_by.add(b.id)

    # Create session
    session = Session(
        id="test-1",
        created_at=datetime.now(),
        host_id=a.id,
        participants={a.id: a, b.id: b},
        items=[burger, fries, coke],
        subtotal=Decimal("18"),
        tax=Decimal("1.80"),
        tip=Decimal("3.60"),
        total=Decimal("23.40"),
    )

    # Compute totals
    totals = compute_totals(session)
    totals_by_id = {t.participant_id: t for t in totals}

    a_total = totals_by_id[a.id]
    b_total = totals_by_id[b.id]

    # Verify A's totals
    assert a_total.claimed_subtotal == Decimal("13")
    assert a_total.tax_share == Decimal("1.30")
    assert a_total.tip_share == Decimal("2.60")
    assert a_total.total_owed == Decimal("16.90")

    # Verify B's totals
    assert b_total.claimed_subtotal == Decimal("5")
    assert b_total.tax_share == Decimal("0.50")
    assert b_total.tip_share == Decimal("1.00")
    assert b_total.total_owed == Decimal("6.50")

    # Verify sum matches total
    total_owed = a_total.total_owed + b_total.total_owed
    assert total_owed == Decimal("23.40")
