"""test endpoints for returning formatted pricing and executing price updates"""

from fastapi.testclient import TestClient
from httpx import Response
from datetime import datetime, timedelta
import time

from app.main import app
from app.auth import authenticate_auth0_token
from tests import auth_overrides
from app.db import DB_V2

test_client = TestClient(app)

ParameterizedStatusCodes = list[tuple[auth_overrides.Token, int]]

TODAY = datetime.today()
FUTURE_DATE = TODAY + timedelta(days=60)
YESTERDAY = TODAY + timedelta(days=-1)

TEST_VENDOR = "test"
TEST_VENDOR_PRODUCT_ID = 4543
TEST_VENDOR_PRICE_CLASS_ID = 37


def test_price_update_rollback():
    assert not DB_V2.conn_params, "Not connected to the test Database"
    session = next(DB_V2.get_db())
    app.dependency_overrides[authenticate_auth0_token] = auth_overrides.AdminToken
    # Setup test data
    new_class_price = f"""
        INSERT INTO vendor_pricing_by_class (
            pricing_class_id,
            product_id,
            price,
            effective_date
        )
        VALUES (
            {TEST_VENDOR_PRICE_CLASS_ID},
            {TEST_VENDOR_PRODUCT_ID},
            90, 
            '{YESTERDAY.date()}'
        )
        RETURNING id;
    """
    price_id = DB_V2.execute(session, new_class_price).scalar_one()
    # session.commit()
    # time.sleep(1)
    update_price_to_add_history = f"""
        UPDATE vendor_pricing_by_class
        SET price = 100, effective_date = '{TODAY.date()}'
        WHERE id = {price_id};
    """
    DB_V2.execute(session, update_price_to_add_history)
    session.commit()
    # execute rollback
    path = f"/admin/price-updates/{TEST_VENDOR}/rollback"
    query = f"?current_effective_date={TODAY}&new_effective_date={FUTURE_DATE}"
    response: Response = test_client.get(path + query)
    assert response.status_code == 200, response.text
    print(price_id)
    # Verify future table
    future = (
        DB_V2.execute(
            session,
            f"""SELECT * FROM vendor_pricing_by_class_future WHERE price_id = {price_id}""",
        )
        .mappings()
        .fetchone()
    )
    assert future["price"] == 100
    assert future["effective_date"].date() == FUTURE_DATE.date()

    # Verify rollback to historical data
    current = (
        DB_V2.execute(
            session, f"""SELECT * FROM vendor_pricing_by_class WHERE id = {price_id}"""
        )
        .mappings()
        .fetchone()
    )
    assert current["price"] == 90
    assert current["effective_date"].date() == YESTERDAY.date()
