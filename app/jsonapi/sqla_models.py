"""Database Table Models with relaltionships defined 
    between models and jsonapi names defined separately"""

from sqlalchemy import (
    Column,
    Float,
    Integer,
    String,
    Boolean,
    DateTime,
    TEXT,
    ForeignKey,
    ARRAY,
    BigInteger,
    exists,
)
from sqlalchemy.orm import (
    declarative_base,
    relationship,
    Query,
    aliased,
    Mapped,
    mapped_column,
)
from app.jsonapi.sqla_jsonapi_ext import JSONAPI_
from app.db import Stage

Base = declarative_base()


class ADPAHProgram(Base):
    __tablename__ = "adp_ah_programs"
    __jsonapi_type_override__ = "adp-ah-programs"
    ## fields
    category = Column(TEXT)
    model_number = Column(TEXT)
    private_label = Column(TEXT)
    mpg = Column(TEXT)
    series = Column(TEXT)
    tonnage = Column(Integer)
    pallet_qty = Column(Integer)
    min_qty = Column(Integer)
    width = Column(Float)
    depth = Column(Float)
    height = Column(Float)
    weight = Column(Integer)
    metering = Column(TEXT)
    motor = Column(TEXT)
    heat = Column(TEXT)
    zero_discount_price = Column(Float)
    material_group_discount = Column(Float)
    material_group_net_price = Column(Float)
    snp_discount = Column(Float)
    snp_price = Column(Float)
    net_price = Column(Float)
    ratings_ac_txv = Column(TEXT)
    ratings_hp_txv = Column(TEXT)
    ratings_piston = Column(TEXT)
    ratings_field_txv = Column(TEXT)
    effective_date = Column(DateTime)
    last_file_gen = Column(DateTime)
    id = Column(Integer, primary_key=True)
    stage: Mapped[Stage] = mapped_column()
    customer_id = Column(Integer, ForeignKey("adp_customers.id"))
    ## relationships
    adp_customers = relationship("ADPCustomer", back_populates=__tablename__)

    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int] = None) -> Query:
        adptoloc = aliased(ADPAliasToSCACustomerLocation)
        exists_subquery = exists().where(
            adptoloc.adp_customer_id == ADPAHProgram.customer_id,
            adptoloc.sca_customer_location_id.in_(ids),
        )
        return q.where(exists_subquery)


class ADPCoilProgram(Base):
    __tablename__ = "adp_coil_programs"
    __jsonapi_type_override__ = "adp-coil-programs"
    ## fields
    category = Column(TEXT)
    model_number = Column(TEXT)
    private_label = Column(TEXT)
    mpg = Column(TEXT)
    series = Column(TEXT)
    tonnage = Column(Integer)
    pallet_qty = Column(Integer)
    width = Column(Float)
    depth = Column(Float)
    height = Column(Float)
    length = Column(Float)
    weight = Column(Integer)
    metering = Column(TEXT)
    cabinet = Column(TEXT)
    zero_discount_price = Column(Float)
    material_group_discount = Column(Float)
    material_group_net_price = Column(Float)
    snp_discount = Column(Float)
    snp_price = Column(Float)
    net_price = Column(Float)
    ratings_ac_txv = Column(TEXT)
    ratings_hp_txv = Column(TEXT)
    ratings_piston = Column(TEXT)
    ratings_field_txv = Column(TEXT)
    effective_date = Column(DateTime)
    last_file_gen = Column(DateTime)
    id = Column(Integer, primary_key=True)
    stage: Mapped[Stage] = mapped_column()
    customer_id = Column(Integer, ForeignKey("adp_customers.id"))
    ## relationships
    adp_customers = relationship("ADPCustomer", back_populates=__tablename__)

    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int] = None) -> Query:
        adptoloc = aliased(ADPAliasToSCACustomerLocation)
        exists_subquery = exists().where(
            adptoloc.adp_customer_id == ADPCoilProgram.customer_id,
            adptoloc.sca_customer_location_id.in_(ids),
        )
        return q.where(exists_subquery)


