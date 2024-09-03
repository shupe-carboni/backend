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
    select,
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
from app.db import Stage, FriedrichPriceLevels, FriedrichMarketType
from functools import partial

Base = declarative_base()
QuerySet = dict[str, str]


def permitted_customer_location_ids(email: str) -> QuerySet:
    customer_locations = aliased(SCACustomerLocation)
    customer_locations_2 = aliased(SCACustomerLocation)
    users = aliased(SCAUser)
    manager_map = aliased(SCAManagerMap)
    user_only = select(customer_locations.id).where(
        exists().where(
            users.email == email, users.customer_location_id == customer_locations.id
        )
    )

    manager = select(customer_locations.id).where(
        exists().where(
            users.email == email,
            manager_map.user_id == users.id,
            manager_map.customer_location_id == customer_locations.id,
        )
    )

    admin = select(customer_locations.id).where(
        exists().where(
            users.email == email,
            customer_locations_2.id == users.customer_location_id,
            customer_locations_2.customer_id == customer_locations.customer_id,
        )
    )
    return {
        "sql_admin": str(admin),
        "sql_manager": str(manager),
        "sql_user_only": str(user_only),
    }


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
    adp_ah_programs_changelog = relationship(
        "ADPAHProgramChangelog",
        back_populates=__tablename__,
        cascade="all,delete",
    )

    ## GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        adptoloc = aliased(ADPAliasToSCACustomerLocation)
        exists_subquery = exists().where(
            adptoloc.adp_customer_id == ADPAHProgram.customer_id,
            adptoloc.sca_customer_location_id.in_(ids),
        )
        return q.where(exists_subquery)

    ## primary id lookup
    def permitted_primary_resource_ids(email: str) -> QuerySet:
        return adp_customer_primary_id_queries(email=email)


class ADPAHProgramChangelog(Base):
    __tablename__ = "adp_ah_programs_changelog"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    ## fields
    id = Column(Integer, primary_key=True)
    record_id = Column(Integer, ForeignKey("adp_ah_programs.id"))
    prior_status: Mapped[Stage] = mapped_column()
    new_status: Mapped[Stage] = mapped_column()
    date = Column(DateTime)
    username = Column(String)
    comment = Column(TEXT)
    ## relationships
    adp_ah_programs = relationship("ADPAHProgram", back_populates=__tablename__)

    ## GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        return q

    ## primary id lookup
    def permitted_primary_resource_ids(email: str) -> str:
        return str()


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
    adp_coil_programs_changelog = relationship(
        "ADPCoilProgramChangelog",
        back_populates=__tablename__,
        cascade="all,delete",
    )

    ## GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        adptoloc = aliased(ADPAliasToSCACustomerLocation)
        exists_subquery = exists().where(
            adptoloc.adp_customer_id == ADPCoilProgram.customer_id,
            adptoloc.sca_customer_location_id.in_(ids),
        )
        return q.where(exists_subquery)

    ## primary id lookup
    def permitted_primary_resource_ids(email: str) -> QuerySet:
        return adp_customer_primary_id_queries(email=email)


class ADPCoilProgramChangelog(Base):
    __tablename__ = "adp_coil_programs_changelog"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    ## fields
    id = Column(Integer, primary_key=True)
    record_id = Column(Integer, ForeignKey("adp_coil_programs.id"))
    prior_status: Mapped[Stage] = mapped_column()
    new_status: Mapped[Stage] = mapped_column()
    date = Column(DateTime)
    username = Column(String)
    comment = Column(TEXT)
    ## relationships
    adp_coil_programs = relationship("ADPCoilProgram", back_populates=__tablename__)

    ## GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        return q


