import pytest
from type_conversion_dict import TypeConversionDict


def test_basic() -> None:
    d = TypeConversionDict(foo="42", bar="blub")
    value = d.pop("foo", type=int)
    assert value == 42
    assert "foo" not in d


@pytest.mark.skip(reason="Not implemented")
def test_pop_type_conversion_fails_1() -> None:
    d = TypeConversionDict(foo="42", bar="blub")
    with pytest.raises(ValueError):
        d.pop("bar", type=int)

    assert "bar" in d


def test_pop_type_conversion_fail_2() -> None:
    d = TypeConversionDict(foo="42", bar="blub")
    value = d.pop("bar", -1, type=int)
    assert value == -1
    # 'bar' was not popped because the type conversion failed
    assert "bar" in d


# >>> d = TypeConversionDict(foo='42', bar='blub')
# >>> d.pop('foo', type=int)
# 42
# >>> 'foo' in d
# False
# >>> d.pop('bar', -1, type=int)
# -1
# >>> 'bar' in d