class ADPAliasToSCACustomerLocation(Base):
    __tablename__ = "adp_alias_to_sca_customer_locations"
    ## fields
    id = Column(Integer, primary_key=True)
    adp_customer_id = Column(Integer, ForeignKey("adp_customers.id"))
    sca_customer_location_id = Column(Integer, ForeignKey("sca_customer_locations.id"))
    ## relationships
    adp_customers = relationship("ADPCustomer", back_populates=__tablename__)
    customer_locations = relationship(
        "SCACustomerLocation", back_populates=__tablename__
    )

    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int] = None) -> Query:
        return q


class ADPCustomer(Base):
    __tablename__ = "adp_customers"
    __jsonapi_type_override__ = "adp-customers"
    ## fields
    adp_alias = Column(TEXT, unique=True)
    customer = Column(TEXT)
    sca_id = Column(Integer, ForeignKey("sca_customers.id"))
    id = Column(Integer, primary_key=True)
    preferred_parts = Column(Boolean)
    ## relationships
    customers = relationship("SCACustomer", back_populates=__tablename__)
    adp_coil_programs = relationship("ADPCoilProgram", back_populates=__tablename__)
    adp_ah_programs = relationship("ADPAHProgram", back_populates=__tablename__)
    adp_program_ratings = relationship("ADPProgramRating", back_populates=__tablename__)
    adp_alias_to_sca_customer_locations = relationship(
        "ADPAliasToSCACustomerLocation", back_populates=__tablename__
    )
    adp_material_group_discounts = relationship(
        "ADPMaterialGroupDiscount", back_populates=__tablename__
    )
    adp_snps = relationship("ADPSNP", back_populates=__tablename__)
    adp_program_parts = relationship("ADPProgramPart", back_populates=__tablename__)
    adp_quotes = relationship("ADPQuote", back_populates=__tablename__)

    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int] = None) -> Query:
        if not ids:
            return q
        adptoloc = aliased(ADPAliasToSCACustomerLocation)
        exists_subquery = exists().where(
            adptoloc.adp_customer_id == ADPCustomer.id,
            adptoloc.sca_customer_location_id.in_(ids),
        )
        return q.where(exists_subquery)


class ADPCustomerTerms(Base):
    __tablename__ = "adp_customer_terms"
    __jsonapi_type_override__ = "adp-customer-terms"
    ## fields
    sca_id = Column(Integer, ForeignKey("sca_customers.id"))
    terms = Column(TEXT)
    ppf = Column(Integer)
    effective_date = Column(DateTime)
    id = Column(Integer, primary_key=True)
    ## relationships
    customers = relationship("SCACustomer", back_populates=__tablename__)

    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int] = None) -> Query:
        if not ids:
            return q
        adptoloc = aliased(ADPAliasToSCACustomerLocation)
        exists_subquery = exists().where(
            adptoloc.sca_customer_location_id == ADPCustomerTerms.sca_id,
            adptoloc.sca_customer_location_id.in_(ids),
        )
        return q.where(exists_subquery)


class SCACustomer(Base):
    __tablename__ = "sca_customers"
    __jsonapi_type_override__ = "customers"
    ## fields
    id = Column(Integer, primary_key=True)
    name = Column(String)
    logo = Column(String)
    domains = Column(ARRAY(String))
    buying_group = Column(String)
    ## relationships
    adp_customer_terms = relationship(
        "ADPCustomerTerms", back_populates=__jsonapi_type_override__
    )
    adp_customers = relationship(
        "ADPCustomer", back_populates=__jsonapi_type_override__
    )
    customer_locations = relationship(
        "SCACustomerLocation", back_populates=__jsonapi_type_override__
    )

    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int] = None) -> Query:
        return q


