import pytest

import symnoesis


@pytest.mark.unit
def test_package_metadata() -> None:
    assert symnoesis.__version__ == "0.1.0.dev0"