class ADPAliasToSCACustomerLocation(Base):
    __tablename__ = "adp_alias_to_sca_customer_locations"
    __jsonapi_type_override__ = "adp-alias-to-sca-customer-locations"
    ## fields
    id = Column(Integer, primary_key=True)
    adp_customer_id = Column(Integer, ForeignKey("adp_customers.id"))
    sca_customer_location_id = Column(Integer, ForeignKey("sca_customer_locations.id"))
    ## relationships
    adp_customers = relationship("ADPCustomer", back_populates=__tablename__)
    customer_locations = relationship(
        "SCACustomerLocation", back_populates=__tablename__
    )

    ## GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
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

    ## GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
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

    ## GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        adptoloc = aliased(ADPAliasToSCACustomerLocation)
        customer_locations = aliased(SCACustomerLocation)
        exists_subquery = exists().where(
            customer_locations.customer_id == ADPCustomerTerms.sca_id,
            adptoloc.sca_customer_location_id == customer_locations.id,
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
    friedrich_customers = relationship(
        "FriedrichCustomer", back_populates=__jsonapi_type_override__
    )

    ## GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        customerloc = aliased(SCACustomerLocation)
        exists_subquery = exists().where(
            customerloc.id.in_(ids), customerloc.customer_id == SCACustomer.id
        )
        return q.where(exists_subquery)


class ADPMaterialGroupDiscount(Base):
    __tablename__ = "adp_material_group_discounts"
    __jsonapi_type_override__ = "adp-material-group-discounts"
    ## fields
    id = Column(Integer, primary_key=True)
    mat_grp = Column(TEXT, ForeignKey("adp_material_groups.id"))
    discount = Column(Float)
    stage: Mapped[Stage] = mapped_column()
    effective_date = Column(DateTime)
    customer_id = Column(Integer, ForeignKey("adp_customers.id"))
    ## relationships
    adp_customers = relationship("ADPCustomer", back_populates=__tablename__)
    adp_material_groups = relationship("ADPMaterialGroup", back_populates=__tablename__)
    adp_material_group_discounts_changelog = relationship(
        "ADPMaterialGroupDiscountChangelog",
        back_populates=__tablename__,
        cascade="all,delete",
    )

    ## GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        adptoloc = aliased(ADPAliasToSCACustomerLocation)
        exists_subquery = exists().where(
            adptoloc.adp_customer_id == ADPMaterialGroupDiscount.customer_id,
            adptoloc.sca_customer_location_id.in_(ids),
        )
        return q.where(exists_subquery)

    ## primary id lookup
    def permitted_primary_resource_ids(email: str) -> QuerySet:
        return adp_customer_primary_id_queries(email=email)


class ADPMaterialGroupDiscountChangelog(Base):
    __tablename__ = "adp_material_group_discounts_changelog"
    __jsonapi_type_override__ = "adp-material-group-discounts-changelog"
    ## fields
    id = Column(Integer, primary_key=True)
    record_id = Column(Integer, ForeignKey("adp_material_group_discounts.id"))
    prior_status: Mapped[Stage] = mapped_column()
    new_status: Mapped[Stage] = mapped_column()
    date = Column(DateTime)
    username = Column(String)
    comment = Column(TEXT)
    ## relationships
    adp_material_group_discounts = relationship(
        "ADPMaterialGroupDiscount", back_populates=__tablename__
    )

    ## GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        return q

    ## primary id lookup
    def permitted_primary_resource_ids(email: str) -> QuerySet:
        return adp_customer_primary_id_queries(email=email)


class ADPMaterialGroup(Base):
    __tablename__ = "adp_material_groups"
    __jsonapi_type_override__ = "adp-material-groups"
    __modifiable_fields__ = None
    __primary_ref__ = None
    ## fields
    id = Column(String(2), primary_key=True)
    series = Column(String(2))
    mat = Column(TEXT)
    config = Column(TEXT)
    description = Column(TEXT)
    ## relationships
    adp_material_group_discounts = relationship(
        "ADPMaterialGroupDiscount", back_populates=__tablename__
    )

    ## GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        return q

    ## primary id lookup
    def permitted_primary_resource_ids(email: str) -> QuerySet:
        """This is a reference table, istelf a primary resource"""


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

    ## GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        adptoloc = aliased(ADPAliasToSCACustomerLocation)
        exists_subquery = exists().where(
            adptoloc.adp_customer_id == ADPProgramRating.customer_id,
            adptoloc.sca_customer_location_id.in_(ids),
        )
        return q.where(exists_subquery)

    ## primary id lookup
    def permitted_primary_resource_ids(email: str) -> QuerySet:
        return adp_customer_primary_id_queries(email=email)


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

    ## GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
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

    ## GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        adptoloc = aliased(ADPAliasToSCACustomerLocation)
        exists_subquery = exists().where(
            adptoloc.adp_customer_id == ADPProgramPart.customer_id,
            adptoloc.sca_customer_location_id.in_(ids),
        )
        return q.where(exists_subquery)

    ## object id queries
    def permitted_primary_resource_ids(email: str) -> QuerySet:
        return adp_customer_primary_id_queries(email=email)


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

    ## GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        adptoloc = aliased(ADPAliasToSCACustomerLocation)
        exists_subquery = exists().where(
            adptoloc.adp_customer_id == ADPQuote.adp_customer_id,
            adptoloc.sca_customer_location_id.in_(ids),
        )
        return q.where(exists_subquery)

    ## primary id lookup
    def permitted_primary_resource_ids(email: str) -> QuerySet:
        return adp_customer_primary_id_queries(email=email)


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
    friedrich_quotes = relationship("FriedrichQuote", back_populates=__tablename_alt__)
    customers = relationship("SCACustomer", back_populates=__tablename_alt__)
    places = relationship("SCAPlace", back_populates=__tablename_alt__)
    manager_map = relationship("SCAManagerMap", back_populates=__tablename_alt__)
    users = relationship("SCAUser", back_populates=__tablename_alt__)
    friedrich_customers_to_sca_customer_locations = relationship(
        "FriedrichCustomertoSCACustomerLocation", back_populates=__tablename_alt__
    )
    adp_alias_to_sca_customer_locations = relationship(
        "ADPAliasToSCACustomerLocation", back_populates=__tablename_alt__
    )

    ## GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        return q.where(SCACustomerLocation.id.in_(ids))

    ## primary id lookup
    def permitted_primary_resource_ids(email: str) -> QuerySet:
        return customers_primary_id_queries(email=email)


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
    adp_snps_changelog = relationship(
        "ADPSNPChangelog",
        back_populates=__tablename__,
        cascade="all,delete",
    )

    ## GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        adptoloc = aliased(ADPAliasToSCACustomerLocation)
        exists_subquery = exists().where(
            adptoloc.adp_customer_id == ADPSNP.customer_id,
            adptoloc.sca_customer_location_id.in_(ids),
        )
        return q.where(exists_subquery)

    ## primary id lookup
    def permitted_primary_resource_ids(email: str) -> QuerySet:
        return adp_customer_primary_id_queries(email=email)


class ADPSNPChangelog(Base):
    __tablename__ = "adp_snps_changelog"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    ## fields
    id = Column(Integer, primary_key=True)
    record_id = Column(Integer, ForeignKey("adp_snps.id"))
    prior_status: Mapped[Stage] = mapped_column()
    new_status: Mapped[Stage] = mapped_column()
    date = Column(DateTime)
    username = Column(String)
    comment = Column(TEXT)
    ## relationships
    adp_snps = relationship("ADPSNP", back_populates=__tablename__)

    ## GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        return q


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

    ## GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        return q

    ## primary id lookup
    def permitted_primary_resource_ids(email: str) -> QuerySet:
        return adp_quote_primary_id_queries(email=email)


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
    friedrich_quotes = relationship(
        "FriedrichQuote", back_populates=__jsonapi_type_override__
    )
    customer_locations = relationship(
        "SCACustomerLocation", back_populates=__jsonapi_type_override__
    )

    ## GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
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

    ## GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
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

    ## GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
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
    vendor_resource_mapping = relationship(
        "SCAVendorResourceMap", back_populates=__jsonapi_type_override__
    )

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
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

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        return q


class SCAVendorResourceMap(Base):
    __tablename__ = "sca_vendor_resource_mapping"
    __tablename_alt__ = "vendor_resource_mapping"
    __jsonapi_type_override__ = "vendor-resource-mapping"
    id = Column(Integer, primary_key=True)
    vendor_id = Column(String, ForeignKey("sca_vendors.id"), nullable=False)
    resource_type = Column(String, nullable=False)
    resource = Column(String, nullable=False)
    category_name = Column(String)
    # relationships
    vendors = relationship("SCAVendor", back_populates=__tablename_alt__)

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        return q


class FriedrichCustomer(Base):
    __tablename__ = "friedrich_customers"
    __jsonapi_type_override__ = "friedrich-customers"
    __modifiable_fields__ = ["name", "friedrich_acct_number"]
    __primary_ref__ = None

    id = Column(Integer, primary_key=True)
    sca_id = Column(Integer, ForeignKey("sca_customers.id"))
    name = Column(String)
    friedrich_acct_number = Column(String)
    # relationships
    customers = relationship("SCACustomer", back_populates=__tablename__)
    friedrich_pricing_special = relationship(
        "FriedrichPricingSpecial", back_populates=__tablename__
    )
    friedrich_customers_to_sca_customer_locations = relationship(
        "FriedrichCustomertoSCACustomerLocation", back_populates=__tablename__
    )
    friedrich_customer_price_levels = relationship(
        "FriedrichCustomerPriceLevel", back_populates=__tablename__
    )
    friedrich_pricing_customers = relationship(
        "FriedrichPricingCustomer", back_populates=__tablename__
    )
    friedrich_pricing_special_customers = relationship(
        "FriedrichPricingSpecialCustomer", back_populates=__tablename__
    )
    friedrich_quotes = relationship("FriedrichQuote", back_populates=__tablename__)

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        friedrichtoloc = aliased(FriedrichCustomertoSCACustomerLocation)
        exists_subquery = exists().where(
            friedrichtoloc.friedrich_customer_id == FriedrichCustomer.id,
            friedrichtoloc.sca_customer_location_id.in_(ids),
        )
        return q.where(exists_subquery)

    ## primary id lookup
    def permitted_primary_resource_ids(email: str) -> QuerySet:
        """Friedrich Customers is the main primary for Friedrivh"""


class FriedrichCustomertoSCACustomerLocation(Base):
    __tablename__ = "friedrich_customers_to_sca_customer_locations"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    id = Column(Integer, primary_key=True)
    friedrich_customer_id = Column(Integer, ForeignKey("friedrich_customers.id"))
    sca_customer_location_id = Column(Integer, ForeignKey("sca_customer_locations.id"))
    # relationships
    customer_locations = relationship(
        "SCACustomerLocation", back_populates=__tablename__
    )
    friedrich_customers = relationship(
        "FriedrichCustomer", back_populates=__tablename__
    )

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        friedrichtoloc = aliased(FriedrichCustomertoSCACustomerLocation)
        exists_subquery = exists().where(
            friedrichtoloc.id == FriedrichCustomertoSCACustomerLocation.id,
            friedrichtoloc.sca_customer_location_id.in_(ids),
        )
        return q.where(exists_subquery)

    ## primary id lookup
    def permitted_primary_resource_ids(email: str) -> QuerySet:
        return friedrich_customer_primary_id_queries(email=email)


class FriedrichProduct(Base):
    __tablename__ = "friedrich_products"
    __jsonapi_type_override__ = "friedrich-products"
    __modifiable_fields__ = ["description"]
    __primary_ref__ = None

    id = Column(Integer, primary_key=True)
    model_number = Column(String)
    description = Column(String)
    # relationships
    friedrich_pricing = relationship("FriedrichPricing", back_populates=__tablename__)
    friedrich_pricing_special = relationship(
        "FriedrichPricingSpecial", back_populates=__tablename__
    )
    friedrich_quote_products = relationship(
        "FriedrichQuoteProduct", back_populates=__tablename__
    )

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        return q

    ## primary id lookup
    def permitted_primary_resource_ids(email: str) -> None:
        """Products table is a reference table"""


class FriedrichPricing(Base):
    __tablename__ = "friedrich_pricing"
    __jsonapi_type_override__ = "friedrich-pricing"
    __modifiable_fields__ = ["price"]
    __primary_ref__ = None

    id = Column(Integer, primary_key=True)
    model_number_id = Column(Integer, ForeignKey("friedrich_products.id"))
    price_level: Mapped[FriedrichPriceLevels] = mapped_column()
    price = Column(Float)
    # relationships
    friedrich_products = relationship("FriedrichProduct", back_populates=__tablename__)
    friedrich_pricing_customers = relationship(
        "FriedrichPricingCustomer", back_populates=__tablename__
    )

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        friedrichtoloc = aliased(FriedrichCustomertoSCACustomerLocation)
        price_levels = aliased(FriedrichCustomerPriceLevel)
        exists_subquery = exists().where(
            price_levels.price_level == FriedrichPricing.price_level,
            price_levels.customer_id == friedrichtoloc.friedrich_customer_id,
            friedrichtoloc.sca_customer_location_id.in_(ids),
        )
        return q.where(exists_subquery)

    ## primary id lookup
    def permitted_primary_resource_ids(email: str) -> None:
        """Pricing table is a reference table"""


class FriedrichPricingSpecial(Base):
    __tablename__ = "friedrich_pricing_special"
    __jsonapi_type_override__ = "friedrich-pricing-special"
    __modifiable_fields__ = ["price", "customer_model_number"]
    __primary_ref__ = "friedrich_customers"

    id = Column(Integer, primary_key=True)
    model_number_id = Column(Integer, ForeignKey("friedrich_products.id"))
    customer_model_number = Column(String)
    price = Column(Float)
    customer_id = Column(Integer, ForeignKey("friedrich_customers.id"))
    # relationships
    friedrich_customers = relationship(
        "FriedrichCustomer", back_populates=__tablename__
    )
    friedrich_products = relationship("FriedrichProduct", back_populates=__tablename__)
    friedrich_pricing_special_customers = relationship(
        "FriedrichPricingSpecialCustomer", back_populates=__tablename__
    )

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        friedrichtoloc = aliased(FriedrichCustomertoSCACustomerLocation)
        exists_subquery = exists().where(
            friedrichtoloc.friedrich_customer_id == FriedrichPricingSpecial.customer_id,
            friedrichtoloc.sca_customer_location_id.in_(ids),
        )
        return q.where(exists_subquery)

    ## primary id lookup
    def permitted_primary_resource_ids(email: str) -> QuerySet:
        return friedrich_customer_primary_id_queries(email=email)


class FriedrichCustomerPriceLevel(Base):
    __tablename__ = "friedrich_customer_price_levels"
    __jsonapi_type_override__ = "friedrich-customer-price-levels"
    __modifiable_fields__ = ["price_level"]
    __primary_ref__ = "friedrich_customers"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("friedrich_customers.id"))
    price_level: Mapped[FriedrichPriceLevels] = mapped_column()
    # relationships
    friedrich_customers = relationship(
        "FriedrichCustomer", back_populates=__tablename__
    )

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        friedrichtoloc = aliased(FriedrichCustomertoSCACustomerLocation)
        exists_subquery = exists().where(
            friedrichtoloc.friedrich_customer_id
            == FriedrichCustomerPriceLevel.customer_id,
            friedrichtoloc.sca_customer_location_id.in_(ids),
        )
        return q.where(exists_subquery)

    ## primary id lookup
    def permitted_primary_resource_ids(email: str) -> QuerySet:
        return friedrich_customer_primary_id_queries(email=email)


