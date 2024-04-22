from app.db import ADP_DB, Session

def load_pricing(
        session: Session,
        slab: str,
        series: str
    ) -> tuple[int, dict[str,int]]:
    pricing_sql = """
        SELECT price
        FROM pricing_mh_series
        WHERE slab = :slab;
    """
    params = dict(slab=slab)
    pricing = ADP_DB.execute(
        session=session,
        sql=pricing_sql,
        params=params
    ).scalar_one()

    price_adders_sql = """
        SELECT key, price
        FROM price_adders
        WHERE series = :series;
    """
    params = dict(series=series)
    adders_ = ADP_DB.execute(session=session, sql=price_adders_sql,
                        params=params).mappings().all()
    adders = dict()
    for adder in adders_:
        adders |= {adder['key']: adder['price']}
    return pricing, adders