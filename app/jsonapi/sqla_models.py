"""Database Table Models / Data Transfer Objects"""

from sqlalchemy import Column, Float, Integer, String, Boolean, DateTime, TEXT, ForeignKey, Enum, UniqueConstraint, Numeric, ARRAY, BigInteger, exists
from sqlalchemy.orm import declarative_base, relationship, Query, aliased
from sqlalchemy.dialects.postgresql import UUID
from app.jsonapi.sqla_jsonapi_ext import JSONAPI_

Base = declarative_base()
STAGE_ENUM = Enum('PROPOSED', 'ACTIVE', 'REJECTED', 'REMOVED', name='stage')
class ADPAHProgram(Base):
    __tablename__ = 'adp_ah_programs'
    __jsonapi_type_override__ = 'adp-ah-programs'
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
    stage = Column(STAGE_ENUM)
    customer_id = Column(Integer, ForeignKey('adp_customers.id'))
    ## relationships
    adp_customer = relationship("ADPCustomer", back_populates="adp_ah_program")
    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int]=None) -> Query:
        adptoloc = aliased(ADPAliasToSCACustomerLocation)
        exists_subquery = exists().where(
            adptoloc.adp_customer_id == ADPAHProgram.customer_id,
            adptoloc.sca_customer_location_id.in_(ids)
        )
        return q.where(exists_subquery)

class ADPCoilProgram(Base):
    __tablename__ = 'adp_coil_programs'
    __jsonapi_type_override__ = 'adp-coil-programs'
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
    stage = Column(STAGE_ENUM)
    customer_id = Column(Integer, ForeignKey('adp_customers.id'))
    ## relationships
    adp_customers = relationship("ADPCustomer", back_populates="adp_coil_program")
    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int]=None) -> Query:
        adptoloc = aliased(ADPAliasToSCACustomerLocation)
        exists_subquery = exists().where(
            adptoloc.adp_customer_id == ADPCoilProgram.customer_id,
            adptoloc.sca_customer_location_id.in_(ids)
        )
        return q.where(exists_subquery)


class ADPAliasToSCACustomerLocation(Base):
    __tablename__ = 'adp_alias_to_sca_customer_locations'
    ## fields
    id = Column(Integer, primary_key=True)
    adp_customer_id = Column(Integer, ForeignKey('adp_customers.id'))
    sca_customer_location_id = Column(Integer, ForeignKey('sca_customer_locations.id'))
    ## relationships
    adp_customer = relationship('ADPCustomer', back_populates='locations_by_alias')
    customer_locations = relationship('SCACustomerLocation', back_populates='adp_aliases')
    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int]=None) -> Query:
        if not ids:
            ids = list()
        return q

class ADPCustomer(Base):
    __tablename__ = 'adp_customers'
    __jsonapi_type_override__ = 'adp-customers'
    ## fields
    adp_alias = Column(TEXT, unique=True)
    customer = Column(TEXT)
    sca_id = Column(Integer, ForeignKey('sca_customers.id'))
    id = Column(Integer, primary_key=True)
    preferred_parts = Column(Boolean)
    ## relationships
    customer = relationship('SCACustomer', back_populates='adp_customers')
    adp_coil_program = relationship('ADPCoilProgram',back_populates='adp_customers')
    adp_ah_program = relationship('ADPAHProgram',back_populates='adp_customer')
    adp_ratings = relationship('ADPProgramRating', back_populates='adp_customer')
    locations_by_alias = relationship('ADPAliasToSCACustomerLocation', back_populates='adp_customer')
    material_group_discounts = relationship('ADPMaterialGroupDiscount', back_populates='adp_customer')
    snps = relationship('ADPSNP', back_populates='adp_customer')
    program_parts = relationship('ADPProgramPart', back_populates='adp_customer')
    adp_quotes = relationship('ADPQuote', back_populates='adp_customer')
    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int]=None) -> Query:
        if not ids:
            ids = list()
        return q