class FriedrichPricingCustomer(Base):
    """mapping of curated pricing from FriedrichPricing. Like a favorites list"""

    __tablename__ = "friedrich_pricing_customers"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = None
    __primary_ref__ = "friedrich_customers"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("friedrich_customers.id"))
    price_id = Column(Integer, ForeignKey("friedrich_pricing.id"))
    # relationships
    friedrich_customers = relationship(
        "FriedrichCustomer", back_populates=__tablename__
    )
    friedrich_pricing = relationship("FriedrichPricing", back_populates=__tablename__)

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        friedrichtoloc = aliased(FriedrichCustomertoSCACustomerLocation)
        exists_subquery = exists().where(
            friedrichtoloc.friedrich_customer_id
            == FriedrichPricingCustomer.customer_id,
            friedrichtoloc.sca_customer_location_id.in_(ids),
        )
        return q.where(exists_subquery)

    ## primary id lookup
    def permitted_primary_resource_ids(email: str) -> QuerySet:
        return friedrich_customer_primary_id_queries(email=email)


class FriedrichPricingSpecialCustomer(Base):
    """mapping of curated pricing from FriedrichPricingSpecial. Like a favorites list"""

    __tablename__ = "friedrich_pricing_special_customers"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = None
    __primary_ref__ = "friedrich_customers"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("friedrich_customers.id"))
    price_id = Column(Integer, ForeignKey("friedrich_pricing_special.id"))
    # relationships
    friedrich_customers = relationship(
        "FriedrichCustomer", back_populates=__tablename__
    )
    friedrich_pricing_special = relationship(
        "FriedrichPricingSpecial", back_populates=__tablename__
    )

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        friedrichtoloc = aliased(FriedrichCustomertoSCACustomerLocation)
        exists_subquery = exists().where(
            friedrichtoloc.friedrich_customer_id
            == FriedrichPricingSpecialCustomer.customer_id,
            friedrichtoloc.sca_customer_location_id.in_(ids),
        )
        return q.where(exists_subquery)

    ## primary id lookup
    def permitted_primary_resource_ids(email: str) -> QuerySet:
        return friedrich_customer_primary_id_queries(email=email)


class FriedrichQuote(Base):

    __tablename__ = "friedrich_quotes"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = [
        "friedrich_quote_id",
        "job_name",
        "status",
        "plans_doc",
        "quote_doc",
    ]
    __primary_ref__ = "friedrich_customers"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("friedrich_customers.id"))
    customer_location_id = Column(Integer, ForeignKey("sca_customer_locations.id"))
    place_id = Column(Integer, ForeignKey("sca_places.id"))
    friedrich_quote_id = Column(Integer, unique=True)
    job_name = Column(String)
    status: Mapped[Stage] = mapped_column()
    new_construction = Column(Boolean)
    market_type: Mapped[FriedrichMarketType] = mapped_column()
    plans_doc = Column(String)
    quote_doc = Column(String, unique=True)
    created_at = Column(DateTime)
    expires_at = Column(DateTime)

    # relationships
    friedrich_customers = relationship(
        "FriedrichCustomer", back_populates=__tablename__
    )
    customer_locations = relationship(
        "SCACustomerLocation", back_populates=__tablename__
    )
    places = relationship("SCAPlace", back_populates=__tablename__)
    friedrich_quote_products = relationship(
        "FriedrichQuoteProduct", back_populates=__tablename__
    )

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        friedrichtoloc = aliased(FriedrichCustomertoSCACustomerLocation)
        exists_subquery = exists().where(
            friedrichtoloc.friedrich_customer_id == FriedrichQuote.customer_id,
            friedrichtoloc.sca_customer_location_id.in_(ids),
        )
        return q.where(exists_subquery)

    ## primary id lookup
    def permitted_primary_resource_ids(email: str) -> QuerySet:
        return friedrich_customer_primary_id_queries(email=email)


class FriedrichQuoteProduct(Base):

    __tablename__ = "friedrich_quote_products"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = [
        "tag",
        "qty",
        "product_id",
        "price",
    ]
    __primary_ref__ = "friedrich_customers"

    id = Column(Integer, primary_key=True)
    quote_id = Column(Integer, ForeignKey("friedrich_quotes.id"))
    tag = Column(String)
    qty = Column(Integer)
    product_id = Column(Integer, ForeignKey("friedrich_products.id"))
    price = Column(Float)

    # relationships
    friedrich_quotes = relationship("FriedrichQuote", back_populates=__tablename__)
    friedrich_products = relationship("FriedrichProduct", back_populates=__tablename__)

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        friedrichtoloc = aliased(FriedrichCustomertoSCACustomerLocation)
        quote_to_customer = aliased(FriedrichQuote)
        exists_subquery = exists().where(
            quote_to_customer.id == FriedrichQuoteProduct.quote_id,
            friedrichtoloc.friedrich_customer_id == quote_to_customer.customer_id,
            friedrichtoloc.sca_customer_location_id.in_(ids),
        )
        return q.where(exists_subquery)

    ## primary id lookup
    def permitted_primary_resource_ids(email: str) -> QuerySet:
        return friedrich_quote_primary_id_queries(email=email)


