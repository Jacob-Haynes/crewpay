from pathlib import Path

import pytest

import crewpay.wsgi


@pytest.fixture
def data_path() -> Path:
    return Path(__file__).parent / "data"
