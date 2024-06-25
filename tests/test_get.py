from typing import TYPE_CHECKING, Union

import pytest
from type_conversion_dict import TypeConversionDict

if TYPE_CHECKING:
    from typing_extensions import assert_type
else:
    assert_type = lambda x, y: None


def test_normal_get() -> None:
    d = TypeConversionDict(foo="42")
    value = d.get("foo")
    assert_type(value, Union[str, None])
    assert value == "42"

    value = d.get("bar")
    assert_type(value, Union[str, None])
    assert value is None


def test_normal_get_required() -> None:
    d = TypeConversionDict(foo="42")
    value = d.get("foo", required=False)
    assert_type(value, Union[str, None])
    assert value == "42"

    value = d.get("bar", required=False)
    assert_type(value, Union[str, None])
    assert value is None

    with pytest.raises(KeyError):
        _value = d.get("bar", required=True)
        assert_type(_value, str)


def test_normal_get_default() -> None:
    d = TypeConversionDict(foo="42")
    value = d.get("foo", "default")
    assert_type(value, str)  # since the default value is a string
    assert value == "42"

    value = d.get("bar", "default")
    assert_type(value, str)
    assert value == "default"


def test_normal_get_default_required() -> None:
    d = TypeConversionDict(foo="42")
    value = d.get("foo", "default", required=False)
    assert_type(value, str)
    assert value == "42"

    value = d.get("bar", "default", required=False)
    assert_type(value, str)
    assert value == "default"

    with pytest.raises(KeyError):
        _value = d.get("bar", "default", required=True)
        assert_type(_value, str)
        _value = d.get("bar", 3.14, required=True)
        assert_type(_value, str)


def test_get_with_type() -> None:
    d = TypeConversionDict(foo="42")
    value = d.get("foo", type=int)
    assert_type(value, Union[int, None])
    assert value == 42

    value = d.get("bar", type=int)
    assert_type(value, Union[int, None])
    assert value is None

    def _my_type(value: str) -> int:
        return int(value) + 1

    value = d.get("foo", type=_my_type)
    assert_type(value, Union[int, None])
    assert value == 43


def test_get_with_type_required() -> None:
    d = TypeConversionDict(foo="42")
    value = d.get("foo", type=int, required=False)
    assert_type(value, Union[int, None])
    assert value == 42

    value = d.get("bar", type=int, required=False)
    assert_type(value, Union[int, None])
    assert value is None

    with pytest.raises(KeyError):
        _value = d.get("bar", type=int, required=True)
        assert_type(_value, int)

    def _my_type(value: str) -> int:
        if value != "hello":
            raise ValueError("value must be 'hello'")
        return 42

    value = d.get("foo", type=_my_type, required=False)
    assert_type(value, Union[int, None])
    assert value is None  # since the value is not 'hello'

    with pytest.raises(ValueError):
        _value = d.get("foo", type=_my_type, required=True)
        assert_type(_value, int)


def test_get_with_type_default() -> None:
    d = TypeConversionDict(foo="42")
    value = d.get("foo", "default", type=int)
    assert_type(value, Union[int, str])
    assert value == 42

    value = d.get("bar", "default", type=int)
    assert_type(value, Union[int, str])
    assert value == "default"

    def _my_type(value: str) -> int:
        return int(value) + 1

    value = d.get("foo", "default", type=_my_type)
    assert_type(value, Union[int, str])
    assert value == 43

    value = d.get("bar", "default", type=_my_type)
    assert_type(value, Union[int, str])
    assert value == "default"


def test_get_with_type_default_required() -> None:
    d = TypeConversionDict(foo="42")
    value = d.get("foo", "default", type=int, required=False)
    assert_type(value, Union[int, str])
    assert value == 42

    value = d.get("bar", "default", type=int, required=False)
    assert_type(value, Union[int, str])
    assert value == "default"

    with pytest.raises(KeyError):
        _value = d.get("bar", "default", type=int, required=True)
        assert_type(_value, int)

    def _my_type(value: str) -> int:
        if value != "hello":
            raise ValueError("value must be 'hello'")
        return 42

    value = d.get("foo", "default", type=_my_type, required=False)
    assert_type(value, Union[int, str])
    assert value == "default"

    with pytest.raises(ValueError):
        _value = d.get("foo", "default", type=_my_type, required=True)
        assert_type(_value, int)


def test_get_missing_with_type() -> None:
    d1 = TypeConversionDict(foo="42")
    assert d1.get("foo", type=int) == 42

    # Foo is none
    d2: TypeConversionDict = TypeConversionDict(foo=None)
    with pytest.raises(ValueError):
        _value = d2.get("foo", type=int, required=True)

    d3: TypeConversionDict = TypeConversionDict(foo=None)
    assert d3.get("foo", type=int, required=False) is None

    d4: TypeConversionDict = TypeConversionDict(foo=None)
    assert d4.get("foo", type=int) is None

    # No foo
    d5: TypeConversionDict = TypeConversionDict()
    with pytest.raises(KeyError):
        _value = d5.get("foo", type=int, required=True)

    d6: TypeConversionDict = TypeConversionDict()
    assert d6.get("foo", type=int, required=False) is None

    d7: TypeConversionDict = TypeConversionDict()
    assert d7.get("foo", type=int) is None