class HardcastProduct(Base):
    __tablename__ = "hardcast_products"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = None
    __primary_ref__ = None

    id = Column(Integer, primary_key=True)
    product_number = Column(Integer)
    category_id = Column(Integer, ForeignKey("hardcast_product_categories.id"))
    description = Column(String)
    code = Column(String)
    upc = Column(BigInteger)
    haz_mat = Column(Boolean)
    freight_class = Column(Float)
    stock = Column(ARRAY(String))
    weight = Column(Integer)
    case_qty = Column(Integer)
    case_price = Column(Float)


class HardcastProductCategory(Base):
    __tablename__ = "hardcast_product_categories"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = None
    __primary_ref__ = None

    id = Column(Integer, primary_key=True)
    category_l1 = Column(String)
    category_l2 = Column(String)
    category_l3 = Column(String)


# V2


class CustomerAdminMap(Base):
    __tablename__ = "customer_admin_map"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = None
    __primary_ref__ = None

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("sca_users.id"))
    customer_id = Column(String, ForeignKey("sca_customers.id"))

    ## GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        customer_locations = aliased(SCACustomerLocation)
        exists_subquery = exists().where(
            customer_locations.customer_id == CustomerAdminMap.id,
            customer_locations.id.in_(ids),
        )
        return q.where(exists_subquery)


class Vendor(Base):
    __tablename__ = "vendors"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = [
        "name",
        "headquarters",
        "description",
        "phone",
        "logo_path",
        "deleted_at",
    ]
    __primary_ref__ = None

    id = Column(String, primary_key=True)
    name = Column(String)
    headquarters = Column(String)
    description = Column(TEXT)
    phone = Column(BigInteger)
    logo_path = Column(String)
    deleted_at = Column(DateTime)
    # relationships
    vendors_attrs = relationship(
        "SCAVendorsAttr", back_populates=__jsonapi_type_override__
    )
    vendors_products = relationship(
        "SCAVendorsProduct", back_populates=__jsonapi_type_override__
    )
    vendors_product_classes = relationship(
        "SCAVendorsProductClass", back_populates=__jsonapi_type_override__
    )
    vendors_pricing_classes = relationship(
        "SCAVendorsPricingClass", back_populates=__jsonapi_type_override__
    )
    vendors_pricing_classes = relationship(
        "SCAVendorsPricingClass", back_populates=__jsonapi_type_override__
    )
    vendors_customers = relationship(
        "SCAVendorsCustomer", back_populates=__jsonapi_type_override__
    )

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        return q


class VendorsAttr(Base):
    __tablename__ = "vendors_attrs"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = ["value", "deleted_at"]
    __primary_ref__ = "vendors"

    id = Column(Integer, primary_key=True)
    vendor_id = Column(String, ForeignKey("vendors.id"))
    attr = Column(String)
    type = Column(String)
    value = Column(String)
    deleted_at = Column(DateTime)

    # relationships
    vendors = relationship("Vendor", back_populates=__jsonapi_type_override__)
    vendors_attrs_changelog = relationship(
        "VendorsAttrsChangelog", back_populates=__jsonapi_type_override__
    )

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        return q


class VendorsAttrsChangelog(Base):
    __tablename__ = "vendors_attrs_changelog"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = None
    __primary_ref__ = "vendors_attrs"

    id = Column(Integer, primary_key=True)
    attr_id = Column(String, ForeignKey("vendors_attrs.id"))
    type = Column(String)
    value = Column(String)
    timestamp = Column(DateTime)

    # relationships
    vendors_attrs = relationship(
        "VendorsAttr", back_populates=__jsonapi_type_override__
    )

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        return q


class VendorProduct(Base):
    __tablename__ = "vendors_products"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = ["vendor_product_description", "deleted_at"]
    __primary_ref__ = "vendors"

    id = Column(Integer, primary_key=True)
    vendor_id = Column(String, ForeignKey("vendors.id"))
    vendor_product_identifier = Column(String)
    vendor_product_description = Column(String)
    deleted_at = Column(DateTime)

    # relationships
    vendors = relationship("Vendor", back_populates=__jsonapi_type_override__)
    vendor_product_attrs = relationship(
        "VendorProductsAttr", back_populates=__jsonapi_type_override__
    )
    vendor_product_to_class_mapping = relationship(
        "VendorsProductToClassMapping", back_populates=__jsonapi_type_override__
    )

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        return q


class VendorsProductsAttr(Base):
    __tablename__ = "vendors_product_attrs"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = ["value", "deleted_at"]
    __primary_ref__ = "vendor_products"

    id = Column(Integer, primary_key=True)
    vendor_product_id = Column(Integer, ForeignKey("vendor_products.id"))
    attr = Column(String)
    type = Column(String)
    value = Column(String)
    deleted_at = Column(DateTime)

    # relationships
    vendor_products = relationship(
        "VendorProduct", back_populates=__jsonapi_type_override__
    )

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        return q