class ADPCustomerTerms(Base):
    __tablename__ = 'adp_customer_terms'
    __jsonapi_type_override__ = 'adp-customer-terms'
    ## fields
    sca_id = Column(Integer, ForeignKey('sca_customers.id'))
    terms = Column(TEXT)
    ppf = Column(Integer)
    effective_date = Column(DateTime)
    id = Column(Integer, primary_key=True)
    ## relationships
    customer = relationship('SCACustomer', back_populates='adp_customer_terms')
    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int]=None) -> Query:
        if not ids:
            ids = list()
        return q

class SCACustomer(Base):
    __tablename__ = 'sca_customers'
    __jsonapi_type_override__ = 'customers'
    ## fields
    id = Column(Integer, primary_key=True)
    name = Column(String)
    logo = Column(String)
    domains = Column(ARRAY(String))
    buying_group = Column(String)
    ## relationships
    adp_customer_terms = relationship('ADPCustomerTerms', back_populates='customer')
    adp_customers = relationship('ADPCustomer', back_populates='customer')
    customer_locations = relationship('SCACustomerLocation', back_populates='customer')
    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int]=None) -> Query:
        if not ids:
            ids = list()
        return q

class ADPMaterialGroupDiscount(Base):
    __tablename__ = 'adp_material_group_discounts'
    ## fields
    mat_grp = Column(TEXT)
    discount = Column(Float)
    id = Column(Integer, primary_key=True)
    stage = Column(STAGE_ENUM)
    effective_date = Column(DateTime)
    customer_id = Column(Integer, ForeignKey('adp_customers.id'))
    ## relationships
    adp_customer = relationship('ADPCustomer', back_populates='material_group_discounts')
    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int]=None) -> Query:
        if not ids:
            ids = list()
        return q

class ADPProgramRating(Base):
    __tablename__ = 'adp_program_ratings'
    ## fields
    ahrinumber = Column("AHRINumber",TEXT)
    outdoor_model = Column("OutdoorModel",TEXT)
    oem_name = Column("OEMName",TEXT)
    indoor_model = Column("IndoorModel",TEXT)
    furnace_model = Column("FurnaceModel",TEXT)
    oem_name_1= Column("OEM Name",TEXT)
    m1 = Column("M1",TEXT)
    status = Column("Status",TEXT)
    oem_series = Column("OEM Series",TEXT)
    adp_series = Column("ADP Series",TEXT)
    model_number = Column("Model Number",TEXT)
    coil_model_number = Column("Coil Model Number",TEXT)
    furnace_model_number = Column("Furnace Model Number",TEXT)
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
    customer_id = Column(Integer, ForeignKey('adp_customers.id'))
    seer2_as_submitted = Column(Float)
    eer95f2_as_submitted = Column(Float)
    capacity2_as_submitted = Column(Float)
    hspf2_as_submitted = Column(Float)
    id = Column(Integer, primary_key=True)
    ## relationships
    adp_customer = relationship('ADPCustomer', back_populates='adp_ratings')
    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int]=None) -> Query:
        if not ids:
            ids = list()
        return q

class ADPPricingPart(Base):
    __tablename__ = 'adp_pricing_parts'
    ## fields
    part_number = Column(String, nullable=False, primary_key=True)
    description = Column(TEXT)
    pkg_qty = Column(Integer)
    preferred = Column(Integer)
    standard = Column(Integer)
    ## relationships
    program_parts = relationship('ADPProgramPart', back_populates='part_price')
    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int]=None) -> Query:
        if not ids:
            ids = list()
        return q

class ADPProgramPart(Base):
    __tablename__ = 'adp_program_parts'
    ## fields
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('adp_customers.id'))
    part_number = Column(String, ForeignKey('adp_pricing_parts.part_number'))
    ## relationships
    part_price = relationship('ADPPricingPart', back_populates='program_parts')
    adp_customer = relationship('ADPCustomer', back_populates='program_parts')
    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int]=None) -> Query:
        if not ids:
            ids = list()
        return q

