# type_conversion_dict

Single-file module with type-conversion dict.

Inspired by [werzeug.datastructures.TypeConversionDict](https://github.com/pallets/werkzeug/blob/62e3ea45846d06576199a2f8470be7fe44c867c1/src/werkzeug/datastructures/structures.py).

Tested in Python 3.9+.

# Usage

```python
>>> from type_conversion_dict import TypeConversionDict
>>> d = TypeConversionDict(foo='42', bar='blub')
>>> d.get('foo', type=int)
42
>>> d.get('bar', -1, type=int)
-1
```

## Install

Just copy the sintle-module file to your project and import it.

```bash
cp ./src/type_conversion_dict/type_conversion_dict.py <wherever-your-heart-deisres>
```

Or even better, without checking out the repository:

```bash
curl -O https://raw.githubusercontent.com/MarcinKonowalczyk/type_conversion_dict/main/src/type_conversion_dict/type_conversion_dict.py
```

Or build and install the package.

```bash
pip install flit
flit build
ls dist/*
pip install dist/*.whl
```
