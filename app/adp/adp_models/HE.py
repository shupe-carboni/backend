import re
from app.adp.adp_models.model_series import (
    ModelSeries,
    Fields,
    Cabinet,
    PriceByCategoryAndKey,
)
from app.db import ADP_DB, Session


class HE(ModelSeries):
    text_len = (18, 17)
    regex = r"""
        (?P<paint>[H|A|G|J|N|P|R|T|Y])
        (?P<mat>[A|E|G])
        (?P<scode>\d{2}|\d\D)
        (?P<meter>[\d|A|B])
        (?P<ton>\d{2})
        (?P<depth>[A|C|D|E])
        (?P<width>\d{3})
        (?P<notch>[A|B])
        (?P<height>\d{2})
        (?P<config>\d{2})
        (?P<option>(AP)|[R|N])
    """

    mat_config_map = {
        "E": {
            "01": "CU_VERT",
            "05": "CU_VERT",
            "20": "CU_MP",
            "22": "CU_MP",
        },
        "G": {
            "01": "AL_VERT",
            "05": "AL_VERT",
            "20": "AL_MP",
            "22": "AL_MP",
        },
        "A": {
            "00": "CU_UNC",
            "04": "CU_UNC",
        },
    }
    orientations = {
        "00": ("Right Hand", "Uncased"),
        "04": ("Left Hand", "Uncased"),
        "01": ("Right Hand", "Upflow"),
        "05": ("Left Hand", "Upflow"),
        "20": ("Right Hand", "Multiposition"),
        "22": ("Left Hand", "Multiposition"),
    }

    def __init__(self, session: Session, re_match: re.Match):
        super().__init__(session, re_match)
        width: int = int(self.attributes["width"])
        if width % 10 == 2:
            self.width = width / 10 + 0.05
        else:
            self.width = width / 10
        self.depth = self.coil_depth_mapping[self.attributes["depth"]]
        height: int = int(self.attributes["height"])
        self.height = height + 0.5 if self.depth != 19.5 else height
        pallet_sql = f"""
            SELECT "{self.height}"
            FROM he_pallet_qty
            WHERE width = :width;
        """
        pallet_params = dict(width=self.width)
        self.pallet_qty = ADP_DB.execute(
            session=session, sql=pallet_sql, params=pallet_params
        ).scalar_one()
        material_orientation_col_mask = self.mat_config_map[self.attributes["mat"]][
            self.attributes["config"]
        ]
        weights_sql = f"""
            SELECT "{material_orientation_col_mask}"
            FROM he_weights
            WHERE "SC_0" LIKE :mat
            AND "SC_1" = :scode;
        """
        weight_params = dict(
            mat=f"%{self.attributes['mat']}%", scode=self.attributes["scode"]
        )
        self.weight = ADP_DB.execute(
            session=session, sql=weights_sql, params=weight_params
        ).scalar_one()
        if self.attributes["paint"] == "H":
            self.cabinet_config = Cabinet.EMBOSSED
        else:
            self.cabinet_config = Cabinet.PAINTED
        self.material = self.material_mapping[self.attributes["mat"]]
        self.color = self.paint_color_mapping[self.attributes["paint"]]
        self.mat_grp = self.mat_grps.loc[
            (self.mat_grps["series"] == self.__series_name__())
            & (self.mat_grps["mat"].str.contains(self.attributes["mat"]))
            & (self.mat_grps["config"].str.contains(self.attributes["config"])),
            "mat_grp",
        ].item()
        self.tonnage = int(self.attributes["ton"])
        rds_option = self.attributes.get("option")
        self.rds_factory_installed = False
        self.rds_field_installed = False
        match rds_option:
            case "R":
                self.rds_factory_installed = True
            case "N":
                self.rds_field_installed = True
        metering = self.attributes["meter"]
        try:
            metering = int(metering)
            if self.rds_factory_installed:
                metering = -metering
        except ValueError:
            pass
        self.metering = self.metering_mapping[metering]
        if self.cabinet_config != Cabinet.PAINTED:
            self.ratings_piston = (
                rf"H(,.){{1,2}}"
                rf"{self.attributes['mat']}{self.attributes['scode']}"
                rf"(\(1,2\)|\*){self.tonnage}"
            )
            self.ratings_field_txv = (
                rf"H(,.){{1,2}}{self.attributes['mat']}"
                rf"{self.attributes['scode']}(\(1,2\)|\*){self.tonnage}\+TXV"
            )
            self.ratings_hp_txv = (
                rf"H(,.){{1,2}}{self.attributes['mat']}"
                rf"{self.attributes['scode']}(9|\*){self.tonnage}"
            )
            self.ratings_ac_txv = (
                rf"H(,.){{1,2}}{self.attributes['mat']}"
                rf"{self.attributes['scode']}(\(6,9\)|\*){self.tonnage}"
            )
        else:
            self.ratings_piston = (
                rf"H(,.){{0,2}},{self.attributes['paint']}"
                rf"(,.){{0,1}}{self.attributes['mat']}"
                rf"{self.attributes['scode']}(\(1,2\)|\*){self.tonnage}"
            )
            self.ratings_field_txv = (
                rf"H(,.){{0,2}},"
                rf"{self.attributes['paint']}(,.){{0,1}}"
                rf"{self.attributes['mat']}{self.attributes['scode']}"
                rf"(\(1,2\)|\*){self.tonnage}\+TXV"
            )
            self.ratings_hp_txv = (
                rf"H(,.){{0,2}},{self.attributes['paint']}"
                rf"(,.){{0,1}}{self.attributes['mat']}"
                rf"{self.attributes['scode']}(9|\*){self.tonnage}"
            )
            self.ratings_ac_txv = (
                rf"H(,.){{0,2}},{self.attributes['paint']}"
                rf"(,.){{0,1}}{self.attributes['mat']}"
                rf"{self.attributes['scode']}(\(6,9\)|\*){self.tonnage}"
            )
        self.zero_disc_price = self.calc_zero_disc_price()

    def category(self) -> str:
        material = self.material
        color = (
            self.color if self.attributes["paint"] == "H" else self.color + " Painted"
        )
        connections, orientation = self.orientations[self.attributes["config"]]
        additional = "Cased Coils"
        value = f"{orientation} {material} {connections} {additional} - {color}"
        if self.rds_field_installed:
            value += " - FlexCoil"
        elif self.rds_factory_installed:
            value += " - A2L"
        return value

    def load_pricing(self, config: str) -> tuple[int, PriceByCategoryAndKey]:

        pricing_sql = f"""
            SELECT "{config}"
            FROM pricing_he_series 
            WHERE slab = :slab;
        """
        params = dict(slab=str(self.attributes["scode"]))
        pricing = ADP_DB.execute(
            session=self.session, sql=pricing_sql, params=params
        ).scalar_one()

        return int(pricing), self.get_adders()

    def calc_zero_disc_price(self) -> int:
        if self.depth == 19.5:
            col = "uncased"
        else:
            col = self.cabinet_config.name
            match self.attributes["config"]:
                case "01" | "05":
                    col += "_CASED"
                case "20" | "22":
                    col += "_MP"
                case _:
                    col = "uncased"
        paint: str = str(self.attributes["paint"])
        pricing_, adders_ = self.load_pricing(config=col)
        core_configs_sql = """
            SELECT depth, hand
            FROM he_core_configs
            WHERE series = :series;
        """
        core_configs_params = dict(series=paint)
        core_configs = (
            ADP_DB.execute(
                session=self.session, sql=core_configs_sql, params=core_configs_params
            )
            .mappings()
            .one()
        )

        # adder for txvs
        result = pricing_ + adders_["metering"].get(self.attributes["meter"], 0)

        # adder for non_core depth
        core_depths: str = core_configs["depth"]
        core_depths_list = [e.strip() for e in core_depths.split(",")]
        depth_core_status = (
            "core" if self.attributes["depth"] in core_depths_list else "non-core"
        )
        result += adders_["misc"].get(depth_core_status, 0)

        # adder for non_core hand
        core_hands: str = core_configs["hand"]
        core_hands_list = [e.strip() for e in core_hands.split(",")]
        hand = {
            "01": "R",
            "00": "R",
            "04": "L",
            "05": "L",
            "20": "R",
            "22": "L",
        }
        model_hand = hand[self.attributes["config"]]
        hand_core_status = "core" if model_hand in core_hands_list else "non-core"
        result += adders_["misc"].get(hand_core_status, 0)
        result += adders_["RDS"].get(self.attributes["option"], 0)
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
            Fields.DEPTH.value: self.depth,
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
