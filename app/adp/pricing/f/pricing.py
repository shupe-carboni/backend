from app.db import ADP_DB, Session

def load_pricing(
        session: Session, slab: str,
        series: str,
        ton: int
    ) -> tuple[dict[str, int], dict[str, int]]:

    pricing_sql = """
        SELECT base, "05", "07", "10", "15", "20"
        FROM pricing_f_series
        WHERE :slab ~ slab
        AND tonnage = :ton;
    """
    # NOTE the ~ operator in Postgres checks that :slab matches regex
    # values contained in the column "slab"
    params = dict(slab=slab, ton=ton)
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