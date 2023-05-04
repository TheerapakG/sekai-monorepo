# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

from dataclasses import fields, is_dataclass
from datetime import datetime
from functools import partial
from typing import Union, get_args, get_origin

from async_pjsekai.enums.unknown import Unknown

from cattrs.converters import BaseConverter
from cattrs.preconf.json import make_converter as make_json_converter
from cattrs.preconf.msgpack import make_converter as make_msgpack_converter
from cattrs.gen import make_dict_unstructure_fn, make_dict_structure_fn, override

json_converter = make_json_converter()
msgpack_converter = make_msgpack_converter()


def to_lower_camel(string: str) -> str:
    split = string.split("_")
    return "".join((split[0].lower(), *(word.capitalize() for word in split[1:])))


def to_pjsekai_camel(string: str) -> str:
    return (
        to_lower_camel(string)
        .replace("AssetBundle", "Assetbundle")
        .replace("assetBundle", "assetbundle")
    )


def to_pjsekai_camel_unstructure(converter: BaseConverter, cls):
    return make_dict_unstructure_fn(
        cls,
        converter,
        **{a.name: override(rename=to_pjsekai_camel(a.name)) for a in fields(cls)}
    )


def to_pjsekai_camel_structure(converter: BaseConverter, cls):
    return make_dict_structure_fn(
        cls,
        converter,
        **{a.name: override(rename=to_pjsekai_camel(a.name)) for a in fields(cls)}
    )


def is_union_unknown(cls):
    if get_origin(cls) is not Union:
        return False
    args = list(get_args(cls))
    try:
        args.remove(Unknown)
    except ValueError:
        pass
    try:
        args.remove(type(None))
    except ValueError:
        pass
    return len(args) < 2


def to_union_unknown(converter: BaseConverter, data, cls):
    args = get_args(cls)
    not_unknown = next(
        (value for value in args if value is not Unknown and value is not type(None))
    )
    if data is None:
        return None
    try:
        if not_unknown is datetime and isinstance(data, int):
            data = data / 1000
        return converter.structure(data, not_unknown)
    except ValueError:
        return Unknown(data)


def to_union_dict_str_int(data, cls):
    if isinstance(data, Union[dict, str, int]):
        return data
    raise ValueError()


def register_converter_hooks(converter: BaseConverter):
    converter.register_unstructure_hook_factory(
        is_dataclass, partial(to_pjsekai_camel_unstructure, converter)
    )
    converter.register_structure_hook_factory(
        is_dataclass, partial(to_pjsekai_camel_structure, converter)
    )
    converter.register_structure_hook_func(
        is_union_unknown, partial(to_union_unknown, converter)
    )
    converter.register_structure_hook(Union[dict, str, int], to_union_dict_str_int)


register_converter_hooks(json_converter)
register_converter_hooks(msgpack_converter)
