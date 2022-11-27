import pytest
from API.api import app


def test_register():
    app.test_client().post("/register")