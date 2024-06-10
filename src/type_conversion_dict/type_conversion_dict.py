"""
Single-file module with type conversion dict.
Inspired by werzeug.datastructures.TypeConversionDict.

Written by Marcin Konowalczyk.
"""

_missing = object()

from typing import Callable, TypeVar, overload, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from typing_extensions import override
else:
    override = lambda f: f

_K = TypeVar("_K")
_V = TypeVar("_V")
_D = TypeVar("_D")
_T = TypeVar("_T")

__version__ = "0.1.0"

__all__ = ["TypeConversionDict"]


class TypeConversionDict(dict[_K, _V]):
    """Works like a regular dict but the :meth:`get`"""

    @overload
    def get(self, key: _K, default: None = ..., type: None = ...) -> Union[_V, None]: ...

    @overload
    def get(self, key: _K, default: _D, type: None = ...) -> Union[_D, _V]: ...

    @overload
    def get(self, key: _K, default: _D, type: Callable[[_V], _T]) -> Union[_D, _T]: ...

    @overload
    def get(self, key: _K, type: Callable[[_V], _T]) -> Union[_T, None]: ...

    @override  # type: ignore[misc]
    def get(self, key, default=None, type=None):  # type: ignore[no-untyped-def]
        """Return the default value if the requested data doesn't exist.
        If `type` is provided and is a callable it should convert the value,
        return it or raise a :exc:`ValueError` if that is not possible.  In
        this case the function will return the default as if the value was not
        found:

        >>> d = TypeConversionDict(foo='42', bar='blub')
        >>> d.get('foo', type=int)
        42
        >>> d.get('bar', -1, type=int)
        -1

        :param key: The key to be looked up.
        :param default: The default value to be returned if the key can't
                        be looked up.  If not further specified `None` is
                        returned.
        :param type: A callable that is used to cast the value in the
                     :class:`MultiDict`.  If a :exc:`ValueError` or a
                     :exc:`TypeError` is raised by this callable the default
                     value is returned.
        """
        try:
            rv = self[key]
        except KeyError:
            return default
        if type is not None:
            try:
                rv = type(rv)
            except (ValueError, TypeError):
                rv = default
        return rv

    @overload
    def pop(self, key: _K) -> _V: ...

    @overload
    def pop(self, key: _K, default: _V) -> _V: ...

    @overload
    def pop(self, key: _K, default: _D) -> Union[_V, _D]: ...

    @overload
    def pop(self, key: _K, default: _D, type: Callable[[_V], _T]) -> Union[_D, _T]: ...

    @overload
    def pop(self, key: _K, type: Callable[[_V], _T]) -> Union[_T, None]: ...

    @override  # type: ignore[misc]
    def pop(self, key, default=_missing, type=None):  # type: ignore[no-untyped-def]
        """Like :meth:`get` but removes the key/value pair.

        >>> d = TypeConversionDict(foo='42', bar='blub')
        >>> d.pop('foo', type=int)
        42
        >>> 'foo' in d
        False
        >>> d.pop('bar', -1, type=int)
        -1
        >>> 'bar' in d
        False

        :param key: The key to be looked up.
        :param default: The default value to be returned if the key is not
                        in the dictionary. If not further specified it's
                        an :exc:`KeyError`.
        :param type: A callable that is used to cast the value in the dict.
                        If a :exc:`ValueError` or a :exc:`TypeError` is raised
                        by this callable the default value is returned.

        .. admonition:: note

           If the type conversion fails, the key is **not** removed from the
           dictionary.

        """
        try:
            rv = self[key]
        except KeyError:
            if default is _missing:
                raise
            return default
        if type is not None:
            try:
                rv = type(rv)
            except (ValueError, TypeError):
                if default is _missing:
                    return None
                return default
        try:
            # This method is not meant to be thread-safe, but at least lets not
            # fall over if the dict was mutated between the get and the delete. -MK
            del self[key]
        except KeyError:
            pass
        return rv
