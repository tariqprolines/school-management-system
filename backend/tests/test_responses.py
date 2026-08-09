from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from app.utils.responses import serialize_for_json


def test_serialize_uuid():
    uid = uuid4()
    result = serialize_for_json({"id": uid})
    assert result["id"] == str(uid)


def test_serialize_date():
    result = serialize_for_json({"joining_date": date(2025, 1, 15)})
    assert result["joining_date"] == "2025-01-15"


def test_serialize_decimal():
    result = serialize_for_json({"amount": Decimal("1500.50")})
    assert result["amount"] == 1500.5


def test_serialize_nested_list():
    uid = uuid4()
    result = serialize_for_json({"data": [{"id": uid, "name": "Test"}]})
    assert result["data"][0]["id"] == str(uid)
