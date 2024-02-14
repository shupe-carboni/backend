from datetime import datetime
import re
import pandas as pd
from adp_models import Fields

class Program:
    def __init__(self, customer: str, data: pd.DataFrame, ratings: pd.DataFrame) -> None:
        self._data = data
        self.customer = customer
        self.product_categories = data[Fields.CATEGORY.formatted()].drop_duplicates()
        self.ratings = ratings
        if data[Fields.PRIVATE_LABEL.formatted()].isna().all():
            self.product_series_contained = set(data[Fields.SERIES.formatted()].unique().tolist())
        else:
            self.product_series_contained = {'CE'}

    def category_data(self, category) -> pd.DataFrame:
        data = self._data.loc[self._data[Fields.CATEGORY.formatted()] == category,:]
        return (
            data
                .dropna(how='all', axis=1)
                .drop(columns=[
                    Fields.CATEGORY.formatted()
                    ])
        )


class CoilProgram(Program):

    def __init__(self, customer: str, data: pd.DataFrame, ratings: pd.DataFrame) -> None:
        super().__init__(customer, data, ratings)
        self.length_or_depth = Fields.DEPTH.formatted()
        self.model_number = Fields.MODEL_NUMBER.formatted()

    def __str__(self) -> str:
        return "Coils"

    def features(self):
        return [
            self.model_number,
            Fields.PALLET_QTY.formatted(),
            Fields.WIDTH.formatted(),
            self.length_or_depth,
            Fields.HEIGHT.formatted(),
            Fields.WEIGHT.formatted(),
            Fields.CABINET.formatted(),
            Fields.METERING.formatted(),
            Fields.NET_PRICE.formatted()
        ] 

    def category_data(self, category) -> pd.DataFrame:
        data = super().category_data(category)
        if Fields.LENGTH.formatted() in data.columns:
            self.length_or_depth = Fields.LENGTH.formatted()
        else:
            self.length_or_depth = Fields.DEPTH.formatted()

        if Fields.PRIVATE_LABEL.formatted() in data.columns:
            self.model_number = Fields.PRIVATE_LABEL.formatted()
        else:
            self.model_number = Fields.MODEL_NUMBER.formatted()

        data = data[self.features()].rename(
                columns={'Private Label': 'Model Number'}
            )
        return data

class AirHandlerProgram(Program):

    def __init__(self, customer: str, data: pd.DataFrame, ratings: pd.DataFrame) -> None:
        super().__init__(customer, data, ratings)
        self.pallet_or_min = Fields.MIN_QTY.formatted()
        self.model_number = Fields.MODEL_NUMBER.formatted()
    
    def __str__(self) -> str:
        return "Air Handlers"

    def features(self):
            return [
            self.model_number,
            self.pallet_or_min,
            Fields.WIDTH.formatted(), 
            Fields.DEPTH.formatted(), 
            Fields.HEIGHT.formatted(),
            Fields.WEIGHT.formatted(),
            Fields.HEAT.formatted(),
            Fields.METERING.formatted(),
            Fields.NET_PRICE.formatted()
        ]

    def category_data(self, category) -> pd.DataFrame:
        data = super().category_data(category)
        if Fields.WEIGHT.formatted() not in data.columns:
            data[Fields.WEIGHT.formatted()] = '--'

        if Fields.PRIVATE_LABEL.formatted() in data.columns:
            self.model_number = Fields.PRIVATE_LABEL.formatted()
        else:
            self.model_number = Fields.MODEL_NUMBER.formatted()

        if Fields.PALLET_QTY.formatted() in data.columns:
            self.pallet_or_min = Fields.PALLET_QTY.formatted()
        else:
            self.pallet_or_min = Fields.MIN_QTY.formatted()
        
        features = self.features()

        data = data[features].rename(
                columns={'Private Label': 'Model Number'}
            )
        return data

class CustomerProgram:
    def __init__(
            self,
            logo_path: str,
            coils: list[CoilProgram]=None,
            air_handlers: list[AirHandlerProgram]=None,
            parts: pd.DataFrame=None,
            terms: dict[str, str|dict]=None
        ) -> None:
        if not (coils or air_handlers):
            raise Exception("Either a Coil Program or an Air Handler Program are required")
        elif coils:
            self.customer = coils[0].customer
        else:
            self.customer = air_handlers[0].customer
       
        self.ratings = pd.DataFrame()
        self.progs: list[Program] = [*coils, *air_handlers]
        self.progs = [prog for prog in self.progs if prog]
        self.series_contained = set()
        for prog in self.progs:
            prog_ratings = prog.ratings
            self.ratings = pd.concat([self.ratings, prog_ratings]).drop_duplicates()
            self.series_contained |= prog.product_series_contained
        self.filter_ratings()
        self.terms = terms
        self.parts = parts
        self.logo_path = logo_path

    def __iter__(self):
        return iter(self.progs)

    def __str__(self) -> str:
        return self.new_file_name()

    def new_file_name(self) -> str:
        TODAY = datetime.today().date()
        customer_name = self.customer.title()
        if "'" in customer_name:
            # title() capitalizes or leaves alone letters after an apostrophe
            customer_name = re.sub(r"(?<=')([^'])", lambda match: match.group(1).lower(), customer_name)
        return f"{customer_name} 2024 Strategy {TODAY}.xlsx".replace('/','_')

    def filter_ratings(self) -> None:
        if not self.ratings.empty:
            registered_filter = self.ratings['AHRI Ref Number'] > 0
            registered = self.ratings[registered_filter]
            unregistered = self.ratings[~registered_filter]
            def in_program(value: str) -> bool:
                if not value:
                    return False
                for prog in self.progs:
                    ratings_models: pd.Series = prog._data.loc[:,prog._data.columns.str.contains('Ratings')].stack(future_stack=True)
                    ratings_models = ratings_models.drop_duplicates().dropna().reset_index(drop=True)
                    if ratings_models.apply(lambda ref: re.match(ref, value) is not None).any():
                        return True
                return False
            registered['in_prog'] = registered['Coil Model Number'].apply(in_program)
            unregistered['in_prog'] = unregistered['IndoorModel'].apply(in_program)
            registered = registered[registered['in_prog'] == True]
            unregistered = unregistered[unregistered['in_prog'] == True]
            self.ratings = pd.concat([registered, unregistered]).drop(columns='in_prog')