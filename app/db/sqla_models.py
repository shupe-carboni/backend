"""Database Table Models / Data Transfer Objects"""

import uuid
from datetime import datetime
from sqlalchemy import Column, Float, Integer, String, Boolean, DateTime, TEXT, ForeignKey, Enum, UniqueConstraint, Numeric, ARRAY
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqla_jsonapi_ext import JSONAPI_

Base = declarative_base()

### SQLAlchemy models here ###
#                            #
##############################

# Fix bug in the JSON:API serializer and initialize it
# BUG JSONAPI's constructor is broken for SQLAchelmy 1.4.x
setattr(Base,"_decl_class_registry",Base.registry._class_registry) 
serializer = JSONAPI_(Base)