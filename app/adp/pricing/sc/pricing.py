from app.db import ADP_DB, Session

def load_pricing(
        session: Session,
        model: str,
        col: int
    ) -> int:
    pricing_sql = f"""
        SELECT "{col}"
        FROM pricing_sc_series
        WHERE :model ~ model;
    """
    return ADP_DB.execute(
            session=session,
            sql=pricing_sql,
            params=dict(model=model)
        ).scalar_one()