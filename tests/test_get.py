import pytest
from type_conversion_dict import TypeConversionDict


def test_basic() -> None:
    d = TypeConversionDict(foo="42", bar="blub")
    value = d["foo"]
    assert value == "42"

    value = d.get("foo")
    assert value == "42"

    value = d.get("foo", type=int)
    assert value == 42

    value = d.get("bar", -1, type=int)
    assert value == -1


def test_missing() -> None:
    d = TypeConversionDict(foo="42")
    value = d.get("bar", -1, type=int)
    assert value == -1


@pytest.mark.skip(reason="Not implemented")
def test_missing_2() -> None:
    d = TypeConversionDict(foo="42")
    value = d.get("bar", -1, type=int)
    assert value == -1

    with pytest.raises(KeyError):
        value = d.get("bar", type=int)
