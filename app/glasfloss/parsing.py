from enum import StrEnum


class ModelTypes(StrEnum):
    GDS = "GDS DISPOSABLE FILTERS"
    ZLP = "Z-LINE STANDARD PLEAT FILTERS"
    HVP = "Z-LINE HV PLEAT FILTERS"
    M11 = "Z-LINE MERV 11 PLEAT FILTERS"
    M13 = "Z-LINE MERV 13 PLEAT FILTERS"


class ModelParser:
    def __init__(
        self,
        model_type: str,
    ): ...
