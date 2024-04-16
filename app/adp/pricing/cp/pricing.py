from app.db import ADP_DB, Session

class NoBasePrice(Exception): ...

def load_pricing(session: Session, material: str,
                 model: str) -> int:
    sql = f"""
        SELECT price
        FROM pricing_cp_series
        WHERE "{material}" = :model ;
    """
    params = dict(model=model)
    result = (ADP_DB.execute(session=session, sql=sql, params=params)
                .scalar_one_or_none())
    if not result:
        raise NoBasePrice
    return int(result)