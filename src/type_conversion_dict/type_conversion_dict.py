"""
Single-file module with type-conversion dict.

Hosted at https://github.com/MarcinKonowalczyk/type_conversion_dict

Inspired by werzeug.datastructures.TypeConversionDict.
Written by Marcin Konowalczyk.
"""

from typing import TYPE_CHECKING, Any, Callable, Literal, TypeVar, Union, overload

if TYPE_CHECKING:
    # import like this not to acquire a dependency on typing_extensions
    from typing_extensions import override
else:
    override = lambda f: f

_K = TypeVar("_K")  # key
_V = TypeVar("_V")  # value
_D = TypeVar("_D")  # default value
_T = TypeVar("_T")  # converted type

__version__ = "0.2.1"

__all__ = ["TypeConversionDict", "nested_convert"]

_missing = object()

_type = type


class TypeConversionDict(dict[_K, _V]):
    """Works like a regular dict but :meth:`get` and :meth:`pop` but can
    convert values to a specified type, and handle/enforce required values.
    """

    # Normal get
    # If the key is not found, None is returned

    @overload
    def get(self, key: _K) -> Union[_V, None]: ...
    @overload
    def get(self, key: _K, *, required: Literal[False]) -> Union[_V, None]: ...

    # Normal get with default
    # If the key is not found, the default is returned

    @overload
    def get(self, key: _K, default: _D) -> Union[_D, _V]: ...
    @overload
    def get(self, key: _K, default: _D, *, required: Literal[False]) -> Union[_D, _V]: ...
    @overload
    def get(self, key: _K, *, default_factory: Callable[[], _D]) -> Union[_D, _V]: ...
    @overload
    def get(self, key: _K, *, default_factory: Callable[[], _D], required: Literal[False]) -> Union[_D, _V]: ...

    # Get with type. No default therefore default is None

    @overload
    def get(self, key: _K, *, type: Callable[[_V], _T]) -> Union[_T, None]: ...
    @overload
    def get(self, key: _K, *, type: Callable[[_V], _T], required: Literal[False]) -> Union[_T, None]: ...

    # Get with default and type. Default is returned if key is not found.
    # The default is *not* run through the type conversion
    # If the type conversion fails, the default is returned
    # This is the same behaviour as werzeug's TypeConversionDict

    @overload
    def get(self, key: _K, default: _D, *, type: Callable[[_V], _T]) -> Union[_D, _T]: ...
    @overload
    def get(self, key: _K, default: _D, *, type: Callable[[_V], _T], required: Literal[False]) -> Union[_D, _T]: ...
    @overload
    def get(self, key: _K, *, default_factory: Callable[[], _D], type: Callable[[_V], _T]) -> Union[_D, _T]: ...
    @overload
    def get(
        self, key: _K, *, default_factory: Callable[[], _D], type: Callable[[_V], _T], required: Literal[False]
    ) -> Union[_D, _T]: ...

    # Get with required. Default is ignored and the key is required. Equivalent to [] access

    @overload
    def get(self, key: _K, *, required: Literal[True]) -> _V: ...
    @overload
    def get(self, key: _K, default: object, *, required: Literal[True]) -> _V: ...
    @overload
    def get(self, key: _K, *, default_factory: object, required: Literal[True]) -> _V: ...

    # Get with type and required.
    # Default is ignored and the key is required.
    # Type conversion must succeed or a ValueError is raised.
    # Equivalent to [] access but with type conversion.

    @overload
    def get(self, key: _K, *, type: Callable[[_V], _T], required: Literal[True]) -> _T: ...
    @overload
    def get(self, key: _K, default: object, *, type: Callable[[_V], _T], required: Literal[True]) -> _T: ...
    @overload
    def get(self, key: _K, *, default_factory: object, type: Callable[[_V], _T], required: Literal[True]) -> _T: ...

    @override
    def get(  # type: ignore[no-untyped-def]
        self,
        key,
        default=None,
        *,
        default_factory=_missing,  # Default to no default_factory
        type=_missing,  # Default to no type conversion
        required=False,  # Default to False
    ):
        """Return the default value if the requested data doesn't exist.
        If `type` is provided and is a callable it should convert the value,
        return it or raise a :exc:`ValueError` if that is not possible. In
        this case the function will return the default as if the value was not
        found:

        >>> d = TypeConversionDict(foo='42', bar='blub')
        >>> d.get('foo', type=int)
        42
        >>> d.get('bar', -1, type=int)
        -1

        :param key: The key to be looked up.
        :param default: The default value to be returned if the key can't
            be looked up. If not further specified `None` is returned.
            Mutually exclusive with `default_factory`.
        :param default_factory: A callable that returns the default value.
            Useful for expensive default value generation.
            Mutually exclusive with `default`.
        :param type: A callable that is used to cast the value. If a ValueError
            or is raised by this callable the default value is
            returned.
        :param required: If set to `True` the key is required. If set to False
            the default value is returned instead.
        """

        __tracebackhide__ = True

        # Get the value from self and handle what to do if it's not found
        try:
            rv = self[key]
        except KeyError:
            if not required:
                # required is False. return default
                if default is None:
                    # default is not provided. what about default_factory?
                    if default_factory is _missing:
                        return None
                    else:
                        # default_factory is provided. return its result
                        # we do not handle the errors in default_factory
                        return default_factory()
                return default
            raise

        # Check for rv already being the default value. If so, return it without type conversion
        if default is None:
            # default value is missing. how about the default_factory though?
            if default_factory is _missing:
                if rv is None:
                    if not required:
                        return None
                    else:
                        raise ValueError(f"Required key {key} is None")
            else:
                # we have rv, no default value and a default_factory.
                # if we had the default value we'd want to check if rv is the default value
                # and then optionally skip the type conversion. since the default_factory
                # can be expensive, we just run the type conversion
                pass
        else:  # noqa: PLR5501
            # we have a default value. check if rv is the default value
            if rv is default or _type(rv) is _type(default) and rv == default:
                return rv

        # Type conversion
        if type is not _missing:
            try:
                rv = type(rv)  # pyright: ignore[reportCallIssue]
            except ValueError:
                if not required:
                    # Type conversion failed. Return default
                    if default is None:
                        # no default. how about default_factory?
                        if default_factory is _missing:
                            return None
                        else:
                            return default_factory()
                    else:
                        return default
                raise

        return rv

    # Normal pop
    # If the key is not found, None is returned

    @overload
    def pop(self, key: _K) -> _V: ...
    @overload
    def pop(self, key: _K, *, required: Literal[True]) -> _V: ...

    # Normal pop with default
    # If the key is not found, the default is returned
    # Presence of default overrides required unless required is also explicitly set to True

    @overload
    def pop(self, key: _K, default: _D) -> Union[_D, _V]: ...
    @overload
    def pop(self, key: _K, default: _D, *, required: Literal[False]) -> Union[_D, _V]: ...
    @overload
    def pop(self, key: _K, default: object, *, required: Literal[True]) -> _V: ...
    @overload
    def pop(self, key: _K, *, default_factory: Callable[[], _D]) -> Union[_D, _V]: ...
    @overload
    def pop(self, key: _K, *, default_factory: Callable[[], _D], required: Literal[False]) -> Union[_D, _V]: ...
    @overload
    def pop(self, key: _K, *, default_factory: object, required: Literal[True]) -> _V: ...

    # Get with type. No default therefore default is None

    @overload
    def pop(self, key: _K, *, type: Callable[[_V], _T]) -> _T: ...
    @overload
    def pop(self, key: _K, *, type: Callable[[_V], _T], required: Literal[True]) -> _T: ...

    # Get with default and type. Default is returned if key is not found.
    # The default is *not* run through the type conversion
    # If the type conversion fails, the default is returned
    # This is the same behaviour as werzeug's TypeConversionDict

    @overload
    def pop(self, key: _K, default: _D, *, type: Callable[[_V], _T]) -> Union[_D, _T]: ...
    @overload
    def pop(self, key: _K, default: _D, *, type: Callable[[_V], _T], required: Literal[False]) -> Union[_D, _T]: ...
    @overload
    def pop(self, key: _K, default: object, *, type: Callable[[_V], _T], required: Literal[True]) -> _T: ...
    @overload
    def pop(self, key: _K, *, default_factory: Callable[[], _D], type: Callable[[_V], _T]) -> Union[_D, _T]: ...
    @overload
    def pop(
        self, key: _K, *, default_factory: Callable[[], _D], type: Callable[[_V], _T], required: Literal[False]
    ) -> Union[_D, _T]: ...
    @overload
    def pop(self, key: _K, *, default_factory: object, type: Callable[[_V], _T], required: Literal[True]) -> _T: ...

    # Get with required. Default is ignored and the key is required. Equivalent to [] access

    @overload
    def pop(self, key: _K, *, required: Literal[False]) -> Union[_V, None]: ...

    # Get with type and required.
    # Default is ignored and the key is required.
    # Type conversion must succeed or a ValueError is raised.
    # Equivalent to [] access but with type conversion.

    @overload
    def pop(self, key: _K, *, type: Callable[[_V], _T], required: Literal[False]) -> Union[_T, None]: ...

    @override
    def pop(  # type: ignore[no-untyped-def]
        self,
        key,
        default=_missing,  # Default to None
        *,
        default_factory=_missing,
        type=_missing,  # Default to no type conversion
        required=_missing,  # Default to mixed behaviour
    ):
        """Like :meth:`get` but removes the key/value pair.

        >>> d = TypeConversionDict(foo='42', bar='blub')
        >>> d.pop('foo', type=int)
        42
        >>> 'foo' in d
        False
        >>> d.pop('bar', -1, type=int)
        -1
        >>> 'bar' in d
        True

        :param key: The key to be looked up.
        :param default: The default value to be returned if the key is not
            in the dictionary. If not further specified it's a KeyError
            exception. Mutually exclusive with `default_factory`.
        :param default_factory: A callable that returns the default value.
            Useful for expensive default value generation.
            Mutually exclusive with `default`.
        :param type: A callable that is used to cast the value in the dict.
            If a ValueError is raised by this callable the default
            value is returned.
        :param required: If set to `True` the key is required. If set to
                        `False` the default value is returned instead.

        .. admonition:: note

           If the type conversion fails, the key is **not** removed from the
           dictionary.
        """

        __tracebackhide__ = True

        # Get the value from self and handle what to do if it's not found
        try:
            rv = self[key]
        except KeyError:
            if default is _missing:
                # No default, but lets check for default_factory
                if default_factory is _missing:
                    # No default or default_factory, therefore behave as if required is True by default
                    if required is _missing or required:
                        raise
                    return None
                else:
                    # default_factory is provided, therefore behave as if required is False by default
                    if required is _missing or not required:
                        return default_factory()
                    raise
            else:
                # default is provided, therefore behave as if required is False by default
                if required is _missing or not required:
                    return default
                raise

        # Check for rv already being the default value. If so, return it without type conversion
        _skip_type_conversion = False
        if default is _missing:
            # No default, but lets check for default_factory
            if default_factory is _missing:
                # No default or default_factory, therefore behave as if required is True by default
                if rv is None:
                    if required is _missing or required:
                        raise ValueError(f"Required key {key} is None")
                    else:
                        return None
            else:
                # We have the rv, no default value and a default_factory.
                # No skipping of type conversion here, as default_factory can be expensive
                pass
        else:  # noqa: PLR5501
            # Maybe skip type conversion
            if rv is default or _type(rv) is _type(default) and rv == default:
                _skip_type_conversion = True

        if type is not _missing and not _skip_type_conversion:
            try:
                rv = type(rv)  # pyright: ignore[reportCallIssue]
            except ValueError:
                if default is _missing:
                    # No default, but lets check for default_factory
                    if default_factory is _missing:
                        # No default or default_factory, therefore behave as if required is True by default
                        if required is _missing or required:
                            raise
                        return None
                    else:
                        # default_factory is provided, therefore behave as if required is False by default
                        if required is _missing or not required:
                            return default_factory()
                        raise
                else:
                    # default is provided, therefore behave as if required is False by default
                    if required is _missing or not required:
                        return default
                    raise
        try:  # noqa: SIM105, RUF100
            # This method is not meant to be thread-safe, but at least lets not
            # fall over if the dict was mutated between the get and the delete. -MK
            del self[key]
        except KeyError:
            pass
        return rv


