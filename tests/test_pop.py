from typing import TYPE_CHECKING, Union

import pytest
from type_conversion_dict import TypeConversionDict

if TYPE_CHECKING:
    from typing_extensions import assert_type
else:
    assert_type = lambda x, y: None


def test_normal_pop() -> None:
    d = TypeConversionDict(foo="42")
    value = d.pop("foo")
    assert_type(value, str)
    assert value == "42"

    with pytest.raises(KeyError):
        _value = d.pop("foo")


def test_normal_pop_required() -> None:
    d = TypeConversionDict(foo="42")

    with pytest.raises(KeyError):
        _value = d.pop("bar", required=True)

    value = d.pop("bar", required=False)
    assert_type(value, Union[str, None])
    assert value is None


def test_normal_pop_default() -> None:
    d = TypeConversionDict(foo="42")

    value = d.pop("bar", "default")
    assert_type(value, str)
    assert value == "default"

    value = d.pop("bar", "default", required=False)
    assert_type(value, str)
    assert value == "default"

    value_2 = d.pop("bar", 3.14, required=False)
    assert_type(value_2, Union[str, float])
    assert value_2 == 3.14


def test_normal_pop_default_required() -> None:
    d = TypeConversionDict(foo="42")
    value = d.pop("foo", "default", required=True)
    assert value == "42"

    assert "foo" not in d

    with pytest.raises(KeyError):
        _value = d.pop("bar", 3.14, required=True)
        assert_type(_value, str)

    value = d.pop("bar", "default", required=False)
    assert value == "default"


def test_pop_with_type() -> None:
    d = TypeConversionDict(foo="42")

    with pytest.raises(KeyError):
        _value = d.pop("bar", type=int)
        assert_type(_value, int)

    def _my_type(value: str) -> int:
        return int(value) + 1

    with pytest.raises(KeyError):
        _value = d.pop("bar", type=_my_type)
        assert_type(_value, int)


def test_pop_with_type_required() -> None:
    d = TypeConversionDict(foo="42")

    with pytest.raises(KeyError):
        _value = d.pop("bar", type=int, required=True)
        assert_type(_value, int)

    def _my_type(value: str) -> int:
        if value != "hello":
            raise ValueError("value must be 'hello'")
        return 42

    with pytest.raises(ValueError):
        _value = d.pop("foo", type=_my_type, required=True)
        assert_type(_value, int)

    # 'foo' was not popped because the type conversion failed
    assert "foo" in d

    value = d.pop("foo", type=_my_type, required=False)
    assert_type(value, Union[int, None])
    assert value is None

    # 'foo' was not popped because the type conversion failed
    assert "foo" in d


def test_from_docstring() -> None:
    d = TypeConversionDict(foo="42", bar="blub")
    d.pop("foo", type=int)
    value = d.pop("bar", -1, type=int)
    assert_type(value, int)


def test_pop_with_type_default() -> None:
    d = TypeConversionDict(foo="42")

    value = d.pop("bar", "default", type=int)
    assert_type(value, Union[int, str])
    assert value == "default"

    def _my_type(value: str) -> int:
        return int(value) + 1

    value = d.pop("foo", "default", type=_my_type)
    assert_type(value, Union[int, str])
    assert value == 43

    value = d.pop("bar", "default", type=_my_type)
    assert_type(value, Union[int, str])


def test_pop_with_type_default_required() -> None:
    d = TypeConversionDict(foo="42")

    value = d.pop("bar", "default", type=int, required=False)
    assert_type(value, Union[int, str])
    assert value == "default"

    with pytest.raises(KeyError):
        _value = d.pop("bar", "default", type=int, required=True)
        assert_type(_value, int)

    def _my_type(value: str) -> int:
        if value != "hello":
            raise ValueError("value must be 'hello'")
        return 42

    d.pop("foo")
    assert "foo" not in d

    # foo is not in d
    value = d.pop("foo", "default", type=_my_type, required=False)
    assert_type(value, Union[int, str])
    assert value == "default"

    d["foo"] = "42"  # reset the value

    value = d.pop("foo", "default", type=_my_type, required=False)
    assert_type(value, Union[int, str])
    assert value == "default"

    d["foo"] = "42"  # reset the value

    with pytest.raises(ValueError):
        _value = d.pop("foo", "default", type=_my_type, required=True)
        assert_type(_value, int)


def test_pop_missing_with_type() -> None:
    d = TypeConversionDict(foo="42")
    assert d.pop("foo", type=int) == 42

    # Foo is none
    d: TypeConversionDict = TypeConversionDict(foo=None)
    with pytest.raises(ValueError):
        _value = d.pop("foo", type=int, required=True)

    d = TypeConversionDict(foo=None)
    assert d.pop("foo", type=int, required=False) is None

    d = TypeConversionDict(foo=None)
    with pytest.raises(ValueError):
        _value = d.pop("foo", type=int)

    # No foo
    d: TypeConversionDict = TypeConversionDict()
    with pytest.raises(KeyError):
        _value = d.pop("foo", type=int, required=True)

    d = TypeConversionDict()
    assert d.pop("foo", type=int, required=False) is None

    d = TypeConversionDict()
    with pytest.raises(KeyError):
        _value = d.pop("foo", type=int)
