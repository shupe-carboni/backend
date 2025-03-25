import re
from app.adp.adp_models.model_series import ModelSeries, Fields, NoBasePrice
from app.db import Session


class PartOrAccessory(ModelSeries):
    text_len = tuple(range(8, 13))
    regex = r"""(?P<part_number>\d{8,11}[A|B]?)"""

    def __init__(
        self, session: Session, re_match: re.Match, db: Session, *args, **kwargs
    ):
        super().__init__(session, re_match, db, *args, **kwargs)
        self.part_number = self.attributes["part_number"]
        self.standard, self.preferred = (p / 100 for p in self.calc_zero_disc_price())
        self.description = self.db.execute(
            self.session,
            """SELECT vendor_product_description
                FROM vendor_products
                WHERE vendor_product_identifier = :part_number
                AND vendor_id = 'adp';
            """,
            dict(part_number=self.part_number),
        ).scalar_one_or_none()

    def category(self) -> str:
        return "Parts & Accessories"

    def calc_zero_disc_price(self) -> tuple[int, int]:
        if self.use_future:
            sql_std = """
                SELECT future.price, future.effective_date
                FROM vendor_pricing_by_class_future future
                JOIN vendor_pricing_by_class a
                    ON a.id = future.price_id
                WHERE EXISTS (
                    SELECT 1
                    FROM vendor_products b
                    WHERE b.id = product_id
                    AND b.vendor_product_identifier = :part_number
                    AND b.vendor_id = 'adp'
                ) AND EXISTS (
                    SELECT 1
                    FROM vendor_pricing_classes c
                    WHERE c.id = pricing_class_id
                    AND c.name = 'STANDARD_PARTS'
                    AND c.vendor_id = 'adp'
                );
            """
            sql_pref = """
                SELECT future.price, future.effective_date
                FROM vendor_pricing_by_class_future future
                JOIN vendor_pricing_by_class a
                    ON a.id = future.price_id
                WHERE EXISTS (
                    SELECT 1
                    FROM vendor_products b
                    WHERE b.id = product_id
                    AND b.vendor_product_identifier = :part_number
                    AND b.vendor_id = 'adp'
                ) AND EXISTS (
                    SELECT 1
                    FROM vendor_pricing_classes c
                    WHERE c.id = pricing_class_id
                    AND c.name = 'PREFERRED_PARTS'
                    AND c.vendor_id = 'adp'
                );
            """
        else:
            sql_std = """
                SELECT price, effective_date
                FROM vendor_pricing_by_class a
                WHERE EXISTS (
                    SELECT 1
                    FROM vendor_products b
                    WHERE b.id = product_id
                    AND b.vendor_product_identifier = :part_number
                    AND b.vendor_id = 'adp'
                ) AND EXISTS (
                    SELECT 1
                    FROM vendor_pricing_classes c
                    WHERE c.id = pricing_class_id
                    AND c.name = 'STANDARD_PARTS'
                    AND c.vendor_id = 'adp'
                );
            """
            sql_pref = """
                SELECT price, effective_date
                FROM vendor_pricing_by_class a
                WHERE EXISTS (
                    SELECT 1
                    FROM vendor_products b
                    WHERE b.id = product_id
                    AND b.vendor_product_identifier = :part_number
                    AND b.vendor_id = 'adp'
                ) AND EXISTS (
                    SELECT 1
                    FROM vendor_pricing_classes c
                    WHERE c.id = pricing_class_id
                    AND c.name = 'PREFERRED_PARTS'
                    AND c.vendor_id = 'adp'
                );
            """
        price_std, self.eff_date = self.db.execute(
            self.session, sql_std, dict(part_number=self.part_number)
        ).one_or_none()
        price_pref, self.eff_date = self.db.execute(
            self.session, sql_pref, dict(part_number=self.part_number)
        ).one_or_none()
        if not (price_std or price_pref):
            raise NoBasePrice(f"{self.part_number} not found in the pricing table")
        return (price_std, price_pref)

    def record(self) -> dict:
        model_record = super().record()
        values = {
            Fields.EFFECTIVE_DATE.value: str(self.eff_date),
            Fields.MODEL_NUMBER.value: str(self),
            Fields.CATEGORY.value: self.category(),
            Fields.DESCRIPTION.value: self.description,
            Fields.SERIES.value: self.__series_name__(),
            Fields.STANDARD_PRICE.value: self.standard,
            Fields.PREFERRED_PRICE.value: self.preferred,
        }
        model_record.update(values)
        return model_record
