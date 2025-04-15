"""test endpoints for returning formatted pricing and executing price updates"""

from fastapi.testclient import TestClient
from httpx import Response
from datetime import datetime, timedelta

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
TEST_VENDOR_ANOTHER_PRICE_CLASS_ID = 39
TEST_VENDOR_NEW_PRICE_CLASS_ID = 40
TEST_VENDOR_CUSTOMER_PRICE_CLASS_ID = 502
TEST_CUSTOMER_ID = 257


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
    response: Response = test_client.post(path + query)
    assert response.status_code == 200, response.text
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


def test_customer_pricing_class_update_alters_pricing_labels():
    assert not DB_V2.conn_params, "Not connected to the test Database"
    session = next(DB_V2.get_db())
    app.dependency_overrides[authenticate_auth0_token] = auth_overrides.AdminToken
    # Setup test data
    reset_ = f"""
        DELETE FROM vendor_pricing_by_customer_changelog
        WHERE EXISTS (
            SELECT 1
            FROM vendor_pricing_by_customer
            WHERE vendor_customer_id = {TEST_CUSTOMER_ID}
            AND pricing_class_id = {TEST_VENDOR_NEW_PRICE_CLASS_ID}
        ); 

        DELETE FROM vendor_pricing_by_customer
        WHERE vendor_customer_id = {TEST_CUSTOMER_ID}
            AND pricing_class_id = {TEST_VENDOR_NEW_PRICE_CLASS_ID};

        UPDATE vendor_customer_pricing_classes
        SET pricing_class_id = {TEST_VENDOR_PRICE_CLASS_ID}
        WHERE id = {TEST_VENDOR_CUSTOMER_PRICE_CLASS_ID};

        DELETE FROM vendor_customer_pricing_classes_changelog
        WHERE EXISTS (
            SELECT 1
            FROM vendor_pricing_classes 
            WHERE vendor_pricing_classes.id = vendor_customer_pricing_classes_changelog.pricing_class_id 
                AND vendor_id = '{TEST_VENDOR}'
                AND vendor_pricing_classes.id = {TEST_VENDOR_NEW_PRICE_CLASS_ID}
        );

    """
    setup_pricing = f"""
    INSERT INTO vendor_pricing_by_customer (
            product_id,
            pricing_class_id,
            vendor_customer_id,
            use_as_override,
            price,
            effective_date
        ) VALUES (
            {TEST_VENDOR_PRODUCT_ID},
            {TEST_VENDOR_PRICE_CLASS_ID},
            {TEST_CUSTOMER_ID},
            true,
            150,
            '{TODAY.date()}'
        ),(
            {TEST_VENDOR_PRODUCT_ID},
            {TEST_VENDOR_ANOTHER_PRICE_CLASS_ID},
            {TEST_CUSTOMER_ID},
            false,
            99,
            '{TODAY.date()}'
        )
    ON CONFLICT DO NOTHING RETURNING id;
    """
    DB_V2.execute(session, reset_)
    pricing_ids = DB_V2.execute(session, setup_pricing).scalars().all()
    assert pricing_ids, "no new records created"
    session.commit()
    path = f"/v2/vendors/vendor-customer-pricing-classes/{TEST_VENDOR_CUSTOMER_PRICE_CLASS_ID}"
    data = dict(
        data={
            "id": TEST_VENDOR_CUSTOMER_PRICE_CLASS_ID,
            "type": "vendor-customer-pricing-classes",
            "relationships": {
                "vendors": {"data": {"id": TEST_VENDOR, "type": "vendors"}},
                "vendor-customers": {
                    "data": {"id": TEST_CUSTOMER_ID, "type": "vendor-customers"}
                },
                "vendor-pricing-classes": {
                    "data": {
                        "id": TEST_VENDOR_NEW_PRICE_CLASS_ID,
                        "type": "vendor-pricing-classes",
                    }
                },
            },
        }
    )
    resp: Response = test_client.patch(path, json=data)
    assert resp.status_code == 200, resp.text
    # TODO check the pricing_ids to see if they have the new id
    get_pricing = """
        SELECT id, pricing_class_id
        FROM vendor_pricing_by_customer
        WHERE id in :ids;
    """
    altered_pricing = (
        DB_V2.execute(session, get_pricing, dict(ids=tuple(pricing_ids)))
        .mappings()
        .fetchall()
    )
    expected = zip(
        pricing_ids,
        (TEST_VENDOR_NEW_PRICE_CLASS_ID, TEST_VENDOR_ANOTHER_PRICE_CLASS_ID),
    )
    expected = {e[0]: e[1] for e in expected}
    for price in altered_pricing:
        assert expected[price["id"]] == price["pricing_class_id"]
