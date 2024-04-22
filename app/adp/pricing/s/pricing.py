from app.db import ADP_DB, Session

def load_pricing(
        session: Session,
        series: str,
        model_number: str,
        heat_option: str
    ) -> tuple[int, dict[str, int]]:
    # NOTE the ~ operator compares the parameter str to the regex
    # patterns in the column
    pricing_sql = f"""
        SELECT "{heat_option}"
        FROM pricing_s_series
        WHERE :model_number ~ model;
    """
    params = dict(model_number = model_number)
    pricing = ADP_DB.execute(session=session, sql=pricing_sql,
                        params=params).scalar_one()

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