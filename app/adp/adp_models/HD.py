import re
from app.adp.adp_models.model_series import (
    ModelSeries,
    Fields,
    Cabinet,
    PriceByCategoryAndKey,
)
from app.db import ADP_DB, Session, Database


class HD(ModelSeries):
    text_len = (18, 17)
    regex = r"""
        (?P<paint>[H|A|G|J|N|P|R|T|Y])
        (?P<mat>[D|P])
        (?P<scode>\d{2})
        (?P<meter>[\d|A|B])
        (?P<ton>\d{2})
        (?P<width>E)
        (?P<height>\d{3})
        (?P<notch>B)
        (?P<length>\d{2})
        (?P<config>\d{2})
        (?P<option>(AP)|[R|N])
    """
    material_weight = {"D": "WEIGHT_CU", "P": "WEIGHT_AL"}

    def __init__(self, session: Session, re_match: re.Match, db: Database):
        super().__init__(session, re_match, db)
        specs_sql = f"""
            SELECT length, pallet_qty, "{self.material_weight[
                self.attributes['mat']]}"
            FROM v_or_hd_len_pallet_weights
            WHERE "SC_1" = :scode;
        """
        specs = (
            ADP_DB.execute(
                session=session,
                sql=specs_sql,
                params=dict(scode=int(self.attributes["scode"])),
            )
            .mappings()
            .one()
        )
        if self.attributes["paint"] == "H":
            self.cabinet_config = Cabinet.EMBOSSED
        else:
            self.cabinet_config = Cabinet.PAINTED
        # NOTE width is in the depth slot of the HE-style nomenclature
        self.width = self.coil_depth_mapping[self.attributes["width"]]
        self.height = int(self.attributes["height"]) / 10
        self.length = int(self.attributes["length"]) + 0.5
        self.material = self.material_mapping[self.attributes["mat"]]
        self.color = self.paint_color_mapping[self.attributes["paint"]]
        self.pallet_qty = specs["pallet_qty"]
        self.weight = specs[self.material_weight[self.attributes["mat"]]]
        self.tonnage = int(self.attributes["ton"])
        rds_option = self.attributes.get("option")
        self.rds_factory_installed = False
        self.rds_field_installed = False
        match rds_option:
            case "R":
                self.rds_factory_installed = True
            case "N":
                self.rds_field_installed = True
        a2l_coil = self.rds_factory_installed or self.rds_field_installed
        metering = self.attributes["meter"]
        try:
            metering = int(metering)
            if self.rds_factory_installed:
                metering = -metering
        except ValueError:
            pass
        self.metering = self.metering_mapping[metering]
        painted = self.cabinet_config == Cabinet.PAINTED
        if not painted and not a2l_coil:
            self.ratings_piston = (
                rf"H(,.){{1,2}}{self.attributes['mat']}"
                rf"{self.attributes['scode']}(\(1,2\)){self.tonnage}"
            )
            self.ratings_field_txv = (
                rf"H(,.){{1,2}}{self.attributes['mat']}"
                rf"{self.attributes['scode']}(\(1,2\)){self.tonnage}\+TXV"
            )
            self.ratings_hp_txv = (
                rf"H(,.){{1,2}}{self.attributes['mat']}"
                rf"{self.attributes['scode']}(9){self.tonnage}"
            )
            self.ratings_ac_txv = (
                rf"H(,.){{1,2}}{self.attributes['mat']}"
                rf"{self.attributes['scode']}(\(6,9\)){self.tonnage}"
            )
        elif not painted and a2l_coil:
            self.ratings_piston = (
                rf"H(,.){{1,2}}{self.attributes['mat']}"
                rf"{self.attributes['scode']}1{self.tonnage}"
            )
            self.ratings_field_txv = (
                rf"H(,.){{1,2}}{self.attributes['mat']}"
                rf"{self.attributes['scode']}\*{self.tonnage}\+TXV"
            )
            self.ratings_hp_txv = (
                rf"H(,.){{1,2}}{self.attributes['mat']}"
                rf"{self.attributes['scode']}\*{self.tonnage}\+TXV"
            )
            self.ratings_ac_txv = (
                rf"H(,.){{1,2}}{self.attributes['mat']}"
                rf"{self.attributes['scode']}\*{self.tonnage}\+TXV"
            )
        elif painted and not a2l_coil:
            self.ratings_piston = (
                rf"H(,.){{0,2}},{self.attributes['paint']}"
                rf"(,.){{0,1}}{self.attributes['mat']}"
                rf"{self.attributes['scode']}(\(1,2\)){self.tonnage}"
            )
            self.ratings_field_txv = (
                rf"H(,.){{0,2}},"
                rf"{self.attributes['paint']}(,.){{0,1}}"
                rf"{self.attributes['mat']}{self.attributes['scode']}"
                rf"(\(1,2\)){self.tonnage}\+TXV"
            )
            self.ratings_hp_txv = (
                rf"H(,.){{0,2}},{self.attributes['paint']}"
                rf"(,.){{0,1}}{self.attributes['mat']}"
                rf"{self.attributes['scode']}(9){self.tonnage}"
            )
            self.ratings_ac_txv = (
                rf"H(,.){{0,2}},{self.attributes['paint']}"
                rf"(,.){{0,1}}{self.attributes['mat']}"
                rf"{self.attributes['scode']}(\(6,9\)){self.tonnage}"
            )
        elif painted and a2l_coil:
            self.ratings_piston = (
                rf"H(,.){{0,2}},{self.attributes['paint']}"
                rf"(,.){{0,1}}{self.attributes['mat']}"
                rf"{self.attributes['scode']}1{self.tonnage}"
            )
            self.ratings_field_txv = (
                rf"H(,.){{0,2}},"
                rf"{self.attributes['paint']}(,.){{0,1}}"
                rf"{self.attributes['mat']}{self.attributes['scode']}"
                rf"\*{self.tonnage}\+TXV"
            )
            self.ratings_hp_txv = (
                rf"H(,.){{0,2}},{self.attributes['paint']}"
                rf"(,.){{0,1}}{self.attributes['mat']}"
                rf"{self.attributes['scode']}\*{self.tonnage}\+TXV"
            )
            self.ratings_ac_txv = (
                rf"H(,.){{0,2}},{self.attributes['paint']}"
                rf"(,.){{0,1}}{self.attributes['mat']}"
                rf"{self.attributes['scode']}\*{self.tonnage}\+TXV"
            )
        self.mat_grp = self.mat_grps.loc[
            (self.mat_grps["series"] == self.__series_name__())
            & (self.mat_grps["mat"].str.contains(self.attributes["mat"])),
            "mat_grp",
        ].item()
        self.zero_disc_price = self.calc_zero_disc_price() / 100

    def load_pricing(self) -> tuple[int, PriceByCategoryAndKey]:
        pricing_sql = f"""
            SELECT price
            FROM vendor_product_series_pricing
            WHERE (
                key = :key_1
                OR key = :key_2
            ) AND (
                series = 'HD'
                AND vendor_id = 'adp'
            );
        """
        try:
            key_1 = str(int(self.attributes["scode"]))
            key_2 = f"{int(self.attributes['scode']):02}"
        except ValueError:
            key_1 = key_2 = self.attributes["scode"]
        params = dict(
            key_1=key_1 + f"_{self.cabinet_config.value}".lower(),
            key_2=key_2 + f"_{self.cabinet_config.value}".lower(),
        )
        pricing = self.db.execute(
            session=self.session, sql=pricing_sql, params=params
        ).scalar_one()
        return pricing, self.get_adders()

    def calc_zero_disc_price(self) -> int:
        pricing_, adders_ = self.load_pricing()
        result = pricing_ + adders_["metering"].get(self.attributes["meter"], 0)
        result += adders_["RDS"].get(self.attributes["option"], 0)
        return result

    def category(self) -> str:
        material = self.material
        color = self.color
        additional = "Dedicated Horizontal Coils - Side Connections"
        value = f"{material} {additional} - {color}"
        if self.rds_field_installed or self.rds_factory_installed:
            value += " - A2L"
        else:
            value += " - R410a"
        return value

    def record(self) -> dict:
        model_record = super().record()
        values = {
            Fields.MODEL_NUMBER.value: str(self),
            Fields.CATEGORY.value: self.category(),
            Fields.SERIES.value: self.__series_name__(),
            Fields.MPG.value: self.mat_grp,
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
