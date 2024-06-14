import re
from app.adp.adp_models.model_series import ModelSeries, Fields, Cabinet
from app.db import ADP_DB, Session


class V(ModelSeries):
    text_len = (11, 12)
    regex = r"""
        (?P<paint>[V|A|G|J|N|P|R|T|Y|C])
        (?P<ton>\d{2})
        (?P<type>H)
        (?P<height>\d{3})
        (?P<mat>[D|P])
        (?P<scode>\d{2})
        (?P<meter>\d)
        (?P<rds>[N|R]?)
        """
    material_weight = {"D": "WEIGHT_CU", "P": "WEIGHT_AL"}

    def __init__(self, session: Session, re_match: re.Match):
        super().__init__(session, re_match)
        weight_column = self.material_weight[self.attributes["mat"]]
        specs_sql = f"""
            SELECT length, pallet_qty, "{weight_column}"
            FROM v_or_hd_len_pallet_weights
            WHERE "SC_1" = :scode;
        """
        params = dict(scode=self.attributes["scode"])
        specs = (
            ADP_DB.execute(session=session, sql=specs_sql, params=params)
            .mappings()
            .one()
        )
        if self.attributes["paint"] == "V":
            self.cabinet_config = Cabinet.EMBOSSED
        else:
            self.cabinet_config = Cabinet.PAINTED
        height = int(self.attributes["height"])
        if height % 10 == 2:
            self.height = height / 10 + 0.05
        else:
            self.height = height / 10
        if self.height < 17:
            height_str = r"\*\*\*"
        else:
            height_str = self.attributes["height"]
        self.material = self.material_mapping[self.attributes["mat"]]
        self.metering = self.metering_mapping[int(self.attributes["meter"])]
        self.color = self.paint_color_mapping[self.attributes["paint"]]
        self.width = 21
        self.pallet_qty = specs["pallet_qty"]
        self.length = specs["length"]
        self.weight = specs[weight_column]
        self.mat_grp = self.mat_grps.loc[
            (self.mat_grps["series"] == self.__series_name__())
            & (self.mat_grps["mat"] == self.attributes["mat"]),
            "mat_grp",
        ].item()
        self.tonnage = int(self.attributes["ton"])
        self.is_flex_coil = True if self.attributes.get("rds") else False
        if self.cabinet_config != Cabinet.PAINTED:
            self.ratings_ac_txv = (
                rf"V,.{self.tonnage}H{height_str}"
                rf"{self.attributes['mat']}{self.attributes['scode']}[\(6,9\)|\*]"
            )
            self.ratings_hp_txv = (
                rf"V,.{self.tonnage}H{height_str}"
                rf"{self.attributes['mat']}{self.attributes['scode']}[9|\*]"
            )
            self.ratings_piston = (
                rf"V,.{self.tonnage}H{height_str}"
                rf"{self.attributes['mat']}{self.attributes['scode']}[\(1,2\)|\*]"
            )
            self.ratings_field_txv = (
                rf"V,.{self.tonnage}H{height_str}"
                rf"{self.attributes['mat']}{self.attributes['scode']}[\(1,2\)|\*]"
                rf"\+TXV"
            )
        else:
            self.ratings_ac_txv = (
                rf"V(,.){{0,2}},{self.attributes['paint']}"
                rf"(,.){{0,1}}{self.tonnage}H{height_str}"
                rf"{self.attributes['mat']}{self.attributes['scode']}[\(6,9\)|\*]"
            )
            self.ratings_hp_txv = (
                rf"V(,.){{0,2}},{self.attributes['paint']}"
                rf"(,.){{0,1}}{self.tonnage}H{height_str}"
                rf"{self.attributes['mat']}{self.attributes['scode']}[9|\*]"
            )
            self.ratings_piston = (
                rf"V(,.){{0,2}},{self.attributes['paint']}"
                rf"(,.){{0,1}}{self.tonnage}H{height_str}"
                rf"{self.attributes['mat']}{self.attributes['scode']}[\(1,2\)|\*]"
            )
            self.ratings_field_txv = (
                rf"V(,.){{0,2}},"
                rf"{self.attributes['paint']}(,.){{0,1}}{self.tonnage}"
                rf"H{height_str}{self.attributes['mat']}"
                rf"{self.attributes['scode']}[\(1,2\)|\*]\+TXV"
            )
        self.zero_disc_price = self.calc_zero_disc_price()

    def category(self) -> str:
        material = self.material
        paint = self.color
        value = f'Dedicated Horizontal "A" {material} Coils - {paint}'
        if self.is_flex_coil:
            value += " - FlexCoil"
        return value

    def load_pricing(self) -> tuple[int, dict[str, int]]:
        pricing_sql = f"""
            SELECT "{self.cabinet_config.name}"
            FROM pricing_v_series
            WHERE slab = :scode;
        """
        pricing = ADP_DB.execute(
            session=self.session,
            sql=pricing_sql,
            params=dict(scode=self.attributes["scode"]),
        ).scalar_one()

        price_adders_sql = """
            SELECT key, price
            FROM price_adders
            WHERE series = :series;
        """
        params = dict(series=self.__series_name__())
        adders_ = (
            ADP_DB.execute(session=self.session, sql=price_adders_sql, params=params)
            .mappings()
            .all()
        )
        adders = dict()
        for adder in adders_:
            adders |= {adder["key"]: adder["price"]}
        return pricing, adders

    def calc_zero_disc_price(self) -> int:
        pricing_, adders_ = self.load_pricing()
        result = pricing_ + adders_.get(self.attributes["meter"], 0)
        if self.is_flex_coil:
            result += 10
        return result

    def record(self) -> dict:
        model_record = super().record()
        values = {
            Fields.MODEL_NUMBER.value: str(self),
            Fields.CATEGORY.value: self.category(),
            Fields.MPG.value: self.mat_grp,
            Fields.SERIES.value: self.__series_name__(),
            Fields.TONNAGE.value: self.tonnage,
            Fields.PALLET_QTY.value: self.pallet_qty,
            Fields.WIDTH.value: self.width,
            Fields.LENGTH.value: self.length,
            Fields.HEIGHT.value: self.height,
            Fields.WEIGHT.value: self.weight,
            Fields.CABINET.value: self.cabinet_config.name.title(),
            Fields.METERING.value: self.metering,
            Fields.ZERO_DISCOUNT_PRICE.value: self.zero_disc_price,
            Fields.RATINGS_AC_TXV.value: self.ratings_ac_txv,
            Fields.RATINGS_HP_TXV.value: self.ratings_hp_txv,
            Fields.RATINGS_PISTON.value: self.ratings_piston,
            Fields.RATINGS_FIELD_TXV.value: self.ratings_field_txv,
        }
        model_record.update(values)
        return model_record
