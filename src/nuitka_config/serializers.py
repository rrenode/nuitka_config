from enum import Enum
from pathlib import Path

def direct_serializer(*, value_transform=None):
    def serializer(value):
        if isinstance(value, Enum):
            value = value.value
        return [f"--{value}"]
    return serializer

def path_serializer(cli_name: str, *, value_transform=None):
    def serializer(value: Path):
        return [value.as_posix()]
    return serializer

def enum_serializer(cli_name: str, *, value_tranform=None):
    def serializer(value: Enum) -> str:
        return [f"--{cli_name}={value.value}"]
    return serializer

def iterable_serializer(cli_name: str, *, value_transform=None):
    def serializer(value) -> list[str]:
        if not value:
            return []
        transform = value_transform or (
            lambda x: x.value if isinstance(x, Enum)
            else x.as_posix() if isinstance(x, Path)
            else x
        )
        return [f"--{cli_name}={transform(v)}" for v in value]
    return serializer

def bool_flag_serializer(cli_name: str, *, value_transform=None):
    def serializer(value) -> str | None:
        if value:
            return [f"--cli_name"]
        return []
    return serializer