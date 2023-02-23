# encoding utf-8
import json
from enum import Enum
from functools import wraps

__all__ = ['Serializable', 'serial_wrapper']
builtin_classes = ['int', 'str', 'float', 'bool']


class Converter:
    @classmethod
    def is_primitive(cls, v) -> bool:
        if v is None:
            return False
        return isinstance(v, int) or isinstance(v, float) or isinstance(v, bool) or isinstance(v, str)

    @classmethod
    def is_primitive_type(cls, t) -> bool:
        return t is None or t is int or t is float or t is bool or t is str

    @classmethod
    def is_valid_field(cls, v) -> bool:
        return cls.is_primitive(v) or isinstance(v, list) \
               or isinstance(v, dict) or isinstance(v, Serializable) \
               or isinstance(v, Enum)

    @classmethod
    def covert_by_type(cls, v, enum_name=True):
        if cls.is_primitive(v):
            return v
        if isinstance(v, list):
            return cls.list_2_json(v)
        if isinstance(v, dict):
            return cls.dict_2_json(v)
        if isinstance(v, Serializable):
            return v.json()
        if isinstance(v, Enum):
            return v.name if enum_name else v.value
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
        if issubclass(t, Serializable):
            return t.from_json(v)
        raise RuntimeError(f'{v} is not supported type: {t}')

    @classmethod
    def list_2_json(cls, li: list, enum_name=True) -> list:
        return [
            cls.covert_by_type(it, enum_name)
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
    def dict_2_json(cls, d: dict, enum_name=True) -> dict:
        return {
            k: cls.covert_by_type(v, enum_name)
            for k, v in d.items()
            if cls.is_valid_field(v)
        }


class Serializable:

    def json(self, enum_name=True) -> dict:
        r"""
        将Serializable转换为json，包含内部所有的元素
        :param enum_name: 枚举类型转换方式，True表示取name，False表示取value
        :return:
        """
        return {
            k: Converter.covert_by_type(v, enum_name)
            for (k, v) in self.__dict__.items()
            if Converter.is_valid_field(v)
        }

    @classmethod
    def from_json(cls, data: dict):
        if not hasattr(cls, '__annotations__'):
            return cls()
        annotations = cls.__annotations__
        instance = cls()
        for (k, t) in annotations.items():
            if k not in data or data[k] is None:
                continue
            value = Converter.deserialize_by_type(data[k], t)
            setattr(instance, k, value)
            pass
        return instance

    def str(self, indent=None, ensure_ascii=False) -> str:
        return json.dumps(self.json(), indent=indent, ensure_ascii=ensure_ascii)


def serial_wrapper(clz, throw: bool = False):
    if not issubclass(clz, Serializable):
        raise RuntimeError(f'{clz} is not subclass of Serializable')

    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                ret = func(*args, **kwargs)
                return clz.from_json(ret)
            except Exception as ex:
                if throw:
                    raise ex
                else:
                    return None

        return wrapper

    return decorate
