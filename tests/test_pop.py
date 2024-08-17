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


def test_normal_pop_default_kwarg() -> None:
    d = TypeConversionDict(foo="42")

    value = d.pop("bar", default="default")
    assert_type(value, str)
    assert value == "default"

    value = d.pop("bar", default="default", required=False)
    assert_type(value, str)
    assert value == "default"

    value_2 = d.pop("bar", default=3.14, required=False)
    assert_type(value_2, Union[str, float])
    assert value_2 == 3.14


def test_normal_pop_default_factory() -> None:
    d = TypeConversionDict(foo="42")

    i = 0

    def df() -> str:
        """Default factory with side effect to make sure it runs correctly"""
        nonlocal i
        i += 1
        return "default"

    value = d.pop("foo", default_factory=df)
    assert_type(value, str)
    assert value == "42"
    assert i == 0

    value = d.pop("bar", default_factory=df)
    assert_type(value, str)
    assert value == "default"
    assert i == 1

    # Run again. The default factory should not run again. We do not cache the result
    value = d.pop("bar", default_factory=df, required=False)
    assert_type(value, str)
    assert value == "default"
    assert i == 2

    value_2 = d.pop("bar", default_factory=lambda: 3.14, required=False)
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


def test_normal_pop_default_factory_required() -> None:
    d = TypeConversionDict(foo="42")
    df = lambda: "default"
    value = d.pop("foo", default_factory=df, required=True)
    assert value == "42"

    assert "foo" not in d

    with pytest.raises(KeyError):
        _value = d.pop("bar", 3.14, required=True)
        assert_type(_value, str)

    value = d.pop("bar", default_factory=df, required=False)
    assert value == "default"


def test_pop_with_type() -> None:
    d = TypeConversionDict(foo="42")

    with pytest.raises(KeyError):
        _value = d.pop("bar", type=int)
        assert_type(_value, int)

    def type(value: str) -> int:
        return int(value) + 1

    with pytest.raises(KeyError):
        _value = d.pop("bar", type=type)
        assert_type(_value, int)


def test_pop_with_type_required() -> None:
    d = TypeConversionDict(foo="42")

    with pytest.raises(KeyError):
        _value = d.pop("bar", type=int, required=True)
        assert_type(_value, int)

    def type(value: str) -> int:
        if value != "hello":
            raise ValueError("value must be 'hello'")
        return 42

    with pytest.raises(ValueError):
        _value = d.pop("foo", type=type, required=True)
        assert_type(_value, int)

    # 'foo' was not popped because the type conversion failed
    assert "foo" in d

    value = d.pop("foo", type=type, required=False)
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

    def type(value: str) -> int:
        return int(value) + 1

    value = d.pop("foo", "default", type=type)
    assert_type(value, Union[int, str])
    assert value == 43

    value = d.pop("bar", "default", type=type)
    assert_type(value, Union[int, str])
    assert value == "default"


def test_pop_with_type_default_factory() -> None:
    d = TypeConversionDict(foo="42")
    df = lambda: "default"

    value = d.pop("bar", default_factory=df, type=int)
    assert_type(value, Union[int, str])
    assert value == "default"

    def type(value: str) -> int:
        return int(value) + 1

    value = d.pop("foo", default_factory=df, type=type)
    assert_type(value, Union[int, str])
    assert value == 43

    value = d.pop("bar", default_factory=df, type=type)
    assert_type(value, Union[int, str])
    assert value == "default"


def test_pop_with_type_default_required() -> None:
    d = TypeConversionDict(foo="42")

    value = d.pop("bar", "default", type=int, required=False)
    assert_type(value, Union[int, str])
    assert value == "default"

    with pytest.raises(KeyError):
        _value = d.pop("bar", "default", type=int, required=True)
        assert_type(_value, int)

    def type(value: str) -> int:
        if value != "hello":
            raise ValueError("value must be 'hello'")
        return 42

    d.pop("foo")
    assert "foo" not in d

    # foo is not in d
    value = d.pop("foo", "default", type=type, required=False)
    assert_type(value, Union[int, str])
    assert value == "default"

    d["foo"] = "42"  # reset the value

    value = d.pop("foo", "default", type=type, required=False)
    assert_type(value, Union[int, str])
    assert value == "default"

    d["foo"] = "42"  # reset the value

    with pytest.raises(ValueError):
        _value = d.pop("foo", "default", type=type, required=True)
        assert_type(_value, int)


def test_pop_with_type_default_factory_required() -> None:
    d = TypeConversionDict(foo="42")
    df = lambda: "default"

    value = d.pop("bar", default_factory=df, type=int, required=False)
    assert_type(value, Union[int, str])
    assert value == "default"

    with pytest.raises(KeyError):
        _value = d.pop("bar", default_factory=df, type=int, required=True)
        assert_type(_value, int)

    def type(value: str) -> int:
        if value != "hello":
            raise ValueError("value must be 'hello'")
        return 42

    d.pop("foo")
    assert "foo" not in d

    # foo is not in d
    value = d.pop("foo", default_factory=df, type=type, required=False)
    assert_type(value, Union[int, str])
    assert value == "default"

    d["foo"] = "42"  # reset the value

    value = d.pop("foo", default_factory=df, type=type, required=False)
    assert_type(value, Union[int, str])
    assert value == "default"

    d["foo"] = "42"  # reset the value

    with pytest.raises(ValueError):
        _value = d.pop("foo", default_factory=df, type=type, required=True)
        assert_type(_value, int)


def test_pop_missing_with_type() -> None:
    d1 = TypeConversionDict(foo="42")
    assert d1.pop("foo", type=int) == 42

    # Foo is none
    d2: TypeConversionDict = TypeConversionDict(foo=None)
    with pytest.raises(ValueError):
        _value = d2.pop("foo", type=int, required=True)

    d3: TypeConversionDict = TypeConversionDict(foo=None)
    assert d3.pop("foo", type=int, required=False) is None

    d4: TypeConversionDict = TypeConversionDict(foo=None)
    with pytest.raises(ValueError):
        _value = d4.pop("foo", type=int)
        print(_value)

    # No foo
    d5: TypeConversionDict = TypeConversionDict()
    with pytest.raises(KeyError):
        _value = d5.pop("foo", type=int, required=True)

    d6: TypeConversionDict = TypeConversionDict()
    assert d6.pop("foo", type=int, required=False) is None

    d7: TypeConversionDict = TypeConversionDict()
    with pytest.raises(KeyError):
        _value = d7.pop("foo", type=int)


def test_pop_with_default_and_default_factory() -> None:
    d = TypeConversionDict(foo="42")

    i = 0

    def df() -> str:
        """Default factory with side effect to make sure it runs correctly"""
        nonlocal i
        i += 1
        return "default_factory"

    # Both of these should get you being shouted at by the type checker, but they should work
    _value = d.pop("foo", "default", default_factory=df, required=True)  # type: ignore
    assert _value == "42"
    assert "foo" not in d
    assert i == 0

    # Default factory should be ignored if default is provided
    _value = d.pop("bar", "default", default_factory=df, required=False)  # type: ignore
    assert _value == "default"
    assert "bar" not in d
    assert i == 0  # default factory should not run
