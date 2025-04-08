from typing import TYPE_CHECKING, Union

import pytest

from type_conversion_dict import TypeConversionDict

if TYPE_CHECKING:
    from typing_extensions import assert_type
else:
    assert_type = lambda x, y: None  # noqa: E731


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


def test_normal_get_default_kwarg() -> None:
    d = TypeConversionDict(foo="42")
    value = d.get("foo", default="default")
    assert_type(value, str)  # since the default value is a string
    assert value == "42"

    value = d.get("bar", default="default")
    assert_type(value, str)
    assert value == "default"


def test_normal_get_default_factory() -> None:
    _i = 0

    def df() -> str:
        """Default factory with side effect to make sure it runs correctly"""
        nonlocal _i
        _i += 1
        return "default"

    d = TypeConversionDict(foo="42")
    value = d.get("foo", default_factory=df)
    assert_type(value, str)  # since the default value is a string
    assert value == "42"
    assert _i == 0

    value = d.get("bar", default_factory=df)
    assert_type(value, str)
    assert value == "default"
    assert _i == 1

    # Run again. The default factory should be called again. We do not cache the result
    value = d.get("bar", default_factory=df)
    assert_type(value, str)
    assert value == "default"
    assert _i == 2


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

    # make sure that the type of the default value is still 'str' even if default is 'float'
    with pytest.raises(KeyError):
        _value = d.get("bar", 3.14, required=True)
        assert_type(_value, str)


def test_normal_get_default_factory_required() -> None:
    d = TypeConversionDict(foo="42")
    df = lambda: "default"  # noqa: E731
    value = d.get("foo", default_factory=df, required=False)
    assert_type(value, str)
    assert value == "42"

    value = d.get("bar", default_factory=df, required=False)
    assert_type(value, str)
    assert value == "default"

    with pytest.raises(KeyError):
        _value = d.get("bar", default_factory=df, required=True)
        assert_type(_value, str)

    # make sure that the type of the default value is still 'str' even if default_factory returns 'float'
    with pytest.raises(KeyError):
        _value = d.get("bar", default_factory=lambda: 3.14, required=True)
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


def test_get_with_type_default_factory() -> None:
    d = TypeConversionDict(foo="42")
    df = lambda: "default"  # noqa: E731
    value = d.get("foo", default_factory=df, type=int)
    assert_type(value, Union[int, str])
    assert value == 42

    value = d.get("bar", default_factory=df, type=int)
    assert_type(value, Union[int, str])
    assert value == "default"

    def _my_type(value: str) -> int:
        return int(value) + 1

    value = d.get("foo", default_factory=df, type=_my_type)
    assert_type(value, Union[int, str])
    assert value == 43

    value = d.get("bar", default_factory=df, type=_my_type)
    assert_type(value, Union[int, str])
    assert value == "default"


def test_get_with_type_default_required() -> None:
    d = TypeConversionDict(foo="42")
    df = lambda: "default"  # noqa: E731
    value = d.get("foo", default_factory=df, type=int, required=False)
    assert_type(value, Union[int, str])
    assert value == 42

    value = d.get("bar", default_factory=df, type=int, required=False)
    assert_type(value, Union[int, str])
    assert value == "default"

    with pytest.raises(KeyError):
        _value = d.get("bar", default_factory=df, type=int, required=True)
        assert_type(_value, int)

    def _my_type(value: str) -> int:
        if value != "hello":
            raise ValueError("value must be 'hello'")
        return 42

    value = d.get("foo", default_factory=df, type=_my_type, required=False)
    assert_type(value, Union[int, str])
    assert value == "default"

    with pytest.raises(ValueError):
        _value = d.get("foo", default_factory=df, type=_my_type, required=True)
        assert_type(_value, int)


def test_get_with_type_default_factory_required() -> None:
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


def test_get_with_default_and_default_factory() -> None:
    d = TypeConversionDict(foo="42")

    i = 0

    def df() -> str:
        """Default factory with side effect to make sure it runs correctly"""
        nonlocal i
        i += 1
        return "default_factory"

    # Both of these should get you being shouted at by the type checker, but they should work
    _value = d.get("foo", "default", default_factory=df, required=True)  # type: ignore
    assert _value == "42"
    assert i == 0

    # Default factory should be ignored if default is provided
    _value = d.get("bar", "default", default_factory=df, required=False)  # type: ignore
    assert _value == "default"
    assert i == 0  # default factory should not run


def test_default_factory_classes() -> None:
    d = TypeConversionDict(foo="42")

    # Make sure we can instantiate basic types
    value_2: Union[list, str] = d.get("bar", default_factory=list)
    assert_type(value_2, Union[list, str])
    assert value_2 == []

    # Make sure we can instantiate classes
    class MyClass:
        pass

    value_3: Union[MyClass, str] = d.get("bar", default_factory=MyClass)
    assert_type(value_3, Union[MyClass, str])
    assert isinstance(value_3, MyClass)
