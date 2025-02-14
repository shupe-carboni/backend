from datetime import datetime
from warnings import warn
import re
import pandas as pd
import logging
from functools import partial, wraps
from app.adp.adp_models import Fields
from app.adp.extraction.models import parse_model_string, ParsingModes

from sqlalchemy.orm import Session

logger = logging.getLogger("uvicorn.info")


def deprecated(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        warn(
            "Flexcoil is no longer dynamically added to strategy files for comparison."
            " This function will be removed in a future version.",
            DeprecationWarning,
            stacklevel=2,
        )
        return func(*args, **kwargs)

    return wrapper


@deprecated
def price_flexcoil_version(
    customer_id: int, session: Session, row_subset: pd.Series
) -> pd.Series:
    """
    ADP has killed the FlexCoil in practical effect, as coils with field installed
        RDS ordered from this point forward will come with an A2L piston and will
        NOT be allowed to be used on R410a systems.
    As a result, SCA is making the decision to remove the Flexcoil model dynamic
        insertion into program files side-by-side with A1 models.
        A2L models will be in their own product vlocks, explicitly added to strategies.

    -- 2024-10-18 (Joseph Carboni)


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
    not_available_txt = "Not Available"
    not_available = pd.Series([not_available_txt, not_available_txt])
    same_as_model_txt = "Same as Model Number"
    same_as_model = pd.Series([same_as_model_txt, same_as_model_txt])
    # flexcoil by replacement
    if series in ("HE", "HH", "HD"):
        if model_number.endswith("AP"):
            model_to_parse = model_number.replace("AP", "N")
        elif model_number[:2] == "CE" and not model_number.endswith("N"):
            model_to_parse = model_number + "N"
        elif model_number.endswith("N"):
            return same_as_model
        elif model_number.endswith("R"):
            model_to_parse = list(model_number)
            model_to_parse[4] = "1"
            model_to_parse[-1] = "N"
            model_to_parse = "".join(model_to_parse)
        else:
            return not_available
    # flexcoil by append
    elif series in ("MH", "V"):
        model_end = model_number[-1]
        if model_end not in ("R", "N"):
            model_to_parse = model_number + "N"
        elif model_end == "N":
            return same_as_model
        elif model_end == "R":
            model_to_parse = model_number[:-2] + "1N"
    else:
        return not_available

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
        if program_data.empty:
            return
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
            self.product_series_contained = {"CE", "CF", "LS"}

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
                ratings_regexes = row[row.index.str.contains("ratings")].dropna()
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
        series_prog_map: dict[str, CoilProgram | AirHandlerProgram]
        series_prog_map = {
            "S": AirHandlerProgram,
            "F": AirHandlerProgram,
            "B": AirHandlerProgram,
            "CP": AirHandlerProgram,
            "CF": AirHandlerProgram,
            "LS": AirHandlerProgram,
            "HE": CoilProgram,
            "MH": CoilProgram,
            "HH": CoilProgram,
            "V": CoilProgram,
            "SC": CoilProgram,
            "CE": CoilProgram,
        }
        for prog in self.progs:
            if not isinstance(prog, series_prog_map[series]):
                continue
            try:
                sample_series = prog._data[Fields.SERIES.value] == series
                if len(series) > 1:
                    sample_series_alt_1 = prog._data[
                        Fields.MODEL_NUMBER.value
                    ].str.startswith(series)
                    sample_series_alt_2 = prog._data[
                        Fields.PRIVATE_LABEL.value
                    ].str.startswith(series)
                    mask = (
                        (sample_series) | (sample_series_alt_1) | (sample_series_alt_2)
                    )
                else:
                    mask = sample_series

                sample_m = prog._data.loc[mask, Fields.MODEL_NUMBER.value].dropna()
                sample_m = sample_m.sample(n=min(len(sample_m), 1))
                sample_pl = prog._data.loc[mask, Fields.PRIVATE_LABEL.value].dropna()
                sample_pl = sample_pl.sample(n=min(len(sample_pl), 1))
                sample: str
                if not sample_pl.empty:
                    sample = sample_pl.item()
                elif not sample_m.empty:
                    sample = sample_m.item()
                else:
                    raise Exception(
                        "Both model number and private label samples returned empty"
                    )
            except Exception as e:
                logger.warning("unable to obtain sample from series " f"{series}: {e}")
                continue
            else:
                result = sample.strip()
                if result[-1] not in ("R", "N"):
                    if series in ("MH", "V", "B", "F", "S", "CP", "CE", "CF"):
                        result += "R"
                    elif series in ("HE", "HH", "HD"):
                        result = result.replace("AP", "R")
                return result
