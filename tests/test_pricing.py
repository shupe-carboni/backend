"""test endpoints for returning formatted pricing and executing price updates"""

from fastapi.testclient import TestClient
from pytest import mark, fixture
from random import random
from pprint import pformat
from httpx import Response
from pathlib import Path
from typing import Union, Optional
from dataclasses import dataclass, asdict, replace
from enum import StrEnum
from itertools import chain
from datetime import datetime, timedelta

from app.main import app
from app.auth import authenticate_auth0_token
from tests import auth_overrides
from app.jsonapi.sqla_models import *

test_client = TestClient(app)

ParameterizedStatusCodes = list[tuple[auth_overrides.Token, int]]

FUTURE_DATE = datetime.today() + timedelta(days=60)
