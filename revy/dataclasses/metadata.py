import dataclasses
from typing import (
    Any,
    Dict,
)


__all__ = (
    'METADATA_NAME',
    'wrap_metadata',
    'unwrap_metadata',
)


METADATA_NAME = 'revy'


def wrap_metadata(
    **kwargs: Any
) -> Dict[str, Any]:
    return {
        METADATA_NAME: kwargs,
    }


def unwrap_metadata(
    field: dataclasses.Field,
) -> Dict[str, Any]:
    metadata = field.metadata.get(METADATA_NAME, dict())
    return metadata