class ADPMaterialGroupDiscount(Base):
    __tablename__ = "adp_material_group_discounts"
    __jsonapi_type_override__ = "adp-material-group-discounts"
    ## fields
    id = Column(Integer, primary_key=True)
    mat_grp = Column(TEXT)
    discount = Column(Float)
    stage: Mapped[Stage] = mapped_column()
    effective_date = Column(DateTime)
    customer_id = Column(Integer, ForeignKey("adp_customers.id"))
    ## relationships
    adp_customers = relationship("ADPCustomer", back_populates=__tablename__)

    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int] = None) -> Query:
        if not ids:
            return q
        adptoloc = aliased(ADPAliasToSCACustomerLocation)
        exists_subquery = exists().where(
            adptoloc.adp_customer_id == ADPMaterialGroupDiscount.customer_id,
            adptoloc.sca_customer_location_id.in_(ids),
        )
        return q.where(exists_subquery)


class ADPMaterialGroup(Base):
    __tablename__ = "adp_material_groups"
    __jsonapi_type_override__ = "adp-material-groups"
    ## fields
    id = Column(Integer, primary_key=True)
    mat_grp = Column(String(2))
    series = Column(String(2))
    mat = Column(TEXT)
    config = Column(TEXT)
    description = Column(TEXT)
    ## relationships
    # None
    ## filtering
    # None


class ADPProgramRating(Base):
    __tablename__ = "adp_program_ratings"
    __jsonapi_type_override__ = "adp-program-ratings"

    ## fields
    ahrinumber = Column("AHRINumber", TEXT)
    outdoor_model = Column("OutdoorModel", TEXT)
    oem_name = Column("OEMName", TEXT)
    indoor_model = Column("IndoorModel", TEXT)
    furnace_model = Column("FurnaceModel", TEXT)
    oem_name_1 = Column("OEM Name", TEXT)
    m1 = Column("M1", TEXT)
    status = Column("Status", TEXT)
    oem_series = Column("OEM Series", TEXT)
    adp_series = Column("ADP Series", TEXT)
    model_number = Column("Model Number", TEXT)
    coil_model_number = Column("Coil Model Number", TEXT)
    furnace_model_number = Column("Furnace Model Number", TEXT)
    seer = Column("SEER", Float)
    eer = Column("EER", Float)
    capacity = Column("Capacity", Float)
    _47o = Column("47o", Float)
    _17o = Column("17o", Float)
    hspf = Column("HSPF", Float)
    seer2 = Column("SEER2", Float)
    eer2 = Column("EER2", Float)
    capacity2 = Column("Capacity2", Float)
    _47o2 = Column("47o2", Float)
    hspf2 = Column("HSPF2", Float)
    ahri_ref_number = Column("AHRI Ref Number", BigInteger)
    region = Column("Region", TEXT)
    effective_date = Column(DateTime)
    customer_id = Column(Integer, ForeignKey("adp_customers.id"))
    seer2_as_submitted = Column(Float)
    eer95f2_as_submitted = Column(Float)
    capacity2_as_submitted = Column(Float)
    hspf2_as_submitted = Column(Float)
    id = Column(Integer, primary_key=True)
    ## relationships
    adp_customers = relationship("ADPCustomer", back_populates=__tablename__)

    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int] = None) -> Query:
        if not ids:
            return q
        adptoloc = aliased(ADPAliasToSCACustomerLocation)
        exists_subquery = exists().where(
            adptoloc.adp_customer_id == ADPProgramRating.customer_id,
            adptoloc.sca_customer_location_id.in_(ids),
        )
        return q.where(exists_subquery)


class ADPPricingPart(Base):
    __tablename__ = "adp_pricing_parts"
    __jsonapi_type_override__ = "adp-pricing-parts"
    ## fields
    id = Column(Integer)
    part_number = Column(String, nullable=False, primary_key=True)
    description = Column(TEXT)
    pkg_qty = Column(Integer)
    preferred = Column(Integer)
    standard = Column(Integer)
    ## relationships
    adp_program_parts = relationship("ADPProgramPart", back_populates=__tablename__)

    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int] = None) -> Query:
        return q


