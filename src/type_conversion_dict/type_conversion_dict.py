"""
Single-file module with type-conversion dict.

Inspired by werzeug.datastructures.TypeConversionDict.
Written by Marcin Konowalczyk.
"""

from typing import TYPE_CHECKING, Callable, Literal, TypeVar, Union, overload

if TYPE_CHECKING:
    # import like this not to acquire a dependency on typing_extensions
    from typing_extensions import override
else:
    override = lambda f: f

_K = TypeVar("_K")  # key
_V = TypeVar("_V")  # value
_D = TypeVar("_D")  # default
_T = TypeVar("_T")  # converted type

__version__ = "0.1.3"

__all__ = ["TypeConversionDict"]

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

    # Get with required. Default is ignored and the key is required. Equivalent to [] access

    @overload
    def get(self, key: _K, *, required: Literal[True]) -> _V: ...
    @overload
    def get(self, key: _K, default: object, *, required: Literal[True]) -> _V: ...

    # Get with type and required.
    # Default is ignored and the key is required.
    # Type conversion must succeed or a ValueError is raised.
    # Equivalent to [] access but with type conversion.

    @overload
    def get(self, key: _K, *, type: Callable[[_V], _T], required: Literal[True]) -> _T: ...
    @overload
    def get(self, key: _K, default: object, *, type: Callable[[_V], _T], required: Literal[True]) -> _T: ...

    @override
    def get(  # type: ignore[no-untyped-def]
        self,
        key,
        default=_missing,  # Default to None
        *,
        type=_missing,  # Default to no type conversion
        required=_missing,  # Default to False
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
                        be looked up. If not further specified `None` is
                        returned.
        :param type: A callable that is used to cast the value in the
                     :class:`MultiDict`. If a :exc:`ValueError` or a
                     :exc:`TypeError` is raised by this callable the default
                     value is returned.
        :param required: If set to `True` the key is required. If set to
                        `False` the default value is returned instead.
        """
        __tracebackhide__ = True
        try:
            rv = self[key]
        except KeyError:
            if required is _missing or not required:
                # required is False. return default
                if default is _missing or default is None:
                    # default is not provided. return None
                    return None
                return default
            raise

        # Check for rv already being the default value. If so, return it without type conversion
        if default is _missing or default is None:
            if rv is None:
                if required is _missing or not required:
                    return None
                else:
                    raise ValueError(f"Required key {key} is None")
        else:
            if rv is default or _type(rv) is _type(default) and rv == default:
                return rv

        # Type conversion
        if type is not _missing:
            try:
                rv = type(rv)  # pyright: ignore[reportCallIssue]
            except ValueError:
                if required is _missing or not required:
                    # Type conversion failed. Return default
                    if default is _missing or default is None:
                        return None
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
                        in the dictionary. If not further specified it's
                        an :exc:`KeyError`.
        :param type: A callable that is used to cast the value in the dict.
                        If a :exc:`ValueError` or a :exc:`TypeError` is raised
                        by this callable the default value is returned.
        :param required: If set to `True` the key is required. If set to
                        `False` the default value is returned instead.

        .. admonition:: note

           If the type conversion fails, the key is **not** removed from the
           dictionary.

        """
        __tracebackhide__ = True
        try:
            rv = self[key]
        except KeyError:
            if default is _missing:
                # No default, therefore behave as if required is True by default
                if required is _missing or required:
                    raise
                return None
            else:
                # default is provided, therefore behave as if required is False by default
                if required is _missing or not required:
                    return default
                raise

        # Check for rv already being the default value. If so, return it without type conversion
        _skip_type_conversion = False
        if default is _missing:
            # No default, therefore behave as if required is True by default
            if rv is None:
                if required is _missing or required:
                    raise ValueError(f"Required key {key} is None")
                else:
                    return None
        else:
            if rv is default or _type(rv) is _type(default) and rv == default:
                _skip_type_conversion = True

        if type is not _missing and not _skip_type_conversion:
            try:
                rv = type(rv)  # pyright: ignore[reportCallIssue]
            except ValueError:
                if default is _missing:
                    # No default, therefore behave as if required is True by default
                    if required is _missing or required:
                        raise
                    return None
                else:
                    # default is provided, therefore behave as if required is False by default
                    if required is _missing or not required:
                        return default
                    raise
        try:
            # This method is not meant to be thread-safe, but at least lets not
            # fall over if the dict was mutated between the get and the delete. -MK
            del self[key]
        except KeyError:
            pass
        return rv
