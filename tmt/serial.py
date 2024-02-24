# encoding utf-8
import json
import re
from enum import Enum

from typing import Optional, Dict

__all__ = ['Serial']
builtin_classes = ['int', 'str', 'float', 'bool']
union_pattern = re.compile(r'typing\.(Union|Optional)\[.*')
empty_dict = {}


class Converter:
    @classmethod
    def is_primitive(cls, v) -> bool:
        if v is None:
            return False
        return False if v is None else isinstance(v, (int, float, bool, str))

    @classmethod
    def is_primitive_type(cls, t) -> bool:
        return t in (None, int, float, bool, str)

    @classmethod
    def is_valid_field(cls, v) -> bool:
        return cls.is_primitive_type(v) or isinstance(v, (bool, list, dict, Serial, Enum))

    @classmethod
    def covert_by_type(cls, v):
        if cls.is_primitive(v):
            return v
        if isinstance(v, list):
            return cls.list_2_json(v)
        if isinstance(v, dict):
            return cls.dict_2_json(v)
        if isinstance(v, Serial):
            return v.json()
        if isinstance(v, Enum):
            return v.name
        raise RuntimeError(f'can not covert this type: {type(v)}')

    @classmethod
    def deserialize_by_type(cls, v, t):
        if cls.is_primitive_type(t):
            return v
        type_str = str(t)
        if type_str.startswith('typing.List['):
            return cls.json_2_list(v, t)
        if type_str.startswith('typing.Dict['):
            return cls.json_2_dict(v, t)
        if issubclass(t, Serial):
            return t.from_json(v)
        if issubclass(t, Enum):
            return t[v]
        raise RuntimeError(f'{v} is not supported type: {t}')

    @classmethod
    def list_2_json(cls, li: list) -> list:
        return [
            cls.covert_by_type(it)
            for it in li if cls.is_valid_field(li)
        ]

    @classmethod
    def json_2_list(cls, v: list, t) -> list:
        if not isinstance(v, list):
            raise RuntimeError(f'{v} is not instance of typing.List')
        key_type = t.__args__[0]
        return [
            cls.deserialize_by_type(item, key_type)
            for item in v
        ]

    @classmethod
    def json_2_dict(cls, v: dict, t) -> dict:
        if not isinstance(v, dict):
            raise RuntimeError(f'{v} is not instance of typing.Dict')
        key_type = t.__args__[0]
        if key_type is not str:
            raise RuntimeError(f'only str type key is supported')
        value_type = t.__args__[1]
        return {
            key: cls.deserialize_by_type(value, value_type)
            for (key, value) in v.items()
        }

    @classmethod
    def dict_2_json(cls, d: dict) -> dict:
        return {
            k: cls.covert_by_type(v)
            for k, v in d.items()
            if cls.is_valid_field(v)
        }


def merged_annotations(cls: type) -> Optional[dict]:
    if not hasattr(cls, '__annotations__') and not hasattr(cls, '__bases__'):
        return empty_dict
    result = cls.__annotations__ if hasattr(cls, '__annotations__') else dict()
    for base in cls.__bases__:
        result = {**result, **merged_annotations(base)}
    return result


class Serial:

    def json(self) -> dict:
        r"""
        convert Serial to json, includes all elements.
        :return:
        """
        return {
            k: Converter.covert_by_type(v)
            for (k, v) in self.__dict__.items()
            if Converter.is_valid_field(v)
        }

    @classmethod
    def from_json(cls, data: dict):
        annotations = merged_annotations(cls)
        instance = cls()
        if annotations is None or len(annotations) == 0:
            return instance
        key_mapping = instance.name_strategy()
        for (k, t) in annotations.items():
            mapped_key = cls.mapped_key(key_mapping, k)
            if mapped_key not in data or data[mapped_key] is None:
                continue
            value = Converter.deserialize_by_type(data[mapped_key], t)
            setattr(instance, k, value)
        return instance

    @classmethod
    def from_str(cls, json_str: str):
        try:
            payload = json.loads(json_str)
            if isinstance(payload, dict):
                return cls.from_json(payload)
            if isinstance(payload, list):
                return cls.from_list(payload)
            raise RuntimeError(f'Invalid input: {json_str}')
        except TypeError as e:
            raise e
        except json.JSONDecodeError as e:
            raise e

    @classmethod
    def from_list(cls, li: list):
        assert isinstance(li, list), 'The method need a list type parameter'
        return [
            cls.from_json(el)
            for el in li if isinstance(el, dict)
        ]

    @classmethod
    def mapped_key(cls, mapping: Optional[dict], key: str) -> str:
        if mapping is None or key not in mapping.keys():
            return key
        return mapping[key]

    def str(self, indent=None, ensure_ascii=False) -> str:
        return json.dumps(self.json(), indent=indent, ensure_ascii=ensure_ascii)

    def name_strategy(self) -> Optional[Dict[str, str]]:
        r"""
        序列化名称映射，默认情况下为空， 即以
        :return: 字典
        """
        return None