# NOTE: Python is not great with recursive types. For now there are just
# two overloads for nested_convert. One for dict and one for list, but they
# drop the value type on purpose.


@overload
def nested_convert(d: dict[_K, _V]) -> TypeConversionDict[_K, Any]: ...
@overload
def nested_convert(d: list) -> list: ...
@overload
def nested_convert(d: Any, *, _depth: int) -> Any: ...


def nested_convert(
    d: Union[dict, list],
    *,
    _depth: int = 0,
) -> Union[TypeConversionDict, list]:
    """Convert a nested dict to a TypeConversionDict.
    Nested dicts and dicts inside lists are converted recursively.
    This is particularly useful when converting JSON to a TypeConversionDict.

    This function is provided as a convenience for a common operation and
    a reference implementation.

    >>> d = {"a": {"b": [{"c": "1"}]}}
    >>> dc = nested_convert(d)
    >>> isinstance(dc, TypeConversionDict)
    True
    >>> isinstance(dc["a"], TypeConversionDict)
    True
    >>> isinstance(dc["a"]["b"][0], TypeConversionDict)
    True

    :param d: The dict or list to convert.
    :param _depth: Internal parameter for recursion depth tracking.
    :return: The converted dict or list.

    """

    if isinstance(d, dict):
        kv = ((k, nested_convert(v, _depth=_depth + 1)) for k, v in d.items())
        return TypeConversionDict(kv)
    elif isinstance(d, list):
        vs = (nested_convert(v, _depth=_depth + 1) for v in d)
        return list(vs)
    else:
        if _depth == 0:
            raise TypeError("Input must be a dict or a list")
        return d


__license__ = """
Copyright 2007-2024 Pallets
Copyright 2024 Marcin Konowalczyk

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

1.  Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.

2.  Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.

3.  Neither the name of the copyright holder nor the names of its
    contributors may be used to endorse or promote products derived from
    this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
