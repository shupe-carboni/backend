from datetime import datetime
import re
import pandas as pd
import logging
from functools import partial
from app.adp.adp_models import Fields
from app.adp.extraction.models import parse_model_string, ParsingModes

from sqlalchemy.orm import Session

logger = logging.getLogger("uvicorn.info")


def price_flexcoil_version(
    customer_id: int, session: Session, row_subset: pd.Series
) -> pd.Series:
    """
    ADP is no longer offering Air Handlers as FlexCoils.

    -- 2024-09-05 (Joseph Carboni)

    I don't like doing it this way, but this seems the most
        straightforward given the requirements.
    To accomplish this, I needed to pass the customer_id in from
        CustomerProgram as well as pass in the database Session down
        from generate_program in workbook_factory down through the
        build_program method, in which the Program's `category_data`
        method is called.

    Really wild.

    The point here is to parse out the Flexcoil versions of
        non-flexcoil product and show the model nubers and prices
        side-by-side with currently active or proposed product.

    -- 2024-04-05 (Joseph Carboni)
    """
    model_number: str = row_subset[Fields.MODEL_NUMBER.value]
    series: str = row_subset[Fields.SERIES.value]
    no_change = "Not Available"
    # flexcoil by replacement
    if series in ("HE", "HH", "HD"):
        if model_number.endswith("AP"):
            model_to_parse = model_number.replace("AP", "N")
        elif model_number[:2] == "CE":
            model_to_parse = model_number + "N"
        else:
            return pd.Series([no_change, no_change])
    # flexcoil by append
    elif series in ("MH", "V"):
        if model_number[-1] not in ("R", "N"):
            model_to_parse = model_number + "N"
        else:
            return pd.Series([no_change, no_change])
    else:
        return pd.Series([no_change, no_change])

    result = parse_model_string(
        session=session,
        adp_customer_id=customer_id,
        model=model_to_parse,
        mode=ParsingModes.CUSTOMER_PRICING,
    )
    if result[Fields.PRIVATE_LABEL.value] is not None:
        return result[[Fields.PRIVATE_LABEL.value, Fields.NET_PRICE.value]].rename(
            {Fields.PRIVATE_LABEL.value: Fields.MODEL_NUMBER.value}
        )
    else:
        return result[[Fields.MODEL_NUMBER.value, Fields.NET_PRICE.value]]


class EmptyProgram(Exception): ...


class Program:
    def __init__(self, program_data: pd.DataFrame, ratings: pd.DataFrame) -> None:
        self._data = program_data
        self.product_categories = program_data[Fields.CATEGORY.value].drop_duplicates()
        self.ratings = ratings
        if program_data[Fields.PRIVATE_LABEL.value].isna().all():
            self.product_series_contained = set(
                program_data[Fields.SERIES.value].unique().tolist()
            )
        elif program_data[Fields.PRIVATE_LABEL.value].isna().any():
            temp = program_data[[Fields.SERIES.value, Fields.PRIVATE_LABEL.value]]
            temp[Fields.PRIVATE_LABEL.value] = temp[
                Fields.PRIVATE_LABEL.value
            ].str.slice(0, 2)
            temp = temp.drop_duplicates()
            pl_series = (
                temp.loc[
                    ~pd.isna(temp[Fields.PRIVATE_LABEL.value]),
                    Fields.PRIVATE_LABEL.value,
                ]
                .drop_duplicates()
                .dropna()
                .to_list()
            )
            non_pl_series = (
                temp.loc[
                    pd.isna(temp[Fields.PRIVATE_LABEL.value])
                    & ~pd.isna(temp[Fields.SERIES.value]),
                    Fields.SERIES.value,
                ]
                .drop_duplicates()
                .dropna()
                .to_list()
            )
            self.product_series_contained = set(pl_series + non_pl_series)
        else:
            self.product_series_contained = {"CE", "CF"}

    def category_data(self, category) -> pd.DataFrame:
        data = self._data.loc[self._data[Fields.CATEGORY.value] == category, :]
        return (
            data.dropna(how="all", axis=1)
            .drop(columns=[Fields.CATEGORY.value])
            .sort_values(
                [
                    Fields.TONNAGE.value,
                    Fields.METERING.value,
                    Fields.WIDTH.value,
                    Fields.HEIGHT.value,
                ]
            )
        )