class VendorsProductClass(Base):
    __tablename__ = "vendor_product_classes"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = ["name", "rank", "deleted_at"]
    __primary_ref__ = "vendors"

    id = Column(Integer, primary_key=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    name = Column(String)
    rank = Column(Integer)
    deleted_at = Column(DateTime)

    # relationships
    vendors = relationship("Vendor", back_populates=__jsonapi_type_override__)
    vendors_attrs_changelog = relationship(
        "VendorsProductToClassMapping", back_populates=__jsonapi_type_override__
    )

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        return q


class VendorsProductToClassMapping(Base):
    __tablename__ = "vendor_product_to_class_mapping"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = ["deleted_at"]
    __primary_ref__ = "vendor_products"

    id = Column(Integer, primary_key=True)
    product_class_id = Column(Integer, ForeignKey("vendor_product_classes.id"))
    product_id = Column(Integer, ForeignKey("vendor_products.id"))
    deleted_at = Column(DateTime)

    # relationships
    vendors = relationship("Vendor", back_populates=__jsonapi_type_override__)
    vendor_product_classes = relationship(
        "VendorsProductClass", back_populates=__jsonapi_type_override__
    )
    vendor_product = relationship(
        "VendorProduct", back_populates=__jsonapi_type_override__
    )

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        return q


class VendorsPricingClass(Base):
    __tablename__ = "vendor_pricing_classes"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = ["name", "deleted_at"]
    __primary_ref__ = "vendors"

    id = Column(Integer, primary_key=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    name = Column(String)
    deleted_at = Column(DateTime)

    # relationships
    vendors = relationship("Vendor", back_populates=__jsonapi_type_override__)
    vendor_pricing_by_class = relationship(
        "VendorsPricingByClass", back_populates=__jsonapi_type_override__
    )

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        return q


class VendorsPricingByClass(Base):
    __tablename__ = "vendor_pricing_by_class"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = ["price", "deleted_at"]
    __primary_ref__ = "vendor_pricing_classes"

    id = Column(Integer, primary_key=True)
    pricing_class_id = Column(Integer, ForeignKey("vendor_pricing_classes.id"))
    product_id = Column(Integer, ForeignKey("vendor_products.id"))
    price = Column(Integer)
    deleted_at = Column(DateTime)

    # relationships
    vendors = relationship("Vendor", back_populates=__jsonapi_type_override__)
    vendor_pricing_classes = relationship(
        "VendorPricingClass", back_populates=__jsonapi_type_override__
    )
    vendor_product_to_class_mapping = relationship(
        "VendorsProductToClassMapping", back_populates=__jsonapi_type_override__
    )

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        return q


class VendorsPricingByClassChangelog(Base):
    __tablename__ = "vendor_pricing_by_class_changelog"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = None
    __primary_ref__ = "vendor_pricing_by_class"

    id = Column(Integer, primary_key=True)
    vendor_pricing_class_id = Column(Integer, ForeignKey("vendor_pricing_by_class.id"))
    price = Column(Integer)
    timestamp = Column(DateTime)

    # relationships
    vendor_pricing_by_class = relationship(
        "VendorsPricingByClass", back_populates=__jsonapi_type_override__
    )

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        return q


class VendorsPricingByCustomer(Base):
    __tablename__ = "vendor_pricing_by_customer"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = ["use_as_override", "price", "deleted_at"]
    __primary_ref__ = "vendor_customers"

    id = Column(Integer, primary_key=True)
    pricing_class_id = Column(Integer, ForeignKey("vendor_pricing_classes.id"))
    product_id = Column(Integer, ForeignKey("vendor_products.id"))
    vendor_customer_id = Column(Integer, ForeignKey("vendor_customers.id"))
    use_as_override = Column(Boolean)
    price = Column(Integer)
    deleted_at = Column(DateTime)

    # relationships
    vendor_customers = relationship(
        "VendorCustomer", back_populates=__jsonapi_type_override__
    )
    vendor_products = relationship(
        "VendorProduct", back_populates=__jsonapi_type_override__
    )
    vendor_pricing_classes = relationship(
        "VendorPricingClass", back_populates=__jsonapi_type_override__
    )

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        vendor_customers = aliased(VendorCustomer)
        vendor_customer_to_locations = aliased(CustomerLocationMapping)
        exists_subquery = exists().where(
            vendor_customer_to_locations.vendor_customer_id == vendor_customers.id,
            vendor_customer_to_locations.customer_location_id.in_(ids),
            vendor_customers.id == VendorsPricingByCustomer.vendor_customer_id,
        )
        return q.where(exists_subquery)

    ## primary id lookup
    def permitted_primary_resource_ids(email: str, vendor: str) -> QuerySet:
        return vendor_customer_primary_id_queries(email=email, vendor=vendor)


class VendorCustomer(Base):
    __tablename__ = "vendor_customers"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = ["name", "deleted_at"]
    __primary_ref__ = "vendors"

    id = Column(Integer, primary_key=True)
    vendor_id = Column(String, ForeignKey("vendors.id"))
    name = Column(String)
    deleted_at = Column(DateTime)

    # relationships
    vendors = relationship("Vendor", back_populates=__jsonapi_type_override__)
    vendor_pricing_by_customer = relationship(
        "VendorPricingByCustomer", back_populates=__jsonapi_type_override__
    )
    vendor_pricing_classes = relationship(
        "VendorProductClassDiscount", back_populates=__jsonapi_type_override__
    )
    vendor_customer_pricing_classes_changelog = relationship(
        "VendorCustomerPricingClassChangelog", back_populates=__jsonapi_type_override__
    )
    vendor_customer_pricing_classes = relationship(
        "VendorCustomerPricingClass", back_populates=__jsonapi_type_override__
    )
    vendor_customers_changelog = relationship(
        "VendorCustomerChangelog", back_populates=__jsonapi_type_override__
    )
    vendor_quotes = relationship(
        "VendorQuote", back_populates=__jsonapi_type_override__
    )
    vendor_customer_attrs = relationship(
        "VendorCustomerAttr", back_populates=__jsonapi_type_override__
    )
    customer_location_mapping = relationship(
        "CustomerLocationMapping", back_populates=__jsonapi_type_override__
    )

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        vendor_customer_to_locations = aliased(CustomerLocationMapping)
        exists_subquery = exists().where(
            vendor_customer_to_locations.vendor_customer_id == VendorCustomer.id,
            vendor_customer_to_locations.customer_location_id.in_(ids),
        )
        return q.where(exists_subquery)

    ## primary id lookup
    def permitted_primary_resource_ids(email: str, vendor: str) -> QuerySet:
        return vendor_customer_primary_id_queries(email=email, vendor=vendor)


class CustomerLocationMapping(Base):
    __tablename__ = "customer_location_mapping"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = ["deleted_at"]
    __primary_ref__ = None

    id = Column(Integer, primary_key=True)
    vendor_customer_id = Column(Integer, ForeignKey("vendor_customers.id"))
    customer_location_id = Column(Integer, ForeignKey("sca_customer_locations.id"))
    # relationships
    vendor_customers = relationship("VendorCustomer", back_populates=__tablename__)
    customer_locations = relationship(
        "SCACustomerLocation", back_populates=__tablename__
    )

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        return q.where(CustomerLocationMapping.customer_location_id.in_(ids))


class VendorPricingByCustomerChangelog(Base):
    __tablename__ = "Vendor_pricing_by_customer_changelog"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = None
    __primary_ref__ = "vendor_pricing_by_customer"

    id = Column(Integer, primary_key=True)
    vendor_pricing_by_customer_id = Column(
        Integer, ForeignKey("vendor_pricing_by_customer.id")
    )
    price = Column(Integer)
    timestamp = Column(DateTime)

    # relationships
    vendor_pricing_by_customer = relationship(
        "VendorsPricingByCustomer", back_populates=__tablename__
    )

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        vendor_pricing_by_customer = aliased(VendorsPricingByCustomer)
        vendor_customers = aliased(VendorCustomer)
        customer_mapping = aliased(CustomerLocationMapping)
        exists_query = exists().where(
            vendor_pricing_by_customer.id
            == VendorPricingByCustomerChangelog.vendor_pricing_by_customer_id,
            vendor_pricing_by_customer.vendor_customer_id == vendor_customers.id,
            vendor_customers.id == customer_mapping.vendor_customer_id,
            customer_mapping.customer_location_id.in_(ids),
        )
        return q.where(exists_query)

    ## primary id lookup
    def permitted_primary_resource_ids(email: str, vendor: str) -> QuerySet:
        return vendor_pricing_by_customer_primary_id_queries(email=email, vendor=vendor)


class VendorProductClassDiscounts(Base):
    __tablename__ = "vendor_product_class_discounts"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = ["discount", "deleted_at"]
    __primary_ref__ = "vendor_customers"

    id = Column(Integer, primary_key=True)
    product_class_id = Column(Integer, ForeignKey("vendor_product_classes.id"))
    vendor_customer_id = Column(Integer, ForeignKey("vendor_customers.id"))
    discount = Column(Float)
    deleted_at = Column(DateTime)

    # relationships
    vendor_customers = relationship("VendorCustomer", back_populates=__tablename__)
    vendor_product_classes = relationship(
        "VendorsProductClass", back_populates=__tablename__
    )

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        vendor_customers = aliased(VendorCustomer)
        customer_mapping = aliased(CustomerLocationMapping)
        exists_query = exists().where(
            vendor_customers.id == VendorProductClassDiscounts.vendor_customer_id,
            vendor_customers.id == customer_mapping.vendor_customer_id,
            customer_mapping.customer_location_id.in_(ids),
        )
        return q.where(exists_query)

    ## primary id lookup
    def permitted_primary_resource_ids(email: str, vendor: str) -> QuerySet:
        return vendor_customer_primary_id_queries(email=email, vendor=vendor)


class VendorPricingByCustomerAttr(Base):
    __tablename__ = "Vendor_pricing_by_customer_attrs"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = None
    __primary_ref__ = "vendor_pricing_by_customer"

    id = Column(Integer, primary_key=True)
    pricing_by_customer_id = Column(
        Integer, ForeignKey("vendor_pricing_by_customer.id")
    )
    attr = Column(String)
    type = Column(String)
    value = Column(String)
    deleted_at = Column(DateTime)

    # relationships
    vendor_pricing_by_customer = relationship(
        "VendorsPricingByCustomer", back_populates=__tablename__
    )

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        vendor_pricing_by_customer = aliased(VendorsPricingByCustomer)
        vendor_customers = aliased(VendorCustomer)
        customer_mapping = aliased(CustomerLocationMapping)
        exists_query = exists().where(
            vendor_pricing_by_customer.id
            == VendorPricingByCustomerAttr.pricing_by_customer_id,
            vendor_pricing_by_customer.vendor_customer_id == vendor_customers.id,
            vendor_customers.id == customer_mapping.vendor_customer_id,
            customer_mapping.customer_location_id.in_(ids),
        )
        return q.where(exists_query)

    ## primary id lookup
    def permitted_primary_resource_ids(email: str, vendor: str) -> QuerySet:
        return vendor_pricing_by_customer_primary_id_queries(email=email, vendor=vendor)


class VendorsProductClassDiscountsChangelog(Base):
    __tablename__ = "vendor_product_class_discounts_changelog"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = None
    __primary_ref__ = "vendor_product_class_discounts"

    id = Column(Integer, primary_key=True)
    vendor_product_class_discounts_id = Column(
        Integer, ForeignKey("vendor_product_class_discounts.id")
    )
    discount = Column(Float)
    timestamp = Column(DateTime)

    # relationships
    vendor_product_class_discounts = relationship(
        "VendorProductClassDiscounts", back_populates=__jsonapi_type_override__
    )

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        vendor_product_class_discounts = aliased(VendorProductClassDiscounts)
        vendor_customers = aliased(VendorCustomer)
        customer_mapping = aliased(CustomerLocationMapping)
        exists_query = exists().where(
            vendor_product_class_discounts.id
            == VendorsProductClassDiscountsChangelog.vendor_product_class_discounts_id,
            vendor_customers.id == vendor_product_class_discounts.vendor_customer_id,
            vendor_customers.id == customer_mapping.vendor_customer_id,
            customer_mapping.customer_location_id.in_(ids),
        )
        return q.where(exists_query)


class VendorQuote(Base):
    __tablename__ = "vendor_quotes"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = [
        "vendor_quote_number",
        "status",
        "quote_doc",
        "plans_doc",
        "deleted_at",
    ]
    __primary_ref__ = "vendor_customers"

    id = Column(Integer, primary_key=True)
    vendor_customer_id = Column(Integer, ForeignKey("vendor_customers.id"))
    place_id = Column(Integer, ForeignKey("sca_places.id"))
    vendor_quote_number = Column(String)
    job_name = Column(String)
    status: Mapped[Stage] = mapped_column()
    quote_doc = Column(String)
    plans_doc = Column(String)
    deleted_at = Column(DateTime)

    # relationships
    vendor_customers = relationship("VendorCustomer", back_populates=__tablename__)
    places = relationship("SCAPlace", back_populates=__tablename__)

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        vendor_customers = aliased(VendorCustomer)
        customer_mapping = aliased(CustomerLocationMapping)
        exists_query = exists().where(
            vendor_customers.id == VendorQuote.vendor_customer_id,
            vendor_customers.id == customer_mapping.vendor_customer_id,
            customer_mapping.customer_location_id.in_(ids),
        )
        return q.where(exists_query)

    ## primary id lookup
    def permitted_primary_resource_ids(email: str, vendor: str) -> QuerySet:
        return vendor_customer_primary_id_queries(email=email, vendor=vendor)


class VendorQuoteProduct(Base):
    __tablename__ = "vendor_quote_products"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = ["qty", "price", "deleted_at"]
    __primary_ref__ = "vendor_quotes"

    id = Column(Integer, primary_key=True)
    vendor_quotes_id = Column(Integer, ForeignKey("vendor_quotes.id"))
    product_id = Column(Integer, ForeignKey("vendor_products.id"))
    tag = Column(String)
    competitor_model = Column(String)
    qty = Column(Integer)
    price = Column(Integer)
    deleted_at = Column(DateTime)

    # relationships
    vendor_quotes = relationship("VendorQuote", back_populates=__tablename__)
    vendor_products = relationship("VendorProduct", back_populates=__tablename__)

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        vendor_quotes = aliased(VendorQuote)
        vendor_customers = aliased(VendorCustomer)
        customer_mapping = aliased(CustomerLocationMapping)
        exists_query = exists().where(
            vendor_quotes.id == VendorQuoteProduct.vendor_quotes_id,
            vendor_customers.id == vendor_quotes.vendor_customer_id,
            vendor_customers.id == customer_mapping.vendor_customer_id,
            customer_mapping.customer_location_id.in_(ids),
        )
        return q.where(exists_query)

    ## primary id lookup
    def permitted_primary_resource_ids(email: str, vendor: str) -> QuerySet:
        return vendor_quotes_primary_id_queries(email=email, vendor=vendor)


class VendorQuoteChangelog(Base):
    __tablename__ = "vendor_quotes_changelog"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = None
    __primary_ref__ = "vendor_quotes"

    id = Column(Integer, primary_key=True)
    vendor_quotes_id = Column(Integer, ForeignKey("vendor_quotes.id"))
    status: Mapped[Stage] = mapped_column()
    timestamp = Column(DateTime)

    # relationships
    vendor_quotes = relationship("VendorQuote", back_populates=__tablename__)

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        vendor_quotes = aliased(VendorQuote)
        vendor_customers = aliased(VendorCustomer)
        customer_mapping = aliased(CustomerLocationMapping)
        exists_query = exists().where(
            vendor_quotes.id == VendorQuoteChangelog.vendor_quotes_id,
            vendor_customers.id == vendor_quotes.vendor_customer_id,
            vendor_customers.id == customer_mapping.vendor_customer_id,
            customer_mapping.customer_location_id.in_(ids),
        )
        return q.where(exists_query)


class VendorQuoteProductChangelog(Base):
    __tablename__ = "vendor_quote_products_changelog"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = None
    __primary_ref__ = "vendor_quote_products"

    id = Column(Integer, primary_key=True)
    vendor_quote_products_id = Column(Integer, ForeignKey("vendor_quote_products.id"))
    qty = Column(Integer)
    price = Column(Integer)
    timestamp = Column(DateTime)

    # relationships
    vendor_quote_products = relationship(
        "VendorQuoteProduct", back_populates=__tablename__
    )

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        vendor_quote_products = aliased(VendorQuoteProduct)
        vendor_quotes = aliased(VendorQuote)
        vendor_customers = aliased(VendorCustomer)
        customer_mapping = aliased(CustomerLocationMapping)
        exists_query = exists().where(
            vendor_quote_products.id
            == VendorQuoteProductChangelog.vendor_quote_products_id,
            vendor_quotes.id == vendor_quote_products.vendor_quotes_id,
            vendor_customers.id == vendor_quotes.vendor_customer_id,
            vendor_customers.id == customer_mapping.vendor_customer_id,
            customer_mapping.customer_location_id.in_(ids),
        )
        return q.where(exists_query)


class VendorCustomerPricingClass(Base):
    __tablename__ = "vendor_customer_pricing_classes"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = None
    __primary_ref__ = "vendor_customers"

    id = Column(Integer, primary_key=True)
    pricing_class_id = Column(Integer, ForeignKey("vendor_pricing_classes.id"))
    vendor_customer_id = Column(Integer, ForeignKey("vendor_customers.id"))
    deleted_at = Column(DateTime)

    # relationships
    vendor_pricing_classes = relationship(
        "VendorsPricingClass", back_populates=__tablename__
    )
    vendor_customers = relationship("VendorCustomer", back_populates=__tablename__)

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        vendor_customers = aliased(VendorCustomer)
        customer_mapping = aliased(CustomerLocationMapping)
        exists_query = exists().where(
            vendor_customers.id == VendorCustomerPricingClass.vendor_customer_id,
            vendor_customers.id == customer_mapping.vendor_customer_id,
            customer_mapping.customer_location_id.in_(ids),
        )
        return q.where(exists_query)


class VendorCustomerPricingClassesChangelog(Base):
    __tablename__ = "vendor_customer_pricing_classes_changelog"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = None
    __primary_ref__ = "vendor_customers"

    id = Column(Integer, primary_key=True)
    pricing_class_id = Column(Integer, ForeignKey("vendor_pricing_classes.id"))
    vendor_customer_id = Column(Integer, ForeignKey("vendor_customers.id"))
    timestamp = Column(DateTime)

    # relationships
    vendor_pricing_classes = relationship(
        "VendorsPricingClass", back_populates=__tablename__
    )
    vendor_customers = relationship("VendorCustomer", back_populates=__tablename__)

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        vendor_customers = aliased(VendorCustomer)
        customer_mapping = aliased(CustomerLocationMapping)
        exists_query = exists().where(
            vendor_customers.id
            == VendorCustomerPricingClassesChangelog.vendor_customer_id,
            vendor_customers.id == customer_mapping.vendor_customer_id,
            customer_mapping.customer_location_id.in_(ids),
        )
        return q.where(exists_query)


class VendorCustomerChangelog(Base):
    __tablename__ = "vendor_customer_changelog"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = None
    __primary_ref__ = "vendor_customers"

    id = Column(Integer, primary_key=True)
    vendor_customer_id = Column(Integer, ForeignKey("vendor_customers.id"))
    name = Column(String)
    timestamp = Column(DateTime)

    # relationships
    vendor_customers = relationship("VendorCustomer", back_populates=__tablename__)

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        vendor_customers = aliased(VendorCustomer)
        customer_mapping = aliased(CustomerLocationMapping)
        exists_query = exists().where(
            vendor_customers.id == VendorCustomerChangelog.vendor_customer_id,
            vendor_customers.id == customer_mapping.vendor_customer_id,
            customer_mapping.customer_location_id.in_(ids),
        )
        return q.where(exists_query)


class VendorCustomerAttr(Base):
    __tablename__ = "vendor_customer_attrs"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = ["value", "deleted_at"]
    __primary_ref__ = "vendor_customers"

    id = Column(Integer, primary_key=True)
    vendor_customer_id = Column(Integer, ForeignKey("vendor_customers.id"))
    attr = Column(String)
    type = Column(String)
    value = Column(String)
    deleted_at = Column(DateTime)

    # relationships
    vendor_customers = relationship("VendorCustomer", back_populates=__tablename__)

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        return q


class VendorQuoteAttr(Base):
    __tablename__ = "vendor_quotes_attrs"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = ["value", "deleted_at"]
    __primary_ref__ = "vendor_quotess"

    id = Column(Integer, primary_key=True)
    vendor_quotes_id = Column(Integer, ForeignKey("vendor_quotes.id"))
    attr = Column(String)
    type = Column(String)
    value = Column(String)
    deleted_at = Column(DateTime)

    # relationships
    vendor_quotes = relationship("VendorQuote", back_populates=__tablename__)

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        return q


class CustomerPricingByClass(Base):
    __tablename__ = "customer_pricing_by_class"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = None
    __primary_ref__ = "vendor_pricing_by_class"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("sca_users.id"))
    pricing_by_class_id = Column(Integer, ForeignKey("vendor_pricing_by_class.id"))

    # relationships
    vendor_pricing_by_class = relationship(
        "VendorsPricingByClass", back_populates=__tablename__
    )
    users = relationship("SCAUser", back_populates=__tablename__)

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        return q


class CustomerPricingByCustomer(Base):
    __tablename__ = "customer_pricing_by_customer"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = None
    __primary_ref__ = "vendor_pricing_by_customer"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("sca_users.id"))
    pricing_by_customer_id = Column(
        Integer, ForeignKey("vendor_pricing_by_customer.id")
    )

    # relationships
    vendor_pricing_by_customer = relationship(
        "VendorsPricingByCustomer", back_populates=__tablename__
    )
    users = relationship("SCAUser", back_populates=__tablename__)

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        return q


