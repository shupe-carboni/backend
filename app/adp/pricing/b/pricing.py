from app.db import ADP_DB, Session

def load_pricing(
        session: Session,
        series: str,
        tonnage: str,
        slab: str,
    ) -> tuple[dict[str, int], dict[str, str|int]]:
    pricing_sql = """
        SELECT base, "2", "3", "4"
        FROM pricing_b_series
        WHERE tonnage = :tonnage
        AND slab = :slab;
    """
    params = dict(tonnage=tonnage, slab=slab)
    pricing = ADP_DB.execute(session=session, sql=pricing_sql,
                            params=params).mappings().one_or_none()
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