class CoilProgram(Program):

    def __init__(self, program_data: pd.DataFrame, ratings: pd.DataFrame) -> None:
        super().__init__(program_data, ratings)
        self.length_or_depth = Fields.DEPTH.value
        self.model_number = Fields.MODEL_NUMBER.value

    def __str__(self) -> str:
        return "Coils"

    def features(self):
        return [
            self.model_number,
            Fields.PALLET_QTY.value,
            Fields.WIDTH.value,
            self.length_or_depth,
            Fields.HEIGHT.value,
            Fields.WEIGHT.value,
            Fields.CABINET.value,
            Fields.METERING.value,
            Fields.NET_PRICE.value,
            Fields.RATED.value,
            Fields.SERIES.value,
            Fields.STAGE.value,
        ]

    def category_data(
        self, category, customer_id: int, session: Session
    ) -> pd.DataFrame:
        data = super().category_data(category)
        if Fields.LENGTH.value in data.columns:
            self.length_or_depth = Fields.LENGTH.value
        else:
            self.length_or_depth = Fields.DEPTH.value

        if Fields.PRIVATE_LABEL.value in data.columns:
            self.model_number = Fields.PRIVATE_LABEL.value
        else:
            self.model_number = Fields.MODEL_NUMBER.value

        data = data[self.features()].rename(
            columns={Fields.PRIVATE_LABEL.value: Fields.MODEL_NUMBER.value}
        )
        # NOTE: STUFF IN FLEXCOIL MODEL AND PRICE HERE
        apply_method = partial(price_flexcoil_version, customer_id, session)
        data[[Fields.FLEXCOIL_MODEL, Fields.FLEXCOIL_PRICE]] = data[
            [Fields.MODEL_NUMBER.value, Fields.SERIES.value]
        ].apply(apply_method, axis=1, result_type="expand")
        data.insert(
            1, Fields.FLEXCOIL_MODEL.value, data.pop(Fields.FLEXCOIL_MODEL.value)
        )
        data.insert(
            10, Fields.FLEXCOIL_PRICE.value, data.pop(Fields.FLEXCOIL_PRICE.value)
        )
        return data


class AirHandlerProgram(Program):

    def __init__(self, program_data: pd.DataFrame, ratings: pd.DataFrame) -> None:
        super().__init__(program_data, ratings)
        self.pallet_or_min = Fields.MIN_QTY.value
        self.model_number = Fields.MODEL_NUMBER.value

    def __str__(self) -> str:
        return "Air Handlers"

    def features(self):
        return [
            self.model_number,
            self.pallet_or_min,
            Fields.WIDTH.value,
            Fields.DEPTH.value,
            Fields.HEIGHT.value,
            Fields.WEIGHT.value,
            Fields.HEAT.value,
            Fields.METERING.value,
            Fields.NET_PRICE.value,
            Fields.RATED.value,
            Fields.SERIES.value,
            Fields.STAGE.value,
        ]

    def category_data(
        self, category, customer_id: int, session: Session
    ) -> pd.DataFrame:
        data = super().category_data(category)
        if Fields.WEIGHT.value not in data.columns:
            data[Fields.WEIGHT.value] = "--"

        if Fields.PRIVATE_LABEL.value in data.columns:
            self.model_number = Fields.PRIVATE_LABEL.value
        else:
            self.model_number = Fields.MODEL_NUMBER.value

        if Fields.PALLET_QTY.value in data.columns:
            self.pallet_or_min = Fields.PALLET_QTY.value
        else:
            self.pallet_or_min = Fields.MIN_QTY.value

        features = self.features()

        data = data[features].rename(
            columns={Fields.PRIVATE_LABEL.value: Fields.MODEL_NUMBER.value}
        )
        # NOTE: STUFF IN FLEXCOIL MODEL AND PRICE HERE
        apply_method = partial(price_flexcoil_version, customer_id, session)
        data[[Fields.FLEXCOIL_MODEL, Fields.FLEXCOIL_PRICE]] = data[
            [Fields.MODEL_NUMBER.value, Fields.SERIES.value]
        ].apply(apply_method, axis=1, result_type="expand")
        data.insert(
            1, Fields.FLEXCOIL_MODEL.value, data.pop(Fields.FLEXCOIL_MODEL.value)
        )
        data.insert(
            10, Fields.FLEXCOIL_PRICE.value, data.pop(Fields.FLEXCOIL_PRICE.value)
        )
        return data