class VendorCustomerAttrChangelog(Base):
    __tablename__ = "vendor_customer_attrs_changelog"
    __jsonapi_type_override__ = __tablename__.replace("_", "-")
    __modifiable_fields__ = None
    __primary_ref__ = "vendor_customer_attrs"

    id = Column(Integer, primary_key=True)
    attr_id = Column(Integer, ForeignKey("vendor_customer_attrs.id"))
    value = Column(String)
    timestamp = Column(DateTime)

    # relationships
    vendor_customer_attrs = relationship("VendorCustomerAttr", back_populates=__tablename__)

    # GET request filtering
    def apply_customer_location_filtering(q: Query, ids: set[int] = None) -> Query:
        if not ids:
            return q
        vendor_customers = aliased(VendorCustomer)
        customer_mapping = aliased(CustomerLocationMapping)
        exists_query = exists().where(
            vendor_customers.id == VendorCustomerAttrChangelog.vendor_customer_id,
            vendor_customers.id == customer_mapping.vendor_customer_id,
            customer_mapping.customer_location_id.in_(ids),
        )
        return q.where(exists_query)


serializer = JSONAPI_(Base)
serializer_partial = partial(JSONAPI_, Base)


def adp_customer_primary_id_queries(email: str) -> QuerySet:
    adp_customers_alias = aliased(ADPCustomer)
    adptoloc = aliased(ADPAliasToSCACustomerLocation)
    users = aliased(SCAUser)
    customer_locations = aliased(SCACustomerLocation)

    user_query = select(adp_customers_alias.id).where(
        exists().where(
            customer_locations.id == users.customer_location_id,
            customer_locations.id == adptoloc.sca_customer_location_id,
            users.email == email,
            adptoloc.adp_customer_id == ADPCustomer.id,
        )
    )

    manager_map = aliased(SCAManagerMap)
    manager_query = select(adp_customers_alias.id).where(
        exists().where(
            customer_locations.id == users.customer_location_id,
            customer_locations.id == adptoloc.sca_customer_location_id,
            manager_map.user_id == users.id,
            users.email == email,
            adptoloc.adp_customer_id == ADPCustomer.id,
        )
    )
    customers_2 = aliased(ADPCustomer)
    admin_query = select(adp_customers_alias.id).where(
        exists().where(
            customer_locations.id == users.customer_location_id,
            customer_locations.id == adptoloc.sca_customer_location_id,
            customers_2.id == adptoloc.adp_customer_id,
            customers_2.sca_id == ADPCustomer.sca_id,
            users.email == email,
            adptoloc.adp_customer_id == ADPCustomer.id,
        )
    )
    querys: QuerySet = {
        "sql_user_only": str(user_query),
        "sql_manager": str(manager_query),
        "sql_admin": str(admin_query),
    }
    return querys