class ADPProgramPart(Base):
    __tablename__ = "adp_program_parts"
    __jsonapi_type_override__ = "adp-program-parts"
    ## fields
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("adp_customers.id"))
    part_number = Column(String, ForeignKey("adp_pricing_parts.part_number"))
    ## relationships
    adp_pricing_parts = relationship("ADPPricingPart", back_populates=__tablename__)
    adp_customers = relationship("ADPCustomer", back_populates=__tablename__)

    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int] = None) -> Query:
        if not ids:
            return q
        adptoloc = aliased(ADPAliasToSCACustomerLocation)
        exists_subquery = exists().where(
            adptoloc.adp_customer_id == ADPProgramPart.customer_id,
            adptoloc.sca_customer_location_id.in_(ids),
        )
        return q.where(exists_subquery)


class ADPQuote(Base):
    __tablename__ = "adp_quotes"
    __jsonapi_type_override__ = "adp-quotes"
    ## fields
    id = Column(Integer, primary_key=True)
    adp_quote_id = Column(String, unique=True)
    place_id = Column(Integer, ForeignKey("sca_places.id"))
    adp_customer_id = Column(Integer, ForeignKey("adp_customers.id"))
    job_name = Column(String)
    created_at = Column(DateTime)
    expires_at = Column(DateTime)
    status: Mapped[Stage] = mapped_column()
    quote_doc = Column(TEXT, unique=True)
    plans_doc = Column(TEXT)
    customer_location_id = Column(Integer, ForeignKey("sca_customer_locations.id"))
    ## relationships
    places = relationship("SCAPlace", back_populates=__tablename__)
    adp_customers = relationship("ADPCustomer", back_populates=__tablename__)
    customer_locations = relationship(
        "SCACustomerLocation", back_populates=__tablename__
    )
    adp_quote_products = relationship("ADPQuoteProduct", back_populates=__tablename__)

    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int] = None) -> Query:
        if not ids:
            return q
        adptoloc = aliased(ADPAliasToSCACustomerLocation)
        exists_subquery = exists().where(
            adptoloc.adp_customer_id == ADPQuote.adp_customer_id,
            adptoloc.sca_customer_location_id.in_(ids),
        )
        return q.where(exists_subquery)


class SCACustomerLocation(Base):
    __tablename__ = "sca_customer_locations"
    __jsonapi_type_override__ = "customer-locations"
    __tablename_alt__ = "customer_locations"
    ## fields
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("sca_customers.id"))
    place_id = Column(Integer, ForeignKey("sca_places.id"))
    hq = Column(Boolean)
    dc = Column(Boolean)
    serviced_by_id = Column(Integer, ForeignKey("sca_customer_locations.id"))
    ## relationships
    serviced_by = relationship("SCACustomerLocation")
    adp_alias_to_sca_customer_locations = relationship(
        "ADPAliasToSCACustomerLocation", back_populates=__tablename_alt__
    )
    adp_quotes = relationship("ADPQuote", back_populates=__tablename_alt__)
    customers = relationship("SCACustomer", back_populates=__tablename_alt__)
    places = relationship("SCAPlace", back_populates=__tablename_alt__)
    manager_map = relationship("SCAManagerMap", back_populates=__tablename_alt__)
    users = relationship("SCAUser", back_populates=__tablename_alt__)

    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int] = None) -> Query:
        if not ids:
            ids = list()
        return q.where(SCACustomerLocation.id.in_(ids))


