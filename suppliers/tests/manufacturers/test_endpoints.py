from typing import Dict

import pytest
from faker import Faker
from fastapi.testclient import TestClient

fake = Faker()
fake.seed_instance(0)
   