def adp_quote_primary_id_queries(email: str) -> QuerySet:
    adp_quotes_alias = aliased(ADPQuote)
    adptoloc = aliased(ADPAliasToSCACustomerLocation)
    users = aliased(SCAUser)
    customer_locations = aliased(SCACustomerLocation)

    user_query = select(adp_quotes_alias.id).where(
        exists().where(
            customer_locations.id == users.customer_location_id,
            customer_locations.id == adptoloc.sca_customer_location_id,
            users.email == email,
            adptoloc.adp_customer_id == ADPQuote.adp_customer_id,
        )
    )

    manager_map = aliased(SCAManagerMap)
    manager_query = select(adp_quotes_alias.id).where(
        exists().where(
            customer_locations.id == users.customer_location_id,
            customer_locations.id == adptoloc.sca_customer_location_id,
            manager_map.user_id == users.id,
            users.email == email,
            adptoloc.adp_customer_id == ADPQuote.adp_customer_id,
        )
    )
    customers_2 = aliased(ADPQuote)
    admin_query = select(adp_quotes_alias.id).where(
        exists().where(
            customer_locations.id == users.customer_location_id,
            customer_locations.id == adptoloc.sca_customer_location_id,
            customers_2.id == adptoloc.adp_customer_id,
            customers_2.adp_customer_id == ADPQuote.adp_customer_id,
            users.email == email,
            adptoloc.adp_customer_id == ADPQuote.adp_customer_id,
        )
    )
    querys: QuerySet = {
        "sql_user_only": str(user_query),
        "sql_manager": str(manager_query),
        "sql_admin": str(admin_query),
    }
    return querys


def customers_primary_id_queries(email: str) -> QuerySet:
    users = aliased(SCAUser)
    customers = aliased(SCACustomer)
    customer_locations = aliased(SCACustomerLocation)

    user_query = select(customers.id).where(
        exists().where(
            customer_locations.id == users.customer_location_id,
            customers.id == customer_locations.id,
            users.email == email,
        )
    )

    manager_map = aliased(SCAManagerMap)
    manager_query = select(customers.id).where(
        exists().where(
            customer_locations.id == manager_map.customer_location_id,
            manager_map.user_id == users.id,
            customers.id == customer_locations.id,
            users.email == email,
        )
    )
    customers_2 = aliased(SCACustomer)
    admin_query = select(customers.id).where(
        exists().where(
            customer_locations.id == users.customer_location_id,
            customers_2.id == customer_locations.customer_id,
            users.email == email,
            customers_2.id == customers.id,
        )
    )
    querys: QuerySet = {
        "sql_user_only": str(user_query),
        "sql_manager": str(manager_query),
        "sql_admin": str(admin_query),
    }
    return querys