class CustomerProgram:
    def __init__(
        self,
        customer_id: int,
        customer_name: str,
        logo_path: str,
        coils: CoilProgram = None,
        air_handlers: AirHandlerProgram = None,
        parts: pd.DataFrame = None,
        terms: dict[str, str | dict] = None,
    ) -> None:
        if not (coils or air_handlers):
            raise Exception(
                "Either a Coil Program or an Air Handler " "Program are required"
            )

        self.customer_id = customer_id
        self.customer_name = customer_name
        self.ratings = pd.DataFrame()
        self.progs: list[Program] = [coils, air_handlers]
        self.progs = [prog for prog in self.progs if not prog._data.empty]
        if not self.progs:
            raise EmptyProgram
        self.series_contained = set()
        for prog in self.progs:
            prog_ratings = prog.ratings
            self.ratings = pd.concat([self.ratings, prog_ratings]).drop_duplicates()
            self.series_contained |= prog.product_series_contained
        self.filter_ratings()
        self.tag_models_rated_unrated()
        self.terms = terms
        self.parts = parts
        self.logo_path = logo_path

    def __iter__(self):
        return iter(self.progs)

    def __str__(self) -> str:
        return self.new_file_name()

    def new_file_name(self) -> str:
        TODAY = datetime.today().date()
        customer_name = self.customer_name.title()
        if "'" in customer_name:
            # title() capitalizes or leaves alone letters after an apostrophe
            customer_name = re.sub(
                r"(?<=')([^'])", lambda match: match.group(1).lower(), customer_name
            )
        return f"{customer_name} {TODAY.year} ADP Product Strategy {TODAY}".replace(
            "/", "_"
        )

    def filter_ratings(self) -> None:
        if not self.ratings.empty:
            registered_filter = self.ratings["AHRI Ref Number"] > 0
            registered = self.ratings[registered_filter]
            unregistered = self.ratings[~registered_filter]

            def in_program(value: str) -> bool:
                if not value:
                    return False
                for prog in self.progs:
                    ratings_models: pd.Series = prog._data.loc[
                        :, prog._data.columns.str.contains("ratings")
                    ].stack(future_stack=True)
                    ratings_models = (
                        ratings_models.drop_duplicates().dropna().reset_index(drop=True)
                    )
                    matches = ratings_models.apply(
                        lambda ref: re.match(ref, value) is not None
                    )
                    if matches.any():
                        return True
                return False

            registered["in_prog"] = registered["Coil Model Number"].apply(in_program)
            unregistered["in_prog"] = unregistered["IndoorModel"].apply(in_program)
            registered = registered[registered["in_prog"] == True]
            unregistered = unregistered[unregistered["in_prog"] == True]
            self.ratings = pd.concat([registered, unregistered]).drop(columns="in_prog")

    def tag_models_rated_unrated(self) -> None:
        if not self.ratings.empty:
            ratings_models: pd.Series = (
                self.ratings.loc[:, ["Coil Model Number", "IndoorModel"]]
                .drop_duplicates()
                .fillna("no val")
                .stack(future_stack=True)
            )
            ratings_models = ratings_models[ratings_models != "no val"]

            def in_ratings(value: str) -> bool:
                if not value:
                    return False
                matches = ratings_models.apply(
                    lambda ref: re.match(value, ref) is not None
                )
                if matches.any():
                    return True
                return False

            def check_model_row(row: pd.Series) -> bool:
                ratings_regexes = row[row.index.str.contains("ratings")]
                if ratings_regexes.isna().all():
                    return False
                if ratings_regexes.apply(in_ratings).any():
                    return True
                return False

            for prog in self.progs:
                prog._data["rated"] = prog._data.apply(check_model_row, axis=1)
        else:
            for prog in self.progs:
                prog._data["rated"] = False

    def sample_from_program(self, series: str) -> str:
        for prog in self.progs:
            try:
                sample_series = prog._data[Fields.SERIES.value] == series
                sample = prog._data.loc[
                    sample_series, Fields.MODEL_NUMBER.value
                ].sample(n=1)
            except Exception as e:
                logger.warning("unable to obtain sample from series " f"{series}: {e}")
                continue
            else:
                result: str = sample.item()
                if result[-1] not in ("R", "N"):
                    if series in ("MH", "V", "B", "F", "S", "CP", "CE", "CF"):
                        result += "N"
                    elif series in ("HE", "HH", "HD"):
                        result = result.replace("AP", "N")
                return result