class ADPSNP(Base):
    __tablename__ = "adp_snps"
    __jsonapi_type_override__ = "adp-snps"
    ## fields
    id = Column(Integer, primary_key=True)
    model = Column(TEXT)
    price = Column(Float)
    stage: Mapped[Stage] = mapped_column()
    effective_date = Column(DateTime)
    customer_id = Column(Integer, ForeignKey("adp_customers.id"))
    ## relationships
    adp_customers = relationship("ADPCustomer", back_populates=__tablename__)

    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int] = None) -> Query:
        if not ids:
            return q
        adptoloc = aliased(ADPAliasToSCACustomerLocation)
        exists_subquery = exists().where(
            adptoloc.adp_customer_id == ADPSNP.customer_id,
            adptoloc.sca_customer_location_id.in_(ids),
        )
        return q.where(exists_subquery)


class ADPQuoteProduct(Base):
    __tablename__ = "adp_quote_products"
    __jsonapi_type_override__ = "adp-quote-products"
    ## fields
    id = Column(Integer, primary_key=True)
    tag = Column(String, nullable=False)
    qty = Column(Integer, nullable=False)
    price = Column(Float)
    model_number = Column(String)
    comp_model = Column(String)
    adp_quote_id = Column(Integer, ForeignKey("adp_quotes.id"))
    ## relationships
    adp_quotes = relationship("ADPQuote", back_populates=__tablename__)

    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int] = None) -> Query:
        return q


class SCAPlace(Base):
    __tablename__ = "sca_places"
    __jsonapi_type_override__ = "places"
    ## fields
    id = Column(Integer, primary_key=True)
    name = Column(String)
    state = Column(String(2))
    lat = Column(Float)
    long = Column(Float)
    ## relationships
    adp_quotes = relationship("ADPQuote", back_populates=__jsonapi_type_override__)
    customer_locations = relationship(
        "SCACustomerLocation", back_populates=__jsonapi_type_override__
    )

    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int] = None) -> Query:
        return q


class SCAManagerMap(Base):
    __tablename__ = "sca_manager_map"
    __jsonapi_type_override__ = "manager-map"
    __tablename_alt__ = "manager_map"
    ## fields
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("sca_users.id"))
    customer_location_id = Column(Integer, ForeignKey("sca_customer_locations.id"))
    ## Relationships
    customer_locations = relationship(
        "SCACustomerLocation", back_populates=__tablename_alt__
    )
    users = relationship("SCAUser", back_populates=__tablename_alt__)

    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int] = None) -> Query:
        if not ids:
            return q
        return q.where(SCAManagerMap.customer_location_id.in_(ids))


class SCAUser(Base):
    __tablename__ = "sca_users"
    __jsonapi_type_override__ = "users"
    ## fields
    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)
    customer_location_id = Column(Integer, ForeignKey("sca_customer_locations.id"))
    ## relationships
    customer_locations = relationship(
        "SCACustomerLocation", back_populates=__jsonapi_type_override__
    )
    manager_map = relationship(
        "SCAManagerMap", back_populates=__jsonapi_type_override__
    )

    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int] = None) -> Query:
        if not ids:
            return q
        return q.where(SCAUser.customer_location_id.in_(ids))


class SCAVendor(Base):
    __tablename__ = "sca_vendors"
    __jsonapi_type_override__ = "vendors"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    headquarters = Column(String)
    description = Column(TEXT)
    phone = Column(BigInteger)
    logo_path = Column(String)
    # relationships
    info = relationship("SCAVendorInfo", back_populates=__jsonapi_type_override__)

    # filtering
    def apply_customer_location_filtering(q: Query, ids: list[int] = None) -> Query:
        return q


class SCAVendorInfo(Base):
    __tablename__ = "sca_vendors_info"
    __jsonapi_type_override__ = "info"
    id = Column(Integer, primary_key=True)
    vendor_id = Column(Integer, ForeignKey("sca_vendors.id"))
    category = Column(TEXT)
    content = Column(TEXT)
    # relationships
    vendors = relationship("SCAVendor", back_populates=__jsonapi_type_override__)

    # filtering
    def apply_customer_location_filtering(q: Query, ids: list[int] = None) -> Query:
        return q


serializer = JSONAPI_(Base)