def friedrich_customer_primary_id_queries(email: str) -> QuerySet:
    friedrich_customers_alias = aliased(FriedrichCustomer)
    friedrichtoloc = aliased(FriedrichCustomertoSCACustomerLocation)
    users = aliased(SCAUser)
    customer_locations = aliased(SCACustomerLocation)

    user_query = select(friedrich_customers_alias.id).where(
        exists().where(
            customer_locations.id == users.customer_location_id,
            customer_locations.id == friedrichtoloc.sca_customer_location_id,
            users.email == email,
            friedrichtoloc.friedrich_customer_id == FriedrichCustomer.id,
        )
    )

    manager_map = aliased(SCAManagerMap)
    manager_query = select(friedrich_customers_alias.id).where(
        exists().where(
            customer_locations.id == users.customer_location_id,
            customer_locations.id == friedrichtoloc.sca_customer_location_id,
            manager_map.user_id == users.id,
            users.email == email,
            friedrichtoloc.friedrich_customer_id == FriedrichCustomer.id,
        )
    )
    customers_2 = aliased(FriedrichCustomer)
    admin_query = select(friedrich_customers_alias.id).where(
        exists().where(
            customer_locations.id == users.customer_location_id,
            customer_locations.id == friedrichtoloc.sca_customer_location_id,
            customers_2.id == friedrichtoloc.friedrich_customer_id,
            customers_2.sca_id == FriedrichCustomer.sca_id,
            users.email == email,
            friedrichtoloc.friedrich_customer_id == FriedrichCustomer.id,
        )
    )
    querys: QuerySet = {
        "sql_user_only": str(user_query),
        "sql_manager": str(manager_query),
        "sql_admin": str(admin_query),
    }
    return querys


def friedrich_quote_primary_id_queries(email: str) -> QuerySet:
    friedrich_quotes_alias = aliased(FriedrichQuote)
    friedrichtoloc = aliased(FriedrichCustomertoSCACustomerLocation)
    users = aliased(SCAUser)
    customer_locations = aliased(SCACustomerLocation)

    user_query = select(friedrich_quotes_alias.id).where(
        exists().where(
            customer_locations.id == users.customer_location_id,
            customer_locations.id == friedrichtoloc.sca_customer_location_id,
            users.email == email,
            friedrichtoloc.friedrich_customer_id == FriedrichCustomer.id,
        )
    )

    manager_map = aliased(SCAManagerMap)
    manager_query = select(friedrich_quotes_alias.id).where(
        exists().where(
            customer_locations.id == users.customer_location_id,
            customer_locations.id == friedrichtoloc.sca_customer_location_id,
            manager_map.user_id == users.id,
            users.email == email,
            friedrichtoloc.friedrich_customer_id == FriedrichCustomer.id,
        )
    )
    customers_2 = aliased(FriedrichCustomer)
    admin_query = select(friedrich_quotes_alias.id).where(
        exists().where(
            customer_locations.id == users.customer_location_id,
            customer_locations.id == friedrichtoloc.sca_customer_location_id,
            customers_2.id == friedrichtoloc.friedrich_customer_id,
            customers_2.sca_id == FriedrichCustomer.sca_id,
            users.email == email,
            friedrichtoloc.friedrich_customer_id == FriedrichCustomer.id,
        )
    )
    querys: QuerySet = {
        "sql_user_only": str(user_query),
        "sql_manager": str(manager_query),
        "sql_admin": str(admin_query),
    }
    return querys


def vendor_customer_primary_id_queries(email: str, vendor: str) -> QuerySet:
    vendor_customer = aliased(VendorCustomer)
    customer_to_loc = aliased(CustomerLocationMapping)
    customer_locations = aliased(SCACustomerLocation)
    users = aliased(SCAUser)

    user_query = select(vendor_customer.id).where(
        exists().where(
            customer_locations.id == users.customer_location_id,
            customer_locations.id == customer_to_loc.customer_location_id,
            users.email == email,
            customer_to_loc.vendor_customer_id == VendorCustomer.id,
        ),
        vendor_customer.vendor_id == vendor,
    )

    manager_map = aliased(SCAManagerMap)
    manager_query = select(vendor_customer.id).where(
        exists().where(
            customer_locations.id == users.customer_location_id,
            customer_locations.id == customer_to_loc.customer_location_id,
            manager_map.user_id == users.id,
            users.email == email,
            customer_to_loc.vendor_customer_id == VendorCustomer.id,
        ),
        vendor_customer.vendor_id == vendor,
    )
    admin_map = aliased(CustomerAdminMap)
    admin_query = select(vendor_customer.id).where(
        exists().where(
            customer_locations.id == customer_to_loc.customer_location_id,
            customer_locations.customer_id == admin_map.customer_id,
            admin_map.user_id == users.id,
            users.email == email,
            customer_to_loc.vendor_customer_id == VendorCustomer.id,
        ),
        vendor_customer.vendor_id == vendor,
    )
    querys: QuerySet = {
        "sql_user_only": str(user_query),
        "sql_manager": str(manager_query),
        "sql_admin": str(admin_query),
    }
    return querys


def vendor_quotes_primary_id_queries(email: str, vendor: str) -> QuerySet:
    vendor_quotes = aliased(VendorQuote)
    vendor_customer = aliased(VendorCustomer)
    customer_to_loc = aliased(CustomerLocationMapping)
    customer_locations = aliased(SCACustomerLocation)
    users = aliased(SCAUser)

    user_query = select(vendor_quotes.id).where(
        exists().where(
            customer_locations.id == users.customer_location_id,
            customer_locations.id == customer_to_loc.customer_location_id,
            users.email == email,
            customer_to_loc.vendor_customer_id == vendor_customer.id,
            vendor_customer.id == VendorQuote.vendor_customer_id,
        ),
        vendor_customer.vendor_id == vendor,
    )

    manager_map = aliased(SCAManagerMap)
    manager_query = select(vendor_quotes.id).where(
        exists().where(
            customer_locations.id == users.customer_location_id,
            customer_locations.id == customer_to_loc.customer_location_id,
            manager_map.user_id == users.id,
            users.email == email,
            customer_to_loc.vendor_customer_id == vendor_customer.id,
            vendor_customer.id == VendorQuote.vendor_customer_id,
        ),
        vendor_customer.vendor_id == vendor,
    )
    admin_map = aliased(CustomerAdminMap)
    admin_query = select(vendor_quotes.id).where(
        exists().where(
            customer_locations.id == customer_to_loc.customer_location_id,
            customer_locations.customer_id == admin_map.customer_id,
            admin_map.user_id == users.id,
            users.email == email,
            customer_to_loc.vendor_customer_id == vendor_customer.id,
            vendor_customer.id == VendorQuote.vendor_customer_id,
        ),
        vendor_customer.vendor_id == vendor,
    )
    querys: QuerySet = {
        "sql_user_only": str(user_query),
        "sql_manager": str(manager_query),
        "sql_admin": str(admin_query),
    }
    return querys


def vendor_pricing_by_customer_primary_id_queries(email: str, vendor: str) -> QuerySet:
    vendor_pricing_by_customer = aliased(VendorsPricingByCustomer)
    vendor_customer = aliased(VendorCustomer)
    customer_to_loc = aliased(CustomerLocationMapping)
    customer_locations = aliased(SCACustomerLocation)
    users = aliased(SCAUser)

    user_query = select(vendor_pricing_by_customer.id).where(
        exists().where(
            customer_locations.id == users.customer_location_id,
            customer_locations.id == customer_to_loc.customer_location_id,
            users.email == email,
            vendor_customer.vendor_id == vendor,
            customer_to_loc.vendor_customer_id == vendor_customer.id,
            vendor_customer.id == VendorsPricingByCustomer.vendor_customer_id,
        )
    )
    manager_map = aliased(SCAManagerMap)
    manager_query = select(vendor_pricing_by_customer.id).where(
        exists().where(
            customer_locations.id == users.customer_location_id,
            customer_locations.id == customer_to_loc.customer_location_id,
            manager_map.user_id == users.id,
            users.email == email,
            vendor_customer.vendor_id == vendor,
            customer_to_loc.vendor_customer_id == vendor_customer.id,
            vendor_customer.id == VendorsPricingByCustomer.vendor_customer_id,
        )
    )
    admin_map = aliased(CustomerAdminMap)
    admin_query = select(vendor_pricing_by_customer.id).where(
        exists().where(
            customer_locations.id == customer_to_loc.customer_location_id,
            customer_locations.customer_id == admin_map.customer_id,
            admin_map.user_id == users.id,
            users.email == email,
            vendor_customer.vendor_id == vendor,
            customer_to_loc.vendor_customer_id == vendor_customer.id,
            vendor_customer.id == VendorsPricingByCustomer.vendor_customer_id,
        )
    )
    querys: QuerySet = {
        "sql_user_only": str(user_query),
        "sql_manager": str(manager_query),
        "sql_admin": str(admin_query),
    }
    return querys
