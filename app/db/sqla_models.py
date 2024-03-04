"""Database Table Models / Data Transfer Objects"""

import uuid
from datetime import datetime
from sqlalchemy import Column, Float, Integer, String, Boolean, DateTime, TEXT, ForeignKey, Enum, UniqueConstraint, Numeric, ARRAY, BigInteger
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.sqla_jsonapi_ext import JSONAPI_

Base = declarative_base()
STAGE_ENUM = Enum('PROPOSED', 'ACTIVE', 'REJECTED', 'REMOVED', name='stage')
class ADPAHProgram(Base):
    __tablename__ = 'adp_ah_programs'
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
    adp_customer = relationship("ADPCustomer", back_populates="customer_air_handlers")

class ADPCoilProgram(Base):
    __tablename__ = 'adp_coil_programs'
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
    adp_customer = relationship("ADPCustomer", back_populates="customer_coils")

class ADPAliasToSCACustomerLocation(Base):
    __tablename__ = 'adp_alias_to_sca_customer_locations'
    ## fields
    id = Column(Integer, primary_key=True)
    adp_customer_id = Column(Integer, ForeignKey('adp_customers.id'), unique=True)
    sca_customer_location_id = Column(Integer, ForeignKey('sca_customer_locations.id'))
    ## relationships
    adp_customer = relationship('ADPCustomer', back_populates='customer_locations_by_alias')
    customer_locations = relationship('SCACustomerLocation', back_populates='adp_aliases')

class ADPCustomer(Base):
    __tablename__ = 'adp_customers'
    ## fields
    adp_alias = Column(TEXT, unique=True)
    customer = Column(TEXT)
    sca_id = Column(Integer, ForeignKey('sca_customers.id'))
    id = Column(Integer, primary_key=True)
    preferred_parts = Column(Boolean)
    ## relationships
    parent_customer = relationship('SCACustomer', back_populates='adp_customers')
    customer_coils = relationship('ADPCoilProgram',back_populates='adp_customer')
    customer_air_handlers = relationship('ADPAHProgram',back_populates='adp_customer')
    customer_ratings = relationship('ADPProgramRating', back_populates='adp_customer')
    customer_locations_by_alias = relationship('ADPAliasToSCACustomerLocation', back_populates='adp_customer')
    customer_material_group_discounts = relationship('ADPMaterialGroupDiscount', back_populates='adp_customer')
    customer_snps = relationship('ADPSNP', back_populates='adp_customer')
    customer_parts = relationship('ADPProgramPart', back_populates='adp_customer')
    customer_quotes = relationship('ADPQuote', back_populates='adp_customer')

class ADPCustomerTerms(Base):
    __tablename__ = 'adp_customer_terms'
    ## fields
    sca_id = Column(Integer, ForeignKey('sca_customers.id'))
    terms = Column(TEXT)
    ppf = Column(Integer)
    effective_date = Column(DateTime)
    id = Column(Integer, primary_key=True)
    ## relationships
    sca_customer = relationship('SCACustomer', back_populates='adp_customer_terms')

class SCACustomer(Base):
    __tablename__ = 'sca_customers'
    ## fields
    id = Column(Integer, primary_key=True)
    name = Column(String)
    logo = Column(String)
    domains = Column(ARRAY(String))
    buying_group = Column(String)
    ## relationships
    adp_customer_terms = relationship('ADPCustomerTerms', back_populates='sca_customer')
    adp_customers = relationship('ADPCustomer', back_populates='parent_customer')
    customer_locations = relationship('SCACustomerLocation', back_populates='sca_customer')

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
    adp_customer = relationship('ADPCustomer', back_populates='customer_material_group_discounts')

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
    adp_customer = relationship('ADPCustomer', back_populates='customer_ratings')

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

class ADPProgramPart(Base):
    __tablename__ = 'adp_program_parts'
    ## fields
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('adp_customers.id'))
    part_number = Column(String, ForeignKey('adp_pricing_parts.part_number'))
    ## relationships
    part_price = relationship('ADPPricingPart', back_populates='program_parts')
    adp_customer = relationship('ADPCustomer', back_populates='customer_parts')

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
    sca_place = relationship('SCAPlace', back_populates='adp_quotes')
    adp_customer = relationship('ADPCustomer', back_populates='customer_quotes')
    sca_customer_location = relationship('SCACustomerLocation', back_populates='adp_quotes')
    quote_products = relationship('ADPQuoteProduct', back_populates='adp_quote')

class SCACustomerLocation(Base):
    __tablename__ = 'sca_customer_locations'
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
    adp_quotes = relationship('ADPQuote', back_populates='sca_customer_location')
    sca_customer = relationship('SCACustomer', back_populates='customer_locations')
    sca_place = relationship('SCAPlace', back_populates='sca_customer_locations')
    manager = relationship('SCAManagerMap', back_populates='sca_customer_location')
    users = relationship('SCAUser', back_populates='sca_customer_location')

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
    adp_customer = relationship('ADPCustomer', back_populates='customer_snps')

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


class SCAPlace(Base):
    __tablename__ = 'sca_places'
    ## fields
    id = Column(Integer, primary_key=True)
    name = Column(String)
    state = Column(String(2))
    lat = Column(Float)
    long = Column(Float)
    ## relationships
    adp_quotes = relationship('ADPQuote', back_populates='sca_place')
    sca_customer_locations = relationship('SCACustomerLocation', back_populates='sca_place')

class SCAManagerMap(Base):
    __tablename__ = 'sca_manager_map'
    ## fields
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('sca_users.id'))
    customer_location_id = Column(Integer, ForeignKey('sca_customer_locations.id'))
    ## Relationships
    sca_customer_location = relationship('SCACustomerLocation', back_populates='manager')
    sca_user = relationship('SCAUser', back_populates='managers')

class SCAUser(Base):
    __tablename__ = 'sca_users'
    ## fields
    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)
    customer_location_id = Column(Integer, ForeignKey('sca_customer_locations.id'))
    ## relationships
    sca_customer_location = relationship('SCACustomerLocation', back_populates='users')
    managers = relationship('SCAManagerMap', back_populates='sca_user')

serializer = JSONAPI_(Base)