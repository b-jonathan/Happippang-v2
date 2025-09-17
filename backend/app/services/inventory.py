from __future__ import annotations

from datetime import date as date_type
from datetime import timedelta
from typing import Dict, List, Literal, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import Inventory
from app.schemas.inventory import InventoryBulkCreate, InventoryItemIn

Mode = Literal["propagate", "freeze"]


def _fifo_step(prev_b0_end: int, prev_b1_end: int, db_qty: int, pg_qty: int) -> dict:
    """
    3-day shelf life, FIFO sell order: age-2 -> age-1 -> today.
    Leftover age-2 becomes waste. rem = r1 + r0.
    """
    use2 = min(pg_qty, prev_b1_end)
    l2_after = prev_b1_end - use2
    p = pg_qty - use2
    use1 = min(p, prev_b0_end)
    r1 = prev_b0_end - use1
    p = p - use1
    use0 = min(p, db_qty)
    r0 = db_qty - use0

    return {
        "waste": l2_after,
        "rem": r1 + r0,
        "b0_end": r0,  # today's leftover → tomorrow's age-1
        "b1_end": r1,  # yesterday's leftover → tomorrow's age-2
    }


async def _recompute_from(
    session: AsyncSession,
    store_id: UUID,
    item_id: UUID,
    start_date: date_type,
    end_date: Optional[date_type] = None,
) -> None:
    """
    Recompute derived fields forward starting at `start_date` for one item.
    Does NOT create new rows; gaps are simulated silently to roll buckets.
    """
    prev_date = start_date - timedelta(days=1)
    prev = await session.execute(
        select(Inventory.b0_end, Inventory.b1_end).where(
            and_(
                Inventory.store_id == store_id,
                Inventory.item_id == item_id,
                Inventory.date == prev_date,
            )
        )
    )
    row = prev.first()
    b0_prev, b1_prev = (row[0], row[1]) if row else (0, 0)

    q = (
        select(Inventory)
        .where(
            and_(
                Inventory.store_id == store_id,
                Inventory.item_id == item_id,
                Inventory.date >= start_date,
                (Inventory.date <= end_date) if end_date else True,
            )
        )
        .order_by(Inventory.date.asc())
    )
    result = await session.execute(q)
    rows: List[Inventory] = list(result.scalars())

    cur_date = start_date
    for r in rows:
        # roll across missing calendar days without persisting (db=0, pg=0)
        while cur_date < r.date:
            silent = _fifo_step(b0_prev, b1_prev, db_qty=0, pg_qty=0)
            b0_prev, b1_prev = silent["b0_end"], silent["b1_end"]
            cur_date += timedelta(days=1)

        # recompute this row
        res = _fifo_step(b0_prev, b1_prev, db_qty=r.db or 0, pg_qty=r.pg or 0)
        if (
            r.waste != res["waste"]
            or r.rem != res["rem"]
            or r.b0_end != res["b0_end"]
            or r.b1_end != res["b1_end"]
        ):
            r.waste = res["waste"]
            r.rem = res["rem"]
            r.b0_end = res["b0_end"]
            r.b1_end = res["b1_end"]

        b0_prev, b1_prev = r.b0_end, r.b1_end
        cur_date = r.date + timedelta(days=1)


async def bulk_upsert_inventory(
    session: AsyncSession,
    payload: InventoryBulkCreate,
    mode: Optional[Mode] = None,  # explicit override beats payload.mode
) -> List[Inventory]:
    mode = mode or getattr(payload, "mode", "propagate")

    # Keep only rows with movement (db or pg > 0)
    active_items: List[InventoryItemIn] = [
        it for it in payload.items if (it.db or it.pg)
    ]
    if not active_items:
        return []

    item_ids = [it.item_id for it in active_items]
    prev_date = payload.date - timedelta(days=1)

    # One prev-day SELECT for starting buckets
    prev_rows = await session.execute(
        select(Inventory.item_id, Inventory.b0_end, Inventory.b1_end).where(
            and_(
                Inventory.store_id == payload.store_id,
                Inventory.date == prev_date,
                Inventory.item_id.in_(item_ids),
            )
        )
    )
    prev_map: Dict[UUID, Tuple[int, int]] = {
        r.item_id: (r.b0_end or 0, r.b1_end or 0) for r in prev_rows
    }

    # Compute derived fields for day D
    records = []
    for it in active_items:
        p0, p1 = prev_map.get(it.item_id, (0, 0))
        res = _fifo_step(prev_b0_end=p0, prev_b1_end=p1, db_qty=it.db, pg_qty=it.pg)
        records.append(
            {
                "store_id": payload.store_id,
                "item_id": it.item_id,
                "date": payload.date,
                "db": it.db,
                "pg": it.pg,
                "waste": res["waste"],
                "rem": res["rem"],
                "b0_end": res["b0_end"],
                "b1_end": res["b1_end"],
            }
        )

    # Bulk UPSERT day D
    base = pg_insert(Inventory).values(records)
    stmt = base.on_conflict_do_update(
        index_elements=[Inventory.store_id, Inventory.item_id, Inventory.date],
        set_={
            "db": base.excluded.db,
            "pg": base.excluded.pg,
            "waste": base.excluded.waste,
            "rem": base.excluded.rem,
            "b0_end": base.excluded.b0_end,
            "b1_end": base.excluded.b1_end,
        },
    ).returning(Inventory)

    result = await session.execute(stmt)
    rows: List[Inventory] = list(result.scalars())

    # Optional forward recompute
    if mode == "propagate":
        start_next = payload.date + timedelta(days=1)
        for it in active_items:
            await _recompute_from(
                session,
                store_id=payload.store_id,
                item_id=it.item_id,
                start_date=start_next,
            )

    await session.commit()
    return rows