class ADPQuote(Base):
    __tablename__ = 'adp_quotes'
    ## fields
    id = Column(Integer, primary_key=True)
    adp_quote_id = Column(String, unique=True)
    place_id = Column(Integer, ForeignKey('sca_places.id'))
    adp_customer_id = Column(Integer, ForeignKey('adp_customers.id'))
    job_name = Column(String)
    created_at = Column(DateTime)
    expires_at = Column(DateTime)
    status = Column(STAGE_ENUM)
    quote_doc = Column(TEXT, unique=True)
    plans_doc = Column(TEXT)
    customer_location_id = Column(Integer, ForeignKey('sca_customer_locations.id'))
    ## relationships
    place = relationship('SCAPlace', back_populates='adp_quotes')
    adp_customer = relationship('ADPCustomer', back_populates='adp_quotes')
    customer_location = relationship('SCACustomerLocation', back_populates='adp_quotes')
    quote_products = relationship('ADPQuoteProduct', back_populates='adp_quote')
    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int]=None) -> Query:
        if not ids:
            ids = list()
        return q

class SCACustomerLocation(Base):
    __tablename__ = 'sca_customer_locations'
    __jsonapi_type_override__ = 'customer-locations'
    ## fields
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('sca_customers.id'))
    place_id = Column(Integer, ForeignKey('sca_places.id'))
    hq = Column(Boolean)
    dc = Column(Boolean)
    serviced_by_id = Column(Integer, ForeignKey('sca_customer_locations.id'))
    ## relationships
    serviced_by = relationship('SCACustomerLocation')
    adp_aliases = relationship('ADPAliasToSCACustomerLocation', back_populates='customer_locations')
    adp_quotes = relationship('ADPQuote', back_populates='customer_location')
    customer = relationship('SCACustomer', back_populates='customer_locations')
    place = relationship('SCAPlace', back_populates='customer_locations')
    manager = relationship('SCAManagerMap', back_populates='customer_location')
    users = relationship('SCAUser', back_populates='customer_location')
    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int]=None) -> Query:
        if not ids:
            ids = list()
        return q

class ADPSNP(Base):
    __tablename__ = 'adp_snps'
    ## fields
    id = Column(Integer, primary_key=True)
    model = Column(TEXT)
    price = Column(Float)
    stage = Column(STAGE_ENUM)
    effective_date = Column(DateTime)
    customer_id = Column(Integer, ForeignKey('adp_customers.id'))
    ## relationships
    adp_customer = relationship('ADPCustomer', back_populates='snps')
    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int]=None) -> Query:
        if not ids:
            ids = list()
        return q

class ADPQuoteProduct(Base):
    __tablename__ = 'adp_quote_products'
    ## fields
    id = Column(Integer, primary_key=True)
    tag = Column(String, nullable=False)
    qty = Column(Integer, nullable=False)
    price = Column(Float)
    adp_quote_id = Column(Integer, ForeignKey('adp_quotes.id'))
    model_number = Column(String)
    ## relationships
    adp_quote = relationship('ADPQuote', back_populates='quote_products')
    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int]=None) -> Query:
        if not ids:
            ids = list()
        return q

class SCAPlace(Base):
    __tablename__ = 'sca_places'
    ## fields
    id = Column(Integer, primary_key=True)
    name = Column(String)
    state = Column(String(2))
    lat = Column(Float)
    long = Column(Float)
    ## relationships
    adp_quotes = relationship('ADPQuote', back_populates='place')
    customer_locations = relationship('SCACustomerLocation', back_populates='place')
    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int]=None) -> Query:
        if not ids:
            ids = list()
        return q

class SCAManagerMap(Base):
    __tablename__ = 'sca_manager_map'
    ## fields
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('sca_users.id'))
    customer_location_id = Column(Integer, ForeignKey('sca_customer_locations.id'))
    ## Relationships
    customer_location = relationship('SCACustomerLocation', back_populates='manager')
    user = relationship('SCAUser', back_populates='managers')
    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int]=None) -> Query:
        if not ids:
            ids = list()
        return q

class SCAUser(Base):
    __tablename__ = 'sca_users'
    ## fields
    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)
    customer_location_id = Column(Integer, ForeignKey('sca_customer_locations.id'))
    ## relationships
    customer_location = relationship('SCACustomerLocation', back_populates='users')
    managers = relationship('SCAManagerMap', back_populates='user')
    ## filtering
    def apply_customer_location_filtering(q: Query, ids: list[int]=None) -> Query:
        if not ids:
            ids = list()
        return q

serializer = JSONAPI_(Base)