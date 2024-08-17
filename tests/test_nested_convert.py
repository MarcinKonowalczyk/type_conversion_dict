import pytest

from type_conversion_dict import TypeConversionDict, nested_convert


def test_nested_convert_dicts() -> None:
    d = {"a": {"b": {"c": "1"}}}

    dc = nested_convert(d)

    assert isinstance(dc, TypeConversionDict)
    assert isinstance(dc["a"], TypeConversionDict)


def test_nested_convert_lists() -> None:
    d = {"a": [{"b": "1"}]}

    dc = nested_convert(d)

    assert isinstance(dc, TypeConversionDict)
    assert isinstance(dc["a"], list)
    assert isinstance(dc["a"][0], TypeConversionDict)


def test_nested_convert_lists_of_dicts() -> None:
    d = [{"a": {"b": "1"}}, {"a": {"b": "2"}}]

    dc = nested_convert(d)

    assert isinstance(dc, list)
    assert isinstance(dc[0], TypeConversionDict)
    assert isinstance(dc[1], TypeConversionDict)


def test_raises_with_other_types() -> None:
    with pytest.raises(TypeError):
        nested_convert(1)  # type: ignore

    assert nested_convert(1, _depth=1) == 1
