import re
from app.adp.adp_models.model_series import ModelSeries, Fields, NoBasePrice
from app.db import Session
from app.db.sql import queries


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

    def calc_zero_disc_price(self) -> tuple[int, int | None]:
        sql_parts = queries.adp_parts_model_lookup_price
        params = dict(part_number=self.part_number, use_future=self.use_future)
        # standard
        if result := self.db.execute(
            self.session,
            sql_parts,
            params | dict(pricing_class_name="STANDARD_PARTS"),
        ).one_or_none():
            price_std, self.eff_date = result
        else:
            raise NoBasePrice(f"{self.part_number} not found in the pricing table")

        # preferred
        if result := self.db.execute(
            self.session,
            sql_parts,
            params | dict(pricing_class_name="PREFERRED_PARTS"),
        ).one_or_none():
            price_pref, self.eff_date = result
        else:
            price_pref = None

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
