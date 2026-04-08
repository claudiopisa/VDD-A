from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar
import warnings

type EntryLength = dict[str, int]

# costante di modulo, non verrebbe vista dalle classi figlie
_LENGTH_CACHE_ATTR: str = "_length_cache"

class EntryContractWarning(UserWarning):
    pass

@dataclass(frozen=True)
class Entry(ABC):
    _strict_format: ClassVar[bool] = False

    # the `__init_subclass__` method is a special method in Python that is called automatically whenever a class is subclassed.
    # In this implementation, it is used to enforce that any subclass of Entry defines its own _length_cache class variable, 
    # which is a dictionary that keeps track of the maximum length of each field for all instances of that subclass.
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        
        # use `__dict__` instead of `hasattr` because the former gives only the attributes defined in the actual (sub)class, whereas the latter would also return True for attributes inherited from the base class, 
        # which we don't want becase we need to check whether the subclass has defined its own _length_cache, not just inherited it from Entry. 
        # This way we ensure that every subclass of Entry defines its own _length_cache, which is essential for the correct functioning of the length caching mechanism.
        if _LENGTH_CACHE_ATTR not in cls.__dict__:
            # use `TypeError` instead of `NotImplementedError` because the latter is typically used to indicate that a method or function is not implemented, whereas in this case we want to indicate that 
            # the subclass itself is not properly defined according to the requirements of the Entry base class.
            raise TypeError(f"Subclass {cls.__name__!r} of Entry must define a class variable {_LENGTH_CACHE_ATTR!r} of type {EntryLength.__name__!r}")
        
        # retrueve the attribute from the actual subclass, not from the base class, to check its type and contents
        subclass_length_cache = cls.__dict__[_LENGTH_CACHE_ATTR]

        # check if it's dict type
        if not type(subclass_length_cache) is dict:
            raise TypeError(f"Subclass {cls.__name__!r} of Entry must define {_LENGTH_CACHE_ATTR!r} as a {EntryLength.__name__!r} type, got {type(subclass_length_cache).__name__!r} type instead")
        
        # check if it's not empty, because an empty length cache would not make sense and would likely indicate a mistake in the subclass definition
        if len(subclass_length_cache) == 0:
            raise ValueError(f"Subclass {cls.__name__!r} of Entry must define a non-empty {_LENGTH_CACHE_ATTR!r}")
        
        # check if keys are str and values are int
        for key, value in subclass_length_cache.items():
            if not type(key) is str:
                raise TypeError(f"Keys of {_LENGTH_CACHE_ATTR!r} in subclass {cls.__name__!r} of Entry must be of type str, got {type(key).__name__!r}")
            if not type(value) is int:
                raise TypeError(f"Values of {_LENGTH_CACHE_ATTR!r} in subclass {cls.__name__!r} of Entry must be of type int, got {type(value).__name__!r} for key {key!r}")
            if value < 0:
                raise ValueError(f"Values of {_LENGTH_CACHE_ATTR!r} in subclass {cls.__name__!r} of Entry must be non-negative integers, got {value!r} for key {key!r}")

            expected_format = len(key.upper())
            if value != expected_format:
                msg = (
                    f"{cls.__name__}: _length_cache[{key!r}]={value}, "
                    f"expected {expected_format} (len of field name in uppercase)"
                )
                if cls._strict_format:
                    raise ValueError(msg)
                warnings.warn(msg, EntryContractWarning, stacklevel=2)

        # short version using all() and generator expression, though less informative in error messages
        #if not all(isinstance(k, str) and isinstance(v, int) for k, v in subclass_length_cache.items()):
        #    raise TypeError(f"{cls.__name__}._length_cache must contain only str keys and int values")
        
        

    # Special method called automatically after the dataclass `__init__` method, in order to update
    # the max length of each field in the `_length_cache` dictionary every time a new instance is created.
    def __post_init__(self):
        for key, current_max in type(self)._length_cache.items():
            value = getattr(self, key)
            type(self)._length_cache[key] = max(current_max, len(str(value)))

            #self._length_cache[key] = max(current_max, len(str(getattr(self, key))))
 
    @property
    def length_cache(self) -> dict[str, int]:
        return type(self)._length_cache

    @classmethod
    def reset_length_cache(cls) -> None:
        for key in cls._length_cache.keys():
            cls._length_cache[key] = len(key.upper())

    @classmethod
    def format_row(cls, *values) -> str:
        gap = "  "
        return gap.join(
            f"{key:<{width}}"
            for (key, width), value in zip(cls._length_cache.items(), values)
        )

    @classmethod
    def format_header_row(cls, *values) -> str:
        gap = "  "
        return gap.join(
            f"{value:^{width}}"
            for width, value in zip(cls._length_cache.values(), values)
        )

    def __repr__(self) -> str:
        return type(self).format_row(*(getattr(self, key) for key in type(self)._length_cache))