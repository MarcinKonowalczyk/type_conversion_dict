import pytest
from type_conversion_dict import TypeConversionDict


def test_normal_get() -> None:
    d = TypeConversionDict(foo="42")
    value = d.get("foo")
    assert value == "42"

    value = d.get("bar")
    assert value is None


def test_normal_get_required() -> None:
    d = TypeConversionDict(foo="42")
    value = d.get("foo", required=False)
    assert value == "42"

    value = d.get("bar", required=False)
    assert value is None

    with pytest.raises(KeyError):
        _value = d.get("bar", required=True)


def test_normal_get_default() -> None:
    d = TypeConversionDict(foo="42")
    value = d.get("foo", "default")
    assert value == "42"

    value = d.get("bar", "default")
    assert value == "default"


def test_normal_get_default_required() -> None:
    d = TypeConversionDict(foo="42")
    value = d.get("foo", "default", required=False)
    assert value == "42"

    value = d.get("bar", "default", required=False)
    assert value == "default"

    with pytest.raises(KeyError):
        _value = d.get("bar", "default", required=True)


def test_get_with_type() -> None:
    d = TypeConversionDict(foo="42")
    value = d.get("foo", type=int)
    assert value == 42

    value = d.get("bar", type=int)
    assert value is None

    def _my_type(value: str) -> int:
        return int(value) + 1

    value = d.get("foo", type=_my_type)
    assert value == 43


def test_get_with_type_required() -> None:
    d = TypeConversionDict(foo="42")
    value = d.get("foo", type=int, required=False)
    assert value == 42

    value = d.get("bar", type=int, required=False)
    assert value is None

    with pytest.raises(KeyError):
        _value = d.get("bar", type=int, required=True)

    def _my_type(value: str) -> int:
        if value != "hello":
            raise ValueError("value must be 'hello'")
        return 42

    value = d.get("foo", type=_my_type, required=False)
    assert value == None # since the value is not 'hello'

    with pytest.raises(ValueError):
        _value = d.get("foo", type=_my_type, required=True)


def test_get_with_type_default() -> None:
    d = TypeConversionDict(foo="42")
    value = d.get("foo", "default", type=int)
    assert value == 42

    value = d.get("bar", "default", type=int)
    assert value == "default"

    def _my_type(value: str) -> int:
        return int(value) + 1

    value = d.get("foo", "default", type=_my_type)
    assert value == 43

    value = d.get("bar", "default", type=_my_type)
    assert value == "default"


def test_get_with_type_default_required() -> None:
    d = TypeConversionDict(foo="42")
    value = d.get("foo", "default", type=int, required=False)
    assert value == 42

    value = d.get("bar", "default", type=int, required=False)
    assert value == "default"

    with pytest.raises(KeyError):
        _value = d.get("bar", "default", type=int, required=True)

    def _my_type(value: str) -> int:
        if value != "hello":
            raise ValueError("value must be 'hello'")
        return 42

    value = d.get("foo", "default", type=_my_type, required=False)
    assert value == "default"

    with pytest.raises(ValueError):
        _value = d.get("foo", "default", type=_my_type, required=True)